from app.utilities import open_connection, close_connection,  read_config
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
    query = f"SELECT `image_width`, `image_height` FROM bb_capture.`{t}` LIMIT 1"
    print(query)
    cursor.execute(query)
    (width, height) = cursor.next()

    query = ("INSERT INTO bb_capture.properties (name, width, height) "
             f"VALUES ('{t}', {width}, {height})")
    try:
        cursor.execute(query)
    except mysql.connector.errors.IntegrityError:
        print("**   Duplicate entry found, skipping")

cursor.close()
close_connection(cnx)
