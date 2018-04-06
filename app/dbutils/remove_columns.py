from app.utilities import open_connection, close_connection, read_config
import mysql

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

for t in tables:
    query = (f"ALTER TABLE `{t}` DROP COLUMN image_width, DROP COLUMN image_height, DROP COLUMN wall_time")
    print(query)
    try:
        cursor.execute(query)
    except mysql.connector.errors.ProgrammingError:
        print("**   Column not found, skipping")

cursor.close()
close_connection(cnx)
