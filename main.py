#!/bin/python
import mysql.connector as mysqlc
import configparser as cp
import app.video.capture_db_model as video_model


def open_connection(config: cp.ConfigParser):
    cnx = mysqlc.connect(host=config["DEFAULT"].get("mysql_host"), user=config["DEFAULT"].get(
        "mysql_user"), password=config["DEFAULT"].get("mysql_password"))  # type: mysqlc.MySQLConnection
    cnx.database = config["DATA"].get("database_name")
    return cnx


def close_connection(cnx: mysqlc.MySQLConnection):
    cnx.close()


def read_performance_data(config: cp.ConfigParser, performance_id):
    cnx = open_connection(config)
    cursor = cnx.cursor(buffered=True)
    query = ("SELECT * FROM taiko_performances INNER JOIN `taiko_songs` "
             "ON `taiko_performances`.`song`=`taiko_songs`.`id` "
             f"WHERE taiko_performances.`id`={performance_id} LIMIT 1")
    cursor.execute(query)
    (_, name, _, nth, year, month, date, hour, minute, second, _, song, diffi) = cursor.next()
    frame_model = video_model.CaptureModel(config, cnx, (year, month, date, hour, minute, second))
    frame_model.timestamps(wall_clock=True)
    frame_model.timestamps(wall_clock=False)
    # frame_model.frames()
    cursor.close()
    close_connection(cnx)


if __name__ == "__main__":
    config = cp.ConfigParser()
    config.read("config.ini")
    read_performance_data(config, config["DATA"].getint("performance_id"))
