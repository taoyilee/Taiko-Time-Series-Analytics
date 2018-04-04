import os
import configparser as cp
import mysql.connector as mysqlc
from app.video import image_decode as imgdec
from PIL import Image, ImageDraw

import io


class CaptureModel:
    def __init__(self, config: cp.ConfigParser, cnx: mysqlc.Connect, time_stamp):
        self.config = config
        self.cnx = cnx
        self.time_stamp = time_stamp

    def frames(self):
        capture_db = self.config["CAPTURE"].get("database_name")
        (year, month, date, hour, minute, second) = self.time_stamp
        data_table_name = f"capture_{year}_{month:02d}_{date:02d}_{hour:02d}_{minute:02d}_{second:02d}"
        cursor_capture = self.cnx.cursor(buffered=True)
        query = f"SELECT * FROM `{capture_db}`.`{data_table_name}`"
        print(query)
        cursor_capture.execute(query)
        print(f"Query: {capture_db}/{data_table_name} for video captures")
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
