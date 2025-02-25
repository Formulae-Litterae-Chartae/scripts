from os import path
from logging import getLogger
from logging.config import fileConfig

def make_proper_path(str_path:str):
    return path.expanduser(path.normpath(str_path))

def get_logger():
    try:
        fileConfig(path.abspath(path.join('..','..','logging.conf')))
    except KeyError:
        try:
            fileConfig(path.abspath(path.join('logging.conf')))
        except KeyError:
            pass
    finally:
        return getLogger()