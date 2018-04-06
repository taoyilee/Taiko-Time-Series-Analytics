#!/bin/python
import mysql.connector as mysqlc
import configparser as cp
import app.video.capture_db_model as video_model
import argparse
from app.sensor.sensor_db_model import SensorModel
import pandas as pd
import matplotlib.pyplot as plt

import os


def open_connection(config: cp.ConfigParser):
    """

    :param config:
    :return: cnx: mysqlc.MySQLConnection
    """
    cnx = mysqlc.connect(host=config["DEFAULT"].get("mysql_host"), user=config["DEFAULT"].get(
        "mysql_user"), password=config["DEFAULT"].get("mysql_password"))  # type: mysqlc.MySQLConnection
    return cnx


def close_connection(cnx: mysqlc.MySQLConnection):
    """

    :param cnx:
    :return:
    """
    cnx.close()


def read_performance_data(cnx, config: cp.ConfigParser, performance_id, write_frames=False):
    """

    :param config:
    :param performance_id:
    :param write_frames:
    :return:
    """
    cnx.database = config["DATA"].get("database_name")
    cursor = cnx.cursor(buffered=True)
    query = ("SELECT * FROM taiko_performances INNER JOIN `taiko_songs` "
             "ON `taiko_performances`.`song`=`taiko_songs`.`id` "
             f"WHERE taiko_performances.`id`={performance_id} LIMIT 1")
    cursor.execute(query)
    (_, name, _, nth, year, month, date, hour, minute, second, _, song, diffi) = cursor.next()
    frame_model = video_model.CaptureModel(config, cnx, (year, month, date, hour, minute, second))
    frame_model.frames() if write_frames else None
    cursor.close()
    return frame_model, name, song, diffi, nth


def read_config():
    """
    Read configuration file from config.ini
    :return:
    """
    config = cp.ConfigParser()
    config.read("config.ini")
    return config


def read_args():
    """
    Read command line arguments
    :return: a dictionary of configurations
    """
    parser = argparse.ArgumentParser(description='Taiko data analysis toolkit')
    parser.add_argument('-f', help='Write frames', action='store_true')
    return vars(parser.parse_args())


if __name__ == "__main__":
    config = read_config()
    args = read_args()
    cnx = open_connection(config)
    performance_ids = config["DATA"].get("performance_id").split(',')
    print(performance_ids)
    for p in performance_ids:
        print(f"Processing performance id {p}")
        frame_model, name, song, diffi, nth = read_performance_data(cnx, config, p, args["f"])
        sensor_data = frame_model.sensor_data()  # type: SensorModel
        left_ax = sensor_data.get_sensor_data_axis(hand="left", axis_name="imu_ax")  # type: pd.Series
        right_ax = sensor_data.get_sensor_data_axis(hand="right", axis_name="imu_ax")  # type: pd.Series
        plt.figure()
        left_ax.plot()
        right_ax.plot()
        plt.legend(["left", "right"])
        file_name = f"{name}_{song}_{diffi}_{nth}"
        plt.title(f"Test Subject#{name} {song}@{diffi} Performance #{nth}", family="IPAPGothic")
        plt.savefig(os.path.join(config["DEFAULT"].get("image_directory"), f"sensor_ax_{file_name}.png"))
    close_connection(cnx)
