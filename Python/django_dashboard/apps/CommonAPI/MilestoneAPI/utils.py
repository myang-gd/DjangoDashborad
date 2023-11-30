import pyodbc
from datetime import datetime, timedelta

conn_string = 'Driver={SQL Server Native Client 11.0};Server=GDCQAAUTOSQL201;' \
                      'Database=automation;uid=qa_automation;pwd=Gr33nDot!;'

class MilestoneUtils():    
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
    
    def dbInsert(self, query):
        SQL_ATTR_CONNECTION_TIMEOUT = 113
        login_timeout = 60
        connection_timeout = 180
        with pyodbc.connect(conn_string, timeout=login_timeout,
                            attrs_before={SQL_ATTR_CONNECTION_TIMEOUT: connection_timeout}) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            conn.commit()
    
    def dateTimeParser(self, date_Time_Str = None):
        if date_Time_Str is None:
            date_Time_Str = datetime.strftime(datetime.now(), '%Y-%m-%d 00:00:00')
        return datetime.strptime("".join(date_Time_Str), '%Y-%m-%d 00:00:00')
    
    def dateTimeFormater(self, date_Time_Utc = None):
        if date_Time_Utc is None:
            date_Time_Utc = datetime.now()
            if date_Time_Utc.microsecond % 1000 >= 500:  # check if there will be rounding up
                date_Time_Utc = date_Time_Utc + timedelta(milliseconds=1)  # manually round up
        return date_Time_Utc.strftime('%Y-%m-%d 00:00:00.000')