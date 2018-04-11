#!/bin/python
import app.video.capture_db_model as video_model
from app.sensor.sensor_db_model import SensorModel
from app.utilities import open_connection, close_connection, read_args, read_config
import configparser as cp
import os
import argparse
import pandas as pd

if __name__ == "__main__":
    config = read_config()
    parser = argparse.ArgumentParser(description='Taiko data analysis toolkit')
    parser.add_argument('-f', help='Excel table for music notes')
    parser.add_argument('-i', help='Corresponding music id')
    args = vars(parser.parse_args())
    cnx = open_connection(config)
    data_table_name = args["f"]
    song_id = args["i"]
    cnx.database = "bb_subjects"
    cursor = cnx.cursor(buffered=True)
    query = f"SELECT `song` FROM `taiko_songs` WHERE `id`={song_id} LIMIT 1"
    cursor.execute(query)
    song_name = cursor.next()[0]
    print(f"Readning file {data_table_name} for song {song_name}")
    table = pd.read_excel(data_table_name, header=1)
    mapping = {1: "Dong_small", 2: "Ka_small", 3: "Dong_big", 4: "Ka_big", 5: "small_Hit_stream", 6: "big_Hit_steam"}

    time_stamp = 0.0
    for seq, row in table.iterrows():
        label = int(row["label"])
        bpm = row["BPM"]
        continuous = "TRUE" if row["continuous"] == 1 else "FALSE"
        query = (f"INSERT INTO `taiko_notes` (`id`, `type`, `bpm`, `sequence`, `continuous`, `timestamp`) "
                 f"VALUES ({song_id}, {label},  {bpm:f}, {seq:d}, {continuous}, {time_stamp})")
        cursor.execute(query)
        time_stamp += (60.0 / bpm) / 2
    cursor.close()
    close_connection(cnx)
