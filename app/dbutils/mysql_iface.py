import mysql.connector as mysqlc
import configparser as cp


class MySQLTaiko:
    cnx = None  # type: mysqlc.MySQLConnection

    def __init__(self, config: cp.ConfigParser):
        self.config = config

    def open(self):
        self.cnx = mysqlc.connect(host=self.config["DEFAULT"].get("mysql_host"), user=self.config["DEFAULT"].get(
            "mysql_user"), password=self.config["DEFAULT"].get("mysql_password"))  # type: mysqlc.MySQLConnection
        self.cnx.autocommit = True

    def set_database(self, db_name):
        self.cnx.database = db_name

    def cursor(self):
        return self.cnx.cursor()

    def close(self):
        self.cnx.close()
