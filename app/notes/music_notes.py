import mysql.connector
import os
import matplotlib.pyplot as plt
import numpy as np
from app.dbutils import MySQLTaiko


def plot_notes(config, database_handle: MySQLTaiko, song_id, plt_handle: plt, offset=0, height=1,
               base_value=0):
    database_handle.set_database("bb_subjects")
    cur = database_handle.cursor()
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

    timestamps = np.array(timestamps) + offset
    notes = np.array(notes)
    timestamps_mono = np.all(np.diff(timestamps) > 0)
    print(f"Timestamp monotonicity = {timestamps_mono}")
    colors = ['black', 'red', 'blue', 'yellow', 'green', 'cyan', 'purple']
    mapping = {1: "Dong_small", 2: "Ka_small", 3: "Dong_big", 4: "Ka_big", 5: "small_Hit_stream", 6: "big_Hit_steam"}
    legend_names = []
    for t in [1, 2, 3, 4, 5, 6]:
        timestamps_t = timestamps[np.where(notes == t)]
        if len(timestamps_t) > 0:
            legend_names.append(mapping[t])
            l = plt_handle.stem(timestamps_t, height * np.ones_like(timestamps_t), linefmt="C0-", markerfmt="",
                                basefmt="", bottom=base_value)
            plt_handle.setp(l, linewidth=1, color=colors[t])
    cur.close()
    return legend_names
