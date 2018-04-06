from app.utilities import open_connection, close_connection, read_config
import mysql
import os
config = read_config()
cnx = open_connection(config)
cursor = cnx.cursor(buffered=True)

query = f"USE `bb_capture`"
cursor.execute(query)
query = f"SHOW tables"
cursor.execute(query)
tables = []
for result in cursor:
    if result[0][0:7] == "capture":
        tables.append(result[0])

os.makedirs("sqldumps", exist_ok=True)
for t in tables:
    print(t)
    cmd = f"mysqldump bb_capture -u beaglebone --password=beaglebone --result-file=\"sqldumps/{t}.sql\" \"{t}\""
    print(cmd)
    os.system(cmd)

cursor.close()
close_connection(cnx)
