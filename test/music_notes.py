#!/bin/python
import app.video.capture_db_model as video_model
from app.sensor.sensor_db_model import SensorModel
from app.sensor.sensor_data import SensorData

from app.utilities import open_connection, close_connection, read_args, read_config
import configparser as cp
import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

if __name__ == "__main__":
    config = read_config()
    args = read_args()
    cnx = open_connection(config)
    performance_ids = config["DATA"].get("performance_id").split(',')
    cnx.database = "bb_subjects"
    for p in performance_ids:
        query = ("SELECT `taiko_performances`.`song`, `taiko_songs`.`song`"
                 " FROM `taiko_performances` LEFT JOIN `taiko_songs`"
                 " ON `taiko_performances`.`song`=`taiko_songs`.`id`"
                 f" WHERE `taiko_performances`.`id`={p}")
        cur = cnx.cursor()
        song_name = cur.execute(query)
        song_id, song_name = cur.next()
        print(f"Reading performance #{p} - {song_name}({song_id})")

        query = ("SELECT `timestamp`, `type`, `bpm`"
                 " FROM `taiko_notes` "
                 f"WHERE `id`={song_id} ORDER BY `sequence` ASC")
        cur.execute(query)
        timestamps = []
        notes = []
        for note in cur:
            timestamp, note_type, bpm = note
            timestamps.append(timestamp)
            notes.append(note_type)

        timestamps = np.array(timestamps)
        notes = np.array(notes)
        timestamps_mono = np.all(np.diff(timestamps) > 0)
        print(f"Timestamp monotonicity = {timestamps_mono}")
        plt.figure(figsize=(12, 6))
        colors = ['red', 'blue', 'yellow', 'green', 'black', 'purple']
        for t in range(6):
            timestamps_t = timestamps[np.where(notes == t)]
            if len(timestamps_t) > 0:
                l = plt.stem(timestamps_t, np.ones_like(timestamps_t), linefmt="C0-", markerfmt="", basefmt="")
                plt.setp(l, linewidth=1, color=colors[t])
        plt.grid()
        output_filename = os.path.join(config["DEFAULT"].get('image_directory'), f"ideal_note_{song_id}.png")
        print(f"Saving file to {output_filename}")
        plt.savefig(output_filename)
        plt.close('all')
        cur.close()
    close_connection(cnx)
