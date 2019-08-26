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

    def add_alert(self, server, user, date, message):
        query = "INSERT INTO alerts ('serverid','userid','date', 'description') VALUES (:serverid,:userid,:date,:message);"
        values = {"serverid": server,"userid": user, "date" : date,"message" : message}
        return self.try_insert_query(query,values)

    def add_alertrole(self, server, role):
        query = "INSERT INTO alertroles ('serverid','role') VALUES (:serverid,:role);"
        values = {"serverid": server,"role": role}
        return self.try_insert_query(query,values)

    def add_checkin(self,server,user,date,message):
        query = "INSERT INTO checkins ('serverid','userid','date', 'description') VALUES (:serverid,:userid,:date,:message);"
        values = {"serverid": server,"userid": user, "date": date, "message": message}
        return self.try_insert_query(query,values)

    def remove_alertrole(self, server, role):
        query = "DELETE FROM alertroles WHERE serverid = :serverid AND role = :role;"
        values = {"serverid": server,"role": role}
        return self.try_insert_query(query,values)

    def get_checkins(self, server):
        query = "SELECT * FROM checkins WHERE serverid = :serverid"
        values = {"serverid": server}
        return self.try_fetch_query(query, values)

    def get_last_checkins(self, server):
        query = "SELECT * FROM checkins WHERE serverid = :serverid ORDER BY date DESC LIMIT 5"
        values = {"serverid": server}
        return self.try_fetch_query(query, values)

    def get_alerts(self,server):
        query = "SELECT * FROM alerts WHERE serverid = :serverid"
        values = {"serverid": server}
        return self.try_fetch_query(query, values)

    def get_alertroles(self, server):
        query = "SELECT * FROM alertroles WHERE serverid = :serverid"
        values = {"serverid": server}
        return self.try_fetch_query(query, values)

    def try_insert_query(self, query, values):
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

    def try_fetch_query(self, query, values):
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
                "CREATE TABLE IF NOT EXISTS alerts (id INTEGER PRIMARY KEY,serverid INTEGER, userid INTEGER, date TEXT NOT NULL, description TEXT);")
            self.cursor.execute(
                "CREATE TABLE IF NOT EXISTS checkins (id INTEGER PRIMARY KEY,serverid INTEGER, userid INTEGER, date TEXT NOT NULL, description TEXT);")
            self.cursor.execute(
                "CREATE TABLE IF NOT EXISTS alertroles (serverid INTEGER, role TEXT, PRIMARY KEY(serverid,role));")
            self.conn.commit()
            self.cursor.execute("SELECT * FROM alerts")
            self.cursor.fetchall()
            self.dbOK = True
        except Exception as e:
            self.dbOK = False
            print("db not ok")
            print(e)

    def __del__(self):
        self.cleanup()