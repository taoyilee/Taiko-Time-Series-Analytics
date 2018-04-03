import mysql.connector as mysqlc
import configparser as cp

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
for result in cursor:
    print(result)

cursor.close()
cnx.close()
