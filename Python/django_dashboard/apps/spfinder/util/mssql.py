import logging
import pyodbc


class Mssql:
    def __init__(self, server, db, user, pwd, driver = '{ODBC Driver 11 for SQL Server}'):
        self.server = server
        self.db = db
        self.user = user
        self.pwd = pwd
        self.driver = driver
        self.logger = logging.getLogger("spfinder") 
    def __GetConnect(self):
        self.conn = pyodbc.connect('DRIVER=%s;SERVER=%s;DATABASE=%s;UID=%s;PWD=%s' % (self.driver, self.server, self.db, self.user, self.pwd))
        cur = self.conn.cursor()
        if not cur:
            raise RuntimeError("Failed to connect to DB: " + self.host + "\\" + self.db)
        else:
            return cur
    def close(self):
        if self.conn.cursor():
            self.conn.cursor().close()
            self.conn.close()
    
    def ExecSPFinderSPFlow(self):
        results = []
        cur = self.__GetConnect()
        try:
            cur.execute(self.dropProcedureFindAllSP())
            cur.execute(self.createProcedureFindAllSP())
            cur.execute(self.executeProcedureFindAllSP())
            #recs=cur.fetchall()
            #for rec in recs:
            #    print(rec)
            columns = [column[0] for column in cur.description]
            for row in cur.fetchall():
                results.append(dict(zip(columns, row)))
        except pyodbc.Error as e:
            self.logger.error(str(e))    
        else:
            self.conn.commit()       
        finally:
            self.close()
        return results
    def executeProcedureFindAllSP(self):
        return '''EXEC findAllSP'''

    def dropProcedureFindAllSP(self):
        return '''
        IF EXISTS (SELECT * FROM sys.objects WHERE type='P' AND name='findAllSP')
         DROP PROCEDURE findAllSP
        '''
    def createProcedureFindAllSP(self):
        return '''
                CREATE PROCEDURE findAllSP AS 
                DECLARE @db_name NVARCHAR(MAX) 
                Set @db_name= NULL
                
                IF OBJECT_ID('tempdb..#allsp') IS NOT NULL DROP TABLE #allsp
                
                CREATE TABLE #allsp (Database_Name NVARCHAR(max),SP_Name NVARCHAR(MAX),Create_Date DATETIME,Modify_date DATETIME)
        
                DECLARE finddb_cur CURSOR FORWARD_ONLY 
                FOR 
                   SELECT distinct name FROM sys.databases
                   WHERE name NOT IN ('master','tempdb','model','msdb')          
        
                OPEN finddb_cur
                FETCH NEXT FROM finddb_cur
                into @db_name
                
                while @@FETCH_STATUS = 0
                Begin
        
        
                    DECLARE @sql NVARCHAR(max)
                    Set @sql = NULL
        
                    SET @sql = 'SELECT \'\'\' + @db_name + \'\'\',name,create_date,modify_date FROM '+@db_name+'.sys.procedures'
        
                      
                    SET NOCOUNT ON  
                    INSERT INTO #allsp
                    (Database_Name, SP_Name ,Create_Date ,Modify_date)
                    EXEC sp_executesql @sql
        
        
                             
                    FETCH NEXT FROM finddb_cur
                    into @db_name
                End
        
            CLOSE finddb_cur;
            DEALLOCATE finddb_cur;
                
            SELECT @@SERVERNAME AS ServerName, * FROM #allsp
            '''