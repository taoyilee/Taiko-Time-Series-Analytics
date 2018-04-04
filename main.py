#!/bin/python
import mysql.connector as mysqlc
import configparser as cp
import app.video.capture_db_model as video_model
import argparse


def open_connection(config: cp.ConfigParser):
    """

    :param config:
    :return: cnx: mysqlc.MySQLConnection
    """
    cnx = mysqlc.connect(host=config["DEFAULT"].get("mysql_host"), user=config["DEFAULT"].get(
        "mysql_user"), password=config["DEFAULT"].get("mysql_password"))  # type: mysqlc.MySQLConnection
    cnx.database = config["DATA"].get("database_name")
    return cnx


def close_connection(cnx: mysqlc.MySQLConnection):
    """

    :param cnx:
    :return:
    """
    cnx.close()


def read_performance_data(config: cp.ConfigParser, performance_id, write_frames=False):
    """

    :param config:
    :param performance_id:
    :param write_frames:
    :return:
    """
    cnx = open_connection(config)
    cursor = cnx.cursor(buffered=True)
    query = ("SELECT * FROM taiko_performances INNER JOIN `taiko_songs` "
             "ON `taiko_performances`.`song`=`taiko_songs`.`id` "
             f"WHERE taiko_performances.`id`={performance_id} LIMIT 1")
    cursor.execute(query)
    (_, name, _, nth, year, month, date, hour, minute, second, _, song, diffi) = cursor.next()
    frame_model = video_model.CaptureModel(config, cnx, (year, month, date, hour, minute, second))
    (begin, end) = frame_model.timestamps()
    frame_model.frames() if write_frames else None
    cursor.close()
    close_connection(cnx)


if __name__ == "__main__":
    config = cp.ConfigParser()
    config.read("config.ini")

    parser = argparse.ArgumentParser(description='Taiko data analysis toolkit')
    parser.add_argument('-f', help='Write frames', action='store_true')
    args = vars(parser.parse_args())

    read_performance_data(config, config["DATA"].getint("performance_id"), args["f"])
