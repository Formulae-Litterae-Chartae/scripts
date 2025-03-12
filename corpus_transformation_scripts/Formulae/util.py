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
        return getLogger()
    

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
    capitains_rng_file= path.join('.','capitains.rng')
    if not path.isfile(capitains_rng_file):
        raise FileNotFoundError(capitains_rng_file)