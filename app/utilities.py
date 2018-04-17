import configparser as cp
import argparse


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
