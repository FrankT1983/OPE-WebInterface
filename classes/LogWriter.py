import logging
import platform
from logging.handlers import RotatingFileHandler

class LogWriter:
    paht = ""
    if (platform.system() == 'Windows') :
        path = 'C:/PHD/Git/omero-parallel-processing/Django/logs.txt'
    else :
        path= '/home/omero/OMERO.server/Plugins/OPP/OPP/logs.txt'

    log_handler = RotatingFileHandler(path, maxBytes=1048576, backupCount=5)
    log_handler.setFormatter(
        logging.Formatter('%(asctime)s %(levelname)s: %(message)s' ))
    applogger = logging.getLogger("GA")
    applogger.setLevel(logging.DEBUG)
    applogger.addHandler(log_handler)

    @staticmethod
    def logInfo(infoString):
        LogWriter.applogger.info(str(infoString))
        print "Info " + str(infoString)
        pass

    @staticmethod
    def logDebug(infoString):
        LogWriter.applogger.debug(str(infoString))
        print "Debug " + str(infoString)
        pass

    @staticmethod
    def logError(infoString):
        LogWriter.applogger.error(str(infoString))
        print "Error " + str(infoString)
        pass