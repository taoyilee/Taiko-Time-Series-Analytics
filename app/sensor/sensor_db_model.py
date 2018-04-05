import configparser as cp
import mysql.connector as mysqlc
import pandas as pd
from pytz import timezone
import numpy as np


class SensorModel:
    def __init__(self, config: cp.ConfigParser, cnx: mysqlc.Connect, table_name, start_time, end_time):
        self.config = config
        self.cnx = cnx  # type: mysqlc.MySQLConnection
        self.start_time = start_time
        self.end_time = end_time
        self.table_name = {"left": table_name[0], "right": table_name[1]}

    def get_sensor_data_axis(self, hand="left", axis_name="imu_ax"):
        database_name = {"left": self.config["CAPTURE"].get("database_left"),
                         "right": self.config["CAPTURE"].get("database_right")}
        cursor = self.cnx.cursor(buffered=True)  # type: cursor.MySQLCursor
        query = (f"SELECT `timestamp`, `{axis_name}`  FROM `{database_name[hand]}`.`{self.table_name[hand]}` "
                 f"WHERE `timestamp` BETWEEN {self.start_time.timestamp()} "
                 f"AND {self.end_time.timestamp()} ORDER BY `timestamp` ASC")
        print(query)
        cursor.execute(query)
        sensor_data = []
        time_index_timestamp = []
        for (time, result) in cursor:
            time = pd.to_datetime(time, unit='s', utc=True)
            time = time.tz_convert(timezone("Asia/Taipei"))
            time_index_timestamp.append(time)
            sensor_data.append(result)
        time_index = pd.DatetimeIndex(time_index_timestamp)
        time_series = pd.Series(sensor_data, index=time_index)
        cursor.close()
        return time_series
