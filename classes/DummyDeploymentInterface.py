from OPP.classes.LogWriter import LogWriter
from OPP.classes.CommandFactory import CommandFactory

class DummyDeploymentInterface:
    def __init__(self, omeroHost, clusterUserAndAddress, sessionId,homepath, mpipath):
        self.sessionId = sessionId
        self.hostName = omeroHost
        self.clusterUserAndAddress = clusterUserAndAddress
        self.homePath = homepath
        self.mpiPaht = mpipath

    def SetConnection(self,conn):
        pass

    def GetHomePath(self):
        return self.homePath

    def ExecuteCommandOnServer(self, command):
        #return call(["ssh", self.clusterUserAndAddress, command])
        LogWriter.logInfo("ssh " + self.clusterUserAndAddress + " " + command)
        return False

    def CopyToServer(self, destinationFolder, fileToCopy):
        # call(["scp", deploymentFile, self.clusterUserAndAddress + ":" + fullDeploymentFolderName])
        LogWriter.logInfo("scp " + fileToCopy + " " + self.clusterUserAndAddress + ":" + destinationFolder)

    def CopyFromServer(self, pathOnCluster, localPath, recusive):
        LogWriter.logDebug("scp " + self.clusterUserAndAddress + ":" + pathOnCluster + " " + localPath + " ")
        pass


    def GetImageFileName(self, id):
        return "image" + str(id)

    def GetFileName(self, id):
        return "file" + str(id)


    def DownloadImageFileToCluster(self, id , workingFolderOnCluster):
        command = CommandFactory.GetDownloadCommand(id,workingFolderOnCluster , self.hostName, self.sessionId)
        self.ExecuteCommandOnServer(command)


    def DownloadFileToCluster(self, id , workingFolderOnCluster):
        command = CommandFactory.GetDownloadCommandFile(id,workingFolderOnCluster , self.hostName, self.sessionId)
        self.ExecuteCommandOnServer(command)

    def GetFileInformationOnCluster(self, path):
        return "FileInfoDumy:"+path

    def UploadFiles(self, fileNamesWithDatasetIds, fullWorkingFolderOnCluster):
        for i in range(len(fileNamesWithDatasetIds)):
            command = CommandFactory.GetUploadCommand(fileNamesWithDatasetIds[i][0], fileNamesWithDatasetIds[i][1],
                                                      fullWorkingFolderOnCluster, self.hostName, self.sessionId)
            self.ExecuteCommandOnServer(command)
        return [25]
        pass


    def isDeploymentExists(self, fullDeploymentFolderName):
        return self.ExecuteCommandOnServer("stat " + fullDeploymentFolderName)

    def DeployDeployment(self,fullDeploymentFolderName, deploymentFile):
        self.ExecuteCommandOnServer("mkdir " + fullDeploymentFolderName)
        self.CopyToServer(deploymentFile , fullDeploymentFolderName)
        self.ExecuteCommandOnServer("tar -xzf " + fullDeploymentFolderName + "aDeployment.tgz -C " + fullDeploymentFolderName)

    def LinkFolderOnServer(self, sourcefolder, targetFolder) :
        self.ExecuteCommandOnServer( "ln -s " + sourcefolder + "* " + targetFolder )

    def CreateFolderOnServer(self, folder) :
        self.ExecuteCommandOnServer("mkdir "+ folder)

    def StartWorkflowExecution(self, fullWorkingFolderOnCluster, jsonFile):
        command = CommandFactory.GetRunProcessManagerCommandJson(fullWorkingFolderOnCluster,jsonFile)
        self.ExecuteCommandOnServer(command)
        return 0

    def AnnotateImagesWithFile(self,ids, filePath):
        return 582

    def AnnotateDataSetsWithFile(self, ids, filePath):
        return 582

    def GetImageName(self,id):
        return "Foo.jpg"

    def GetResultFromServer(self, fileId):
        return "{\"blocks\":[{\"Inputs\":[\"ImageId\"],\"Outputs\":[\"LoadedImage\"],\"blockId\":\"0\",\"blockName\":\"OmeroImage\",\"blockType\":\"plugins.Frank.de.c3e.ProcessManager.OmeroImageInputBlock\",\"elementId\":\"0\",\"positionX\":476,\"positionY\":256},{\"Inputs\":[\"Sequence\",\"Channel\"],\"Outputs\":[\"Extracted\"],\"blockId\":\"ExtractChannel\",\"blockName\":\"ExtractChannel\",\"blockType\":\"plugins.tprovoost.sequenceblocks.extract.ExtractChannel\",\"elementId\":\"1\",\"positionX\":763,\"positionY\":427},{\"Inputs\":[\"Image to save\",\"DataSet Id\"],\"Outputs\":[],\"blockId\":\"OmeroImageSaveToDataSet\",\"blockName\":\"OmeroImageSaveToDataSet\",\"blockType\":\"plugins.Frank.de.c3e.ProcessManager.OmeroImageSaveToDataSet\",\"elementId\":\"2\",\"positionX\":1052,\"positionY\":630}],\"intermediateDataSet\":751,\"intermediates\":true,\"links\":[{\"anchors\":[[1,0.5,1,0,0,0],[0,0.3333333333333333,-1,0,0,0]],\"sourceBlock\":\"0\",\"sourcePort\":\"LoadedImage\",\"targetBlock\":\"1\",\"targetPort\":\"Sequence\"},{\"anchors\":[[1,0.5,1,0,0,0],[0,0.3333333333333333,-1,0,0,0]],\"sourceBlock\":\"1\",\"sourcePort\":\"Extracted\",\"targetBlock\":\"2\",\"targetPort\":\"Image to save\"}],\"name\":\"ExtractChannel\",\"parameters\":[[\"2\",\"DataSet Id\",\"601\",\"in\"],[\"1\",\"Channel\",\"0\",\"in\"],[\"0\",\"ImageId\",\"351\",\"in\"]],\"runId\":\"4e075173-1bd8-4353-8123-1d0d362ccbac\"}"

    def GetAnnotationFileFromServer(self, fileId):
        if (fileId == 1):
            return "dummyData.txt", "dumm data"
        if (fileId == 2):
            return "Full path,Parent folder,Dataset,ROI,Color,X,Y,Z,T,C,Box width,Box height,Box depth,Contour,Interior,Sphericity (%),Roudness (%),Convexity (%),Max. Feret diam.,Ellipse (a),Ellipse (b),Ellipse (c),Yaw angle,Pitch angle,Roll angle,Elongation ratio,Flatness ratio (3D),Min.,Avg.,Max.,Sum,Std. dev. \n" +\
                        "--,--,--,Object #1 (value: 1.0),,\"544,1513503\",\"69,97258883\",0,0,0,355,159,N/A,\"1926,71046\",24625,\"28,87198187\",\"1,017974666\",55,\"359,6804137\",\"277,3524479\",\"133,2439945\",N/A,\"82,53040768\",0,0,\"2,081538076\",N/A,,,,, \n" + \
                        "--,--,--,Object #2 (value: 1.0),,\"612,6666667\",\"56,16666667\",0,0,0,2,4,N/A,\"9,670543795\",6,\"89,79034932\",20,100,\"3,16227766\",#NUM!,#DIV/0!,N/A,90,0,0,#NUM!,N/A,,,,,                                                    \n" +\
                        "--,--,--,Object #3 (value: 1.0),,\"626,4444444\",\"125,6666667\",0,0,0,4,3,N/A,\"10,92817459\",9,\"97,31472548\",\"38,28207467\",100,\"3,16227766\",\"3,168638534\",\"2,021656331\",N/A,\"97,46959232\",0,0,\"1,567347766\",N/A,,,,,        \n" +\
                        "--,--,--,Object #4 (value: 1.0),,\"647,5\",\"51,5\",0,0,0,2,2,N/A,\"5,656854249\",4,100,100,100,\"1,414213562\",#NUM!,\"0,0000055398\",N/A,180,0,0,#NUM!,N/A,,,,,                                                                 \n" +\
                        "--,--,--,Object #5 (value: 1.0),,\"414,2222222\",\"352,0222222\",0,0,0,13,5,N/A,\"29,82766953\",45,\"79,72451137\",\"31,59796809\",100,\"12,16552506\",\"11,02770804\",\"3,774165862\",N/A,\"99,78781906\",0,0,\"2,921892796\",N/A,,,,,     \n" +\
                        "--,--,--,Object #6 (value: 1.0),,\"615,972973\",\"122,6216216\",0,0,0,8,6,N/A,\"21,34213562\",37,100,\"58,8052074\",100,\"7,280109889\",\"6,94396555\",\"5,231279871\",N/A,\"171,8903855\",0,0,\"1,327393242\",N/A,,,,,                   \n" +\
                        "--,--,--,Object #7 (value: 1.0),,\"520,343934\",\"290,9399882\",0,0,0,186,156,N/A,\"1412,056059\",16980,\"32,71311016\",\"7,241119761\",73,\"202,2992832\",\"145,6151313\",\"125,8548195\",N/A,\"154,1580672\",0,0,\"1,157008781\",N/A,,,,, \n" +\
                        "--,--,--,Object #8 (value: 1.0),,\"123,7884615\",\"36,07692308\",0,0,0,10,7,N/A,\"27,77056275\",52,\"92,04960376\",\"36,55398485\",100,\"9,486832981\",\"9,251514009\",\"5,713097969\",N/A,\"95,16360709\",0,0,\"1,619351543\",N/A,,,,,     \n" +\
                        "--,--,--,Object #9 (value: 1.0),,465,\"317,5\",0,0,0,3,2,N/A,\"7,456854249\",6,100,\"44,72135955\",100,\"2,236067977\",#NUM!,#NUM!,N/A,180,0,0,#NUM!,N/A,,,,,                                                                   \n" +\
                        "--,--,--,Object #10 (value: 1.0),,\"656,7619048\",\"104,4285714\",0,0,0,7,4,N/A,\"17,22792206\",21,\"94,29348367\",\"41,47045524\",100,\"6,08276253\",\"5,953701718\",\"3,048229711\",N/A,\"92,29244278\",0,0,\"1,953167012\",N/A,,,,,      \n" +\
                        "--,--,--,Object #11 (value: 1.0),,\"637,754386\",\"105,3508772\",0,0,0,13,8,N/A,\"32,65584412\",57,\"81,95613054\",\"19,3718167\",100,\"12,64911064\",\"11,76727211\",\"5,126454655\",N/A,\"161,8051277\",0,0,\"2,295401579\",N/A,,,,,      \n" +\
                        "--,--,--,Object #12 (value: 1.0),,\"630,8888889\",\"79,4985755\",0,0,0,33,18,N/A,\"93,72539674\",351,\"70,86000893\",\"30,57385075\",87,\"33,83784863\",\"30,36849735\",\"14,60171733\",N/A,\"105,0700621\",0,0,\"2,07978943\",N/A,,,,,     \n" +\
                        "--,--,--,Object #13 (value: 1.0),,\"599,4191617\",\"157,7664671\",0,0,0,36,18,N/A,\"89,86828996\",167,\"50,97493606\",\"6,533887562\",76,\"37,33630941\",\"32,52521101\",\"6,618364025\",N/A,\"151,6423634\",0,0,\"4,914388343\",N/A,,,,,   \n" +\
                        "--,--,--,Object #14 (value: 1.0),,\"190,9900618\",\"167,6591778\",0,0,0,294,328,N/A,\"2508,344587\",56751,\"33,66700576\",\"14,61531586\",79,\"336,0133926\",\"266,617028\",\"249,5995612\",N/A,\"89,42703266\",0,0,\"1,068179073\",N/A,,,,,\n" +\
                        "--,--,--,Object #15 (value: 1.0),,\"623,7\",\"40,6\",0,0,0,6,4,N/A,\"15,29949494\",20,100,\"47,07670566\",100,\"5,830951895\",\"5,48477899\",\"3,102629617\",N/A,\"106,857956\",0,0,\"1,767783999\",N/A,,,,,                              \n" +\
                        "--,--,--,Object #16 (value: 1.0),,\"662,7482517\",\"72,16083916\",0,0,0,14,14,N/A,\"47,44137803\",143,\"89,35434081\",\"48,92158897\",100,\"16,40121947\",\"14,7991179\",\"10,85146818\",N/A,\"132,0670648\",0,0,\"1,363789457\",N/A,,,,,   \n"
        return None

    def GetDataSetAnnotations(self, datasetId):
        return [[1, "intermediate_12_12_12_12.txt"],
                [2, "intermediate_12_12_13_13.csv"]]