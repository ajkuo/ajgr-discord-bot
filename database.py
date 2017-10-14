import asyncio
import config
import pymysql


class Db:
    def __init__(self):
        self.db_config = {
            'host': config.DB_HOST, 
            'user': config.DB_USER, 
            'passwd': config.DB_PASSWORD, 
            'db': config.DB_NAME, 
            'port': config.DB_PORT,
            'charset': config.DB_CHARSET
        }


    def connect_db(self):
        return pymysql.connect(**self.db_config)

    def get_value(self, table, column, condition='1=1'):
        try:
            conn = self.connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT {} FROM {} WHERE {}".format(column, table, condition))

            return list(cursor)

        except Exception as e:
            print("Error %s", str(e))

        finally:
            conn.close()

    def execute_sql(self, sql):
        try:
            conn = self.connect_db()
            cursor = conn.cursor()
            cursor.execute(sql)
            conn.commit()
            return list(cursor)

        except Exception as e:
            print("Error %s", str(e))

        finally:
            conn.close()
