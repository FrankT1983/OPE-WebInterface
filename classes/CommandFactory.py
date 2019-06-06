class CommandFactory :

    @staticmethod
    def GetDownloadCommand(imageId,workingFolderOnCluster , hostname, sessionId):
        command = "java -jar " + workingFolderOnCluster + "myOmeroCli.jar" \
                                                              " -h " + hostname + \
                      " -uuid " + str(sessionId) + \
                      " -download " + str(imageId) + \
                      " -path " + workingFolderOnCluster
        return command

    @staticmethod
    def GetDownloadCommandFile(imageId, workingFolderOnCluster, hostname, sessionId):
        command = "java -jar " + workingFolderOnCluster + "myOmeroCli.jar" \
                                                          " -h " + hostname + \
                  " -uuid " + str(sessionId) + \
                  " -fileDownload " + str(imageId) + \
                  " -path " + workingFolderOnCluster
        return command

    @staticmethod
    def GetRunProcessManagerCommand(fullWorkingFolderOnCluster, parameterFile, workflowFile,mpirun):
        command =  mpirun + " java -jar " + fullWorkingFolderOnCluster + "ProcessingManager.jar" + \
                     " -WorkingFolder " + fullWorkingFolderOnCluster + \
                     " -ParamFile " + parameterFile + \
                     " -ProtocolFile " + workflowFile
        return command

    @staticmethod
    def GetRunProcessManagerCommandJson(fullWorkingFolderOnCluster, jsonFile , mpirun):
        command = mpirun + " java -jar " + fullWorkingFolderOnCluster + "ProcessingManager.jar" + \
                  " -WorkingFolder " + fullWorkingFolderOnCluster + \
                  " -JsonFile " + jsonFile
        return command

    @staticmethod
    def GetRunProcessManagerCommandLocal(fullWorkingFolderOnCluster, parameterFile, workflowFile):
        command = "java -jar " + fullWorkingFolderOnCluster + "ProcessingManager.jar" + \
                     " -WorkingFolder " + fullWorkingFolderOnCluster + \
                     " -ParamFile " + parameterFile + \
                     " -ProtocolFile " + workflowFile + \
                     " -SingleNode"

        return command

    @staticmethod
    def GetRunProcessManagerCommandJsonLocal(fullWorkingFolderOnCluster, jsonFile):
        command = "java -jar " + fullWorkingFolderOnCluster + "ProcessingManager.jar" + \
                  " -WorkingFolder " + fullWorkingFolderOnCluster + \
                  " -JsonFile " + jsonFile + \
                  " -SingleNode"
        return command

    @staticmethod
    def GetUploadCommand( fileName, dataSetId, fullWorkingFolderOnCluster, hostName, sessionId):
        command = "java -jar " + fullWorkingFolderOnCluster + "myOmeroCli.jar" + \
                " " + fullWorkingFolderOnCluster + fileName + \
                " -h " + hostName + \
                " -uuid " + str(sessionId) + \
                " -uploadToDs " + str(dataSetId)
        return command