import mysql.connector as mysqlc
import configparser as cp
import app.video.capture_db_model as video_model

config = cp.ConfigParser()
config.read("config.ini")
cnx = mysqlc.connect(host=config["DEFAULT"].get("mysql_host"), user=config["DEFAULT"].get(
    "mysql_user"), password=config["DEFAULT"].get("mysql_password"))

cnx.database = "bb_subjects"
cursor = cnx.cursor(buffered=True)
perf_id = config["DATA"].getint("performance_id")
query = ("SELECT * FROM taiko_performances INNER JOIN `taiko_songs` "
         "ON `taiko_performances`.`song`=`taiko_songs`.`id` "
         f"WHERE taiko_performances.`id`={perf_id}")
print(query)
cursor.execute(query)
for (_, name, _, nth, year, month, date, hour, minute, second, _, song, diffi) in cursor:
    frame_model = video_model.CaptureModel(config, cnx, (year, month, date, hour, minute, second))
    frame_model.frames()

cursor.close()
cnx.close()
