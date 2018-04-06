import os
import configparser as cp
import mysql.connector as mysqlc
import mysql.connector.cursor as cursor
import pandas as pd
import datetime
from app.video import image_decode as imgdec
from PIL import Image, ImageDraw
from pytz import timezone
import io
from app.sensor.sensor_db_model import SensorModel
from app.video.timestamped_frame import TimestampedFrame
from app.video.timestamped_frame_series import TimestampedFrameSeries


class CaptureModel:
    verbosity = 0

    def __init__(self, config: cp.ConfigParser, cnx: mysqlc.Connect, time_stamp):
        self.config = config
        self.cnx = cnx  # type: mysqlc.MySQLConnection
        self.time_stamp = time_stamp
        self.capture_db = self.config["CAPTURE"].get("database_name")
        (year, month, date, hour, minute, second) = self.time_stamp
        self.data_table_name = f"capture_{year}_{month:02d}_{date:02d}_{hour:02d}_{minute:02d}_{second:02d}"
        self.verbosity = config["DEFAULT"].getint("verbosity")

    def timestamps(self, wall_clock=False):
        cursor_capture = self.cnx.cursor(buffered=True)  # type: cursor.MySQLCursor
        column = "wall_time" if wall_clock else "timestamp"
        query = (f"SELECT `{column}`  FROM `{self.capture_db}`.`{self.data_table_name}` "
                 "ORDER BY `timestamp` ASC LIMIT 1")
        cursor_capture.execute(query)
        begin = cursor_capture.next()[0]
        query = (f"SELECT `{column}`  FROM `{self.capture_db}`.`{self.data_table_name}` "
                 "ORDER BY `timestamp` DESC LIMIT 1")
        cursor_capture.execute(query)
        end = cursor_capture.next()[0]
        cursor_capture.close()
        if wall_clock:
            begin = pd.to_datetime(begin, format="%Y-%m-%d_%H%M%S")
            end = pd.to_datetime(end, format="%Y-%m-%d_%H%M%S")
            begin = begin.tz_localize(timezone("Asia/Taipei"))
            end = end.tz_localize(timezone("Asia/Taipei"))
        else:
            begin = pd.to_datetime(begin, unit='s', utc=True)
            end = pd.to_datetime(end, unit='s', utc=True)
            begin = begin.tz_convert(timezone("Asia/Taipei"))
            end = end.tz_convert(timezone("Asia/Taipei"))
        print(f"{begin} - {end}") if self.verbosity > 0 else None

        return begin, end

    def sensor_data(self):
        (left_table, right_table) = self.find_table()
        (begin_time, end_time) = self.timestamps()
        return SensorModel(self.config, self.cnx, (left_table, right_table), begin_time, end_time)

    def sensor_data_table(self, hand="left"):
        database_name = {"left": self.config["CAPTURE"].get("database_left"),
                         "right": self.config["CAPTURE"].get("database_right")}

        cursor = self.cnx.cursor(buffered=True)  # type: cursor.MySQLCursor
        query = f"USE `{database_name[hand]}`"
        print(query) if self.verbosity > 0 else None
        cursor.execute(query)
        query = f"SHOW tables"
        print(query) if self.verbosity > 0 else None
        cursor.execute(query)
        tables = []
        for result in cursor:
            tables.append(result[0])
        cursor.execute(query)
        cursor.close()
        if not tables:
            raise ValueError(f"No appropriate sensor data table for corresponding video frames")
        return tables

    def find_table(self):
        return self.find_table_hand(hand="left"), self.find_table_hand(hand="right")

    def find_table_hand(self, hand="left"):
        (begin, end) = self.timestamps()
        tables = self.sensor_data_table(hand=hand)
        for i, t in enumerate(tables):
            table_time = pd.to_datetime(t[5:], format="%Y_%m_%d_%H_%M_%S")
            table_time = table_time.tz_localize(timezone("Asia/Taipei"))
            t_delta_begin = table_time - begin
            t_delta_end = table_time - end
            index = (t_delta_begin > pd.Timedelta(0)) and (t_delta_end > pd.Timedelta(0))
            if index:
                return tables[i - 1]

    def frames(self):
        cursor_capture = self.cnx.cursor(buffered=True)  # type: cursor.MySQLCursor
        query = f"SELECT * FROM `{self.capture_db}`.`{self.data_table_name}`"
        print(query) if self.verbosity > 0 else None
        cursor_capture.execute(query)
        print(f"Query: {self.capture_db}/{self.data_table_name} for video captures") if self.verbosity > 0 else None
        timestamp0 = 1e10
        frames = TimestampedFrameSeries()
        for (_, timestamp, _, width, height, img_base64) in cursor_capture:
            if timestamp < timestamp0:
                timestamp0 = timestamp
            t = timestamp - timestamp0
            print(f"{t:.4f} {width}X{height} px") if self.verbosity > 0 else None
            img_bytes = imgdec.decode(img_base64)
            current_frame = Image.open(io.BytesIO(img_bytes))  # type: Image.Image
            (b, g, r) = current_frame.split()
            current_frame = Image.merge("RGB", (r, g, b))
            image_draw = ImageDraw.Draw(current_frame)  # type: ImageDraw.Draw
            image_draw.text((0, 0), f"{t:.4f}", (255, 0, 0))
            frames.append(TimestampedFrame(current_frame, timestamp))
        cursor_capture.close()
        return frames
