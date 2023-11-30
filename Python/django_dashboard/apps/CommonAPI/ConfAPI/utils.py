import pyodbc
from datetime import datetime, timedelta

conn_string = 'Driver={SQL Server};Server=qabosdbag.awsnp.gdotawsnp.com;' \
                      'Database=GBOS;uid=qa_automation;pwd=G33Nff4%$^;'

class ProductDB():    
    def dbQuery(self, query):
        data = []
        SQL_ATTR_CONNECTION_TIMEOUT = 113
        login_timeout = 60
        connection_timeout = 180
        with pyodbc.connect(conn_string, timeout=login_timeout,
                            attrs_before={SQL_ATTR_CONNECTION_TIMEOUT: connection_timeout}) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
            for row in rows:
                data.append({columns[i]: row[i] for i in range(len(columns))})
        return data