import pyodbc
from datetime import datetime, timedelta

conn_string = 'Driver={ODBC Driver 17 for SQL Server};Server=GDCQAAUTOSQL201;' \
                      'Database=LicenseServer;uid=qa_automation;pwd=Gr33nDot!;'
                      
class LicenseDB():    
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