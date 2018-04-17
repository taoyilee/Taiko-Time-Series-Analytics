#!/bin/python

from app.performance import Performance
import app.dbutils as dbutils
from app.utilities import read_args, read_config

if __name__ == "__main__":
    config = read_config()
    args = read_args()
    db_handle = dbutils.MySQLTaiko(config)
    db_handle.open()
    performance_ids = config["DATA"].get("performance_id").split(',')

    for p in performance_ids:
        print(f"Processing performance id {p}")
        performance = Performance(p, db_handle, config)
        performance.write_video()

    db_handle.close()
