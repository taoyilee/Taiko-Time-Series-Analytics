import mysql.connector as mysqlc
import configparser as cp
from app import image_decode as imgdec
from PIL import Image, ImageDraw
import io
import os

config = cp.ConfigParser()
config.read("config.ini")
cnx = mysqlc.connect(host=config["DEFAULT"].get("mysql_host"), user=config["DEFAULT"].get(
    "mysql_user"), password=config["DEFAULT"].get("mysql_password"))

cnx.database = "bb_subjects"
cursor = cnx.cursor(buffered=True)
perf_id = config["DATA"].getint("performance_id")
query = f"SELECT * FROM taiko_performances INNER JOIN `taiko_songs` ON taiko_performances.song=taiko_songs.id WHERE taiko_performances.`id`={perf_id}"
print(query)
cursor.execute(query)
for (_, name, _, nth, year, month, date, hour, minute, second, _, song, diffi) in cursor:
    capture_db = config["CAPTURE"].get("database_name")
    data_table_name = f"capture_{year}_{month:02d}_{date:02d}_{hour:02d}_{minute:02d}_{second:02d}"
    cursor_capture = cnx.cursor(buffered=True)
    query = f"SELECT * FROM `{capture_db}`.`{data_table_name}`"
    print(query)
    cursor_capture.execute(query)
    print(f"Query: {capture_db}/{data_table_name} for video captures")
    image_dir = config["DEFAULT"].get("image_directory")
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

cursor.close()
cnx.close()
