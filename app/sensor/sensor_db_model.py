import os
import configparser as cp
import mysql.connector as mysqlc
import mysql.connector.cursor as cursor
import pandas as pd
import datetime
from app.video import image_decode as imgdec
from PIL import Image, ImageDraw
from pytz import timezone
import io


class SensorModel:
    def __init__(self, config: cp.ConfigParser, cnx: mysqlc.Connect, start_time, end_time):
        self.config = config
        self.cnx = cnx  # type: mysqlc.MySQLConnection
        self.start_time = start_time
        self.end_time = end_time
