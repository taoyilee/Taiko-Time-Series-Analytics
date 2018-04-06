import mysql.connector as mysqlc
import configparser as cp
import argparse


def open_connection(config: cp.ConfigParser):
    """

    :param config:
    :return: cnx: mysqlc.MySQLConnection
    """
    cnx = mysqlc.connect(host=config["DEFAULT"].get("mysql_host"), user=config["DEFAULT"].get(
        "mysql_user"), password=config["DEFAULT"].get("mysql_password"))  # type: mysqlc.MySQLConnection
    return cnx


def close_connection(cnx: mysqlc.MySQLConnection):
    """

    :param cnx:
    :return:
    """
    cnx.close()


def read_config():
    """
    Read configuration file from config.ini
    :return:
    """
    config = cp.ConfigParser()
    config.read("config.ini")
    return config


def read_args():
    """
    Read command line arguments
    :return: a dictionary of configurations
    """
    parser = argparse.ArgumentParser(description='Taiko data analysis toolkit')
    parser.add_argument('-f', help='Write frames', action='store_true')
    return vars(parser.parse_args())
