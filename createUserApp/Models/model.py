import psycopg2

class Database:
    def __init__(self, host, database, user, password):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.conn = None

    def connect(self):
        self.conn = psycopg2.connect(
            host=self.host,
            database=self.database,
            user=self.user,
            password=self.password
        )

    def disconnect(self):
        if self.conn is not None:
            self.conn.close()

    def get_userid(self, username):
        self.connect()
        cur = self.conn.cursor()
        query = f"SELECT \"Id\" FROM \"AspNetUsers\" a WHERE a.\"UserName\" = '{username}' "
        cur.execute(query)
        user_id = cur.fetchone()
        cur.close()
        self.disconnect()
        return user_id