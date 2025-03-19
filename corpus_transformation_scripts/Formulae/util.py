from os import path
from logging import Logger
from logging import getLogger
from logging.config import fileConfig
import subprocess
from subprocess import CompletedProcess

def make_proper_path(str_path:str):
    return path.expanduser(path.normpath(str_path))

def get_logger() -> Logger:
    """
    Uniforms the way logging should be handled in all files in this repository. 
    It returns the already configured logger.

    """
    try:
        fileConfig(path.abspath(path.join('..','..','logging.conf')))
    except KeyError:
        try:
            fileConfig(path.abspath(path.join('logging.conf')))
        except KeyError:
            pass
    finally:
        logger = getLogger()
        logger.setLevel(logging.DEBUG)

        # create console handler with a higher log level
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        ch.setFormatter(CustomFormatter())

        logger.addHandler(ch)


        return logger
    

def subprocess_run(commands:list, logger:Logger) -> CompletedProcess:
    """
    Wrapping method for all subproces.run calls
    To standardize the error handling behavior.
    For more information about the available flags: https://www.saxonica.com/documentation9.5/using-xsl/commandline.html
    """
    xml_file_path = commands[3].replace('-s:','')
    if not path.isfile(xml_file_path):
        logger.warning(xml_file_path+' does not exist!')

    try:
        completed_process = subprocess.run(commands, check=True, stdout=subprocess.PIPE)
        logger.debug(str(commands))
        return completed_process
    except Exception as e:
        logger.warning(' '.join(commands)+' failed')
        try:
            # -t flag to get more detailed information why the process failes
            commands.append('-t')
            completed_process = subprocess.run(commands, check=True, stdout=subprocess.PIPE)
            return completed_process
        except Exception as e:
            if '' in commands:
                logger.warning('The list of commands contains empty commands.')
            logger.error('The following subprocess command raised an exception. Try running it directly in the terminal for more detailed information.')
            logger.error(' '.join(commands))
            raise e
        
def convert_docx_to_tei(input_docx_path:str):
    raise NotImplementedError

def check_capitains_rng():
    """
    Checks the existance of capitains.rng
    """
    capitains_rng_file= path.join('.','capitains.rng')
    if not path.isfile(capitains_rng_file):
        raise FileNotFoundError(capitains_rng_file)
    
import logging

class CustomFormatter(logging.Formatter):
    # source: https://stackoverflow.com/a/56944256/7924573

    grey = "\x1b[0;37m"
    green = "\x1b[1;32m"
    yellow = "\x1b[1;33m"
    red = "\x1b[1;31m"
    purple = "\x1b[1;35m"
    blue = "\x1b[1;34m"
    light_blue = "\x1b[1;36m"
    reset = "\x1b[0m"
    blink_red = "\x1b[5m\x1b[1;31m"


    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    #format="%(asctime)s %(levelname)s %(filename)s:%(lineno)s - %(message)s"

    format="%(asctime)s %(levelname)s %(filename)s:%(lineno)s - %(message)s"
    encoding="utf-8"
    datefmt="%H:%M:%S"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: green + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt='%H:%M:%S')
        return formatter.format(record)