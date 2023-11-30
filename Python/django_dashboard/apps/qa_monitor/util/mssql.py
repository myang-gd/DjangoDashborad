import logging
import pyodbc

class Mssql:
    def __init__(self, server, db, user, pwd, driver = '{SQL Server}'):
        self.server = server
        self.db = db
        self.user = user
        self.pwd = pwd
        self.driver = driver
        self.logger = logging.getLogger("MSSQL") 
    def __GetConnect(self):
        try:
            self.conn = pyodbc.connect('DRIVER=%s;SERVER=%s;DATABASE=%s;UID=%s;PWD=%s' % (self.driver, self.server, self.db, self.user, self.pwd))
            cur = self.conn.cursor()
        except:
            raise RuntimeError("Failed to connect to DB: " + self.server + "\\" + self.db)
        else:    
            return cur
    def close(self):
        if self.conn.cursor():
            self.conn.cursor().close()
            self.conn.close()
    
    def ExecQuery(self,sql):
        results = []
        cur = self.__GetConnect()
        try:
            cur.execute(sql)
            columns = [column[0] for column in cur.description]
            for row in cur.fetchall():
                results.append(dict(zip(columns, row)))
        except pyodbc.Error as e:
            self.logger.error(str(e))            
        finally:
            self.close()
            return results

    def ExecNonQuery(self,sql):
        cur = self.__GetConnect()
        try:
            cur.execute(sql)
        except pyodbc.Error as e:
            self.logger.error(str(e))    
        else:
            self.conn.commit()       
        finally:
            self.close()