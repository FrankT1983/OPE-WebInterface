import pickle
import os

import datetime


class RunRepository:

    runs = {}

    @staticmethod
    def getRuns():
        RunRepository.loadSerilalization()
        return RunRepository.runs

    @staticmethod
    def registerRun(runId,name = ""):
        RunRepository.runs[runId] = ["starting", str(datetime.datetime.now()), -1 , str(name)]
        RunRepository.updateSerilalization()

    @staticmethod
    def updateStatusRun(runId, status):
        RunRepository.runs[runId][0] = status
        RunRepository.updateSerilalization()

    @staticmethod
    def FinishRun(runId, resultAnnotationId, hadErrors = False):
        if hadErrors:
            RunRepository.runs[runId][0] = "Finished. With errors"
        else:
            RunRepository.runs[runId][0] = "Finished"

        RunRepository.runs[runId][2] = resultAnnotationId
        RunRepository.updateSerilalization()


    @staticmethod
    def updateSerilalization():
        # todo: this is potentialy not thread save?
        with open(RunRepository.getRunFile(), 'wb') as f:
            var = pickle.dump(RunRepository.runs, f)

    @staticmethod
    def loadSerilalization():
        if (os.path.exists((RunRepository.getRunFile()))):
            with open(RunRepository.getRunFile(), 'rb') as f:
                try :
                    RunRepository.runs = pickle.load(f)
                except Exception:
                    print("error in deserialising run repo")

    @staticmethod
    def getRunFile():
        windowsFile = 'C:/PHD/Git/omero-parallel-processing/Django/RunRepository_Runs'
        linuxFile = '/home/omero/OMERO.server/Plugins/OPP/OPP/RunRepository_Runs'
        if (os.path.isfile(windowsFile)):
            return windowsFile
        return linuxFile




RunRepository.loadSerilalization()