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


class CaptureModel:
    def __init__(self, config: cp.ConfigParser, cnx: mysqlc.Connect, time_stamp):
        self.config = config
        self.cnx = cnx  # type: mysqlc.MySQLConnection
        self.time_stamp = time_stamp
        self.capture_db = self.config["CAPTURE"].get("database_name")
        (year, month, date, hour, minute, second) = self.time_stamp
        self.data_table_name = f"capture_{year}_{month:02d}_{date:02d}_{hour:02d}_{minute:02d}_{second:02d}"

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
        print(f"{begin} - {end}")

        return begin, end

    def frames(self):
        cursor_capture = self.cnx.cursor(buffered=True)  # type: cursor.MySQLCursor
        query = f"SELECT * FROM `{self.capture_db}`.`{self.data_table_name}`"
        print(query)
        cursor_capture.execute(query)
        print(f"Query: {self.capture_db}/{self.data_table_name} for video captures")
        image_dir = self.config["DEFAULT"].get("image_directory")
        os.makedirs(image_dir, exist_ok=True)
        i = 0
        timestamp0 = 1e10
        for (_, timestamp, _, width, height, img_base64) in cursor_capture:
            if timestamp < timestamp0:
                timestamp0 = timestamp
            t = timestamp - timestamp0
            print(f"{t:.4f} {width}X{height} px")
            img_bytes = imgdec.decode(img_base64)
            image = Image.open(io.BytesIO(img_bytes))  # type: Image.Image
            (b, g, r) = image.split()
            image = Image.merge("RGB", (r, g, b))
            image_draw = ImageDraw.Draw(image)  # type: ImageDraw.Draw
            image_draw.text((0, 0), f"{t:.4f}", (255, 0, 0))
            image.save(os.path.join(image_dir, f"capture_{i:03d}.png"))
            i += 1
        cursor_capture.close()
