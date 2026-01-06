import logging
import logging.config
#https://stackoverflow.com/a/15729700/7924573
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
logging.setLevel(logging.DEBUG)

# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

ch.setFormatter(CustomFormatter())



logging.addHandler(ch)