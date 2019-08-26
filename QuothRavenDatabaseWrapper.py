import sqlite3

class queryResult:
    queryStatus = None
    resultSet = None

    def __init__(self,queryStatus = True, resultSet = []):
        self.queryStatus = queryStatus
        self.resultSet = resultSet


class QuothRavenDatabaseClient():
    conn = None
    cursor = None
    dbOK = None

    def cleanup(self):
        self.conn.close()

    def add_alert(self,user,date,message):
        query = "INSERT INTO alerts ('userid','date', 'description') VALUES (:user,:date,:message);"
        values = {"user": user, "date" : date,"message" : message}
        return self.tryInsertQuery(query,values)

    def add_checkin(self,user,date,message):
        query = "INSERT INTO checkins ('userid','date', 'description') VALUES (:user,:date,:message);"
        values = {"user": user, "date": date, "message": message}
        return self.tryInsertQuery(query,values)

    def get_checkins(self):
        query = "SELECT * FROM checkins"
        values = {}
        return self.tryFetchQuery(query, values)

    def get_checkins(self):
        query = "SELECT * FROM checkins"
        values = {}
        return self.tryFetchQuery(query, values)

    def get_last_checkins(self):
        query = "SELECT * FROM checkins ORDER BY date DESC LIMIT 5"
        values = {}
        return self.tryFetchQuery(query, values)

    def get_alerts(self):
        query = "SELECT * FROM alerts"
        values = {}
        return self.tryFetchQuery(query, values)



    def tryInsertQuery(self,query,values):
        status = None
        result = None
        try:
            self.cursor.execute(query,values)
            self.conn.commit()
            status = True
        except Exception as e:
            print("query failed")
            print(e)
            status = False
        return queryResult(status,[])

    def tryFetchQuery(self,query,values):
        status = None
        result = None
        try:
            self.cursor.execute(query,values)
            result = self.cursor.fetchall()
            status = True
        except Exception as e:
            print("query failed")
            print(e)
            status = False
        return queryResult(status,result)

    def __init__(self,dbName = 'QuothRaven.db'):
        self.conn = sqlite3.connect(dbName)
        self.cursor = self.conn.cursor()
        try:
            self.cursor.execute(
                "CREATE TABLE IF NOT EXISTS alerts (id INTEGER PRIMARY KEY, userid INTEGER, date TEXT NOT NULL, description TEXT);")
            self.cursor.execute(
                "CREATE TABLE IF NOT EXISTS checkins (id INTEGER PRIMARY KEY, userid INTEGER, date TEXT NOT NULL, description TEXT);")
            self.conn.commit()
            self.cursor.execute("SELECT * FROM alerts")
            self.cursor.fetchall()
            self.dbOK = True
        except Exception as e:
            self.dbOK = False
            print("db not ok")
            print(e)