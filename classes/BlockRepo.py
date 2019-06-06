import json
import os.path

from OPP.classes.Decoder import object_decoder
from OPP.classes.LogWriter import LogWriter


class BlockRepository:
        @staticmethod
        def getRepoPath():
            windowsFile = 'C:/PHD/Git/omero-parallel-processing/Django/OPP/blocks.json'
            linuxFile = '/home/omero/OMERO.server/Plugins/OPP/OPP/blocks.json'
            if (os.path.isfile(windowsFile)):
                return windowsFile

            return linuxFile

        @staticmethod
        def getBlocks():
            with open(BlockRepository.getRepoPath()) as data_file:
                try:
                    return json.load(data_file, object_hook=object_decoder)
                except Exception as e:
                    LogWriter.logError(e.message)
                    return []
            pass

        @staticmethod
        def getBlockFromType(blocktype):
            with open(BlockRepository.getRepoPath()) as data_file:
                blocksFromJson = json.load(data_file, object_hook=object_decoder)

            for block in enumerate(blocksFromJson):
                if (block[1].Type == blocktype):
                    return block[1]