#!/bin/python
import app.video.capture_db_model as video_model
from app.sensor.sensor_db_model import SensorModel
from app.utilities import open_connection, close_connection, read_args, read_config
import configparser as cp
import os


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
    if write_frames:
        frames = frame_model.frames()
        frames.write(config["DEFAULT"].get("image_directory"))
    cursor.close()
    return frame_model, name, song, diffi, nth


if __name__ == "__main__":
    config = read_config()
    args = read_args()
    cnx = open_connection(config)
    performance_ids = config["DATA"].get("performance_id").split(',')

    for p in performance_ids:
        print(f"Processing performance id {p}")
        frame_model, name, song, diffi, nth = read_performance_data(cnx, config, p, args["f"])
        sensor_data = frame_model.sensor_data()  # type: SensorModel
        file_name = os.path.join(config["DEFAULT"].get("image_directory"), f"{name}_{song}_{diffi}_{nth}")
        title = f"Test Subject#{name} {song}@{diffi} Performance #{nth}"
        sensor_data.plot_sensor_data(hand="all", axis_name="imu_ax", title=title, filename=file_name)
        sensor_data.plot_sensor_data(hand="all", axis_name="imu_ay", title=title, filename=file_name)
        sensor_data.plot_sensor_data(hand="all", axis_name="imu_az", title=title, filename=file_name)

    close_connection(cnx)
