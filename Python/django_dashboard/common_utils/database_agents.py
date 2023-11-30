import binascii
import re
import sys
from binascii import hexlify

import pyodbc
from apps.query_view.models import Database
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider


class DatabaseAgents:

    def __init__(self, name):
        obj = Database.objects.get(id=name)
        type_obj = obj._meta.get_field('type')
        self.db_type = type_obj.value_from_object(obj)

        server_obj = obj._meta.get_field('server')
        self.db_server = server_obj.value_from_object(obj)

        db_obj = obj._meta.get_field('database')
        self.db_database = db_obj.value_from_object(obj)

        user_obj = obj._meta.get_field('username')
        db_user = user_obj.value_from_object(obj)

        pwd_obj = obj._meta.get_field('password')
        db_pwd = pwd_obj.value_from_object(obj)

        props_obj = obj._meta.get_field('conn_properties')
        db_props = props_obj.value_from_object(obj)

        if self.db_type is not None and self.db_type.upper() == 'MSSQL':
            conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + self.db_server.replace(':', ',') + ';DATABASE=' + self.db_database + ';'

            if db_user is not None and db_user != '' and db_pwd is not None and db_pwd != '':
                conn_str += 'UID=' + db_user + ';PWD=' + db_pwd + ';'

            if db_props is not None and db_props != '':
                conn_str += db_props
            self.db = pyodbc.connect(conn_str)
        elif self.db_type is not None and self.db_type.upper() == 'CASSANDRA':
            db_server_arr = self.db_server.split(':')
            contact_points = [db_server_arr[0]]
            auth_provider = None
            ports = 9042

            if len(db_server_arr) == 2 and int(db_server_arr[1]) != 9042:
                ports = db_server_arr[1]

            if db_user is not None and db_user != '' and db_pwd is not None and db_pwd != '':
                auth_provider = PlainTextAuthProvider(username=db_user, password=db_pwd)

            cluster = Cluster(contact_points=contact_points, auth_provider=auth_provider, port=ports)
            self.db = cluster.connect(self.db_database)

    # external limitation for mssql
    def limit_sql(self, sql, limit=-1):
        lmt_sql = sql
        if limit > 0:
            matched = re.match(".*( top ).*", sql, re.IGNORECASE)
            if not matched:
                index = sql.lower().find('distinct ')
                if index != -1:
                    index = sql.lower().find('distinct ') + len('distinct ') - 1
                    lmt_sql = sql[:index] + ' TOP ' + str(limit) + ' ' + sql[index:]
                else:
                    if sql.lower().find('select ') != -1:
                        index = sql.lower().find('select ') + len('select ') - 1
                        lmt_sql = sql[:index] + ' TOP ' + str(limit) + ' ' + sql[index:]
                    else:
                        if sql.lower().find('select\n') != -1:
                            index = sql.lower().find('select\n') + len('select\n') - 1
                            lmt_sql = sql[:index] + ' TOP ' + str(limit) + ' ' + sql[index:]

        matched = re.match(".*(SET NOCOUNT ON;).*", lmt_sql, re.IGNORECASE)
        if not matched:
            lmt_sql = 'SET NOCOUNT ON; ' + lmt_sql

        print(lmt_sql)
        return lmt_sql

    def execute(self, sql, limit=-1):
        result = []
        try:
            if not self.validate(sql):
                print('validate query failed')
                raise Exception("Not allow delete/update operation: " + sql)

            if self.db_type is not None and self.db_type.upper() == 'MSSQL':
                cursor = self.db.cursor()
                cursor.execute(self.limit_sql(sql, limit))
                columns = [column[0].lower() for column in cursor.description]
                for row in cursor.fetchall():
                    result.append(dict(zip(columns, [self.fmt_value(itm) for itm in row])))
                cursor.close()
            elif self.db_type is not None and self.db_type.upper() == 'CASSANDRA':
                cursor = self.db.execute(sql)
                columns = cursor.column_names
                for row in cursor.current_rows:
                    values = []
                    for value in row:
                        values.append(str(value))
                    result.append(dict(zip(columns, [self.fmt_value(itm) for itm in values])))
                self.db.shutdown()
        except Exception as e:
            raise e
        finally:
            if self.db_type is not None and self.db_type.upper() == 'MSSQL':
                self.db.close()
            elif self.db_type is not None and self.db_type.upper() == 'CASSANDRA':
                if self.db is not None and not self.db.is_shutdown:
                    self.db.shutdown()
        return result

    def execute_commit(self, sql):
        try:
            if self.db_type is not None and self.db_type.upper() == 'MSSQL':
                cursor = self.db.cursor()
                cursor.execute(sql)
                cursor.commit()
        except Exception as e:
            raise e
        finally:
            if self.db_type is not None and self.db_type.upper() == 'MSSQL':
                self.db.close()

    def fmt_value(self, value):
        if isinstance(value, (bytes, bytearray)):
            if sys.version_info < (3, 5, 0):
                return '0x' + str(binascii.hexlify(value).decode("ascii"))
            else:
                return '0x' + str(value.hex())
        else:
            return str(value)

    @staticmethod
    def database(name):
        return DatabaseAgents(name=name)

    # Just deal with simple sql and not restricted
    @staticmethod
    def validate(sql):
        idx_delete = sql.lower().find('delete ')
        idx_update = sql.lower().find('update ')
        idx_select = sql.lower().find('select ')

        if idx_select != -1 and (idx_select < idx_delete or idx_select < idx_update):
            raise  Exception('Does not support queries that mixed with select, update or delete action.')
        return bool(idx_delete == -1 and idx_update == -1)

    @staticmethod
    def is_update(sql):
        idx_update = sql.lower().find('update ')
        all_update = [m.start() for m in re.finditer('update ', sql.lower())]
        if len(all_update) > 1:
            raise Exception('Does not support multiple update statement.')
        return bool(idx_update != -1)

    @staticmethod
    def is_delete(sql):
        idx_delete = sql.lower().find('delete ')
        all_delete =  [m.start() for m in re.finditer('delete ', sql.lower())]
        if len(all_delete) > 1:
            raise Exception('Does not support multiple delete statement.')
        return bool(idx_delete != -1)

    @staticmethod
    def is_insert(sql):
        idx_insert = sql.lower().find('insert ')
        return bool(idx_insert != -1)

    @staticmethod
    def validate_update_delete_query(db_id, sql):
        default_affect_info = {'affect_row': 999, 'with_where': False,
                               'is_allow': False, 'success': True, 'error': ''}
        if sql != '':
            try:
                db = DatabaseAgents.database(db_id)
                if DatabaseAgents.is_delete(sql):
                    index_from = sql.lower().find('from ')
                    index_where = sql.lower().find('where ')
                    if index_where != -1:
                        default_affect_info['with_where'] = True
                        if index_from != -1:
                            count_sql = 'select count(1) row_ct ' + sql[index_from:]
                            print(count_sql)
                            default_affect_info['affect_row'] = db.execute(count_sql)[0]['row_ct']
                    else:
                        default_affect_info['with_where'] = False
                elif DatabaseAgents.is_update(sql):
                    index_update = sql.lower().find('update ')
                    index_set = sql.lower().find('set ')
                    index_from = sql.lower().find('from ')
                    index_where = sql.lower().find('where')
                    if index_where != -1:
                        default_affect_info['with_where'] = True
                        if index_where < index_from:
                            count_sql = 'select count(1) row_ct from' \
                                        + sql[index_update + 6:index_set] + sql[index_where:]
                            default_affect_info['affect_row'] = db.execute(count_sql)[0]['row_ct']
                            print(default_affect_info)
                        elif index_from != -1:
                            count_sql = 'select count(1) row_ct ' + sql[index_from:]
                            default_affect_info['affect_row'] = db.execute(count_sql)[0]['row_ct']
                            print(default_affect_info)
                        else:
                            count_sql = 'select count(1) row_ct from' \
                                        + sql[index_update + 6:index_set] + sql[index_where:]
                            default_affect_info['affect_row'] = db.execute(count_sql)[0]['row_ct']
                    else:
                        default_affect_info['with_where'] = False

            except Exception as e:
                default_affect_info['success'] = False
                default_affect_info['error'] = str(e)
        return default_affect_info
