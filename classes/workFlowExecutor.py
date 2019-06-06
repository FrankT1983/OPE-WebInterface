
import uuid
import json

import copy
import os

import tempfile
import shutil

from OPP.classes.InterfaceFactory import InterfaceFactory
from OPP.classes.LogWriter import LogWriter
from OPP.classes.RunRepo import RunRepository
from OPP.workFlowAnalyser import WorkFlowAnalyser
from OPP.classes.JavaHelper import JavaHelper

import traceback


class WorkflowExecutor:
    serverInterface = InterfaceFactory.getServerInterface("omero-address", "login@cluster",
                                                          "SessionUUID", "/home/", " ", " -Single")

    jsonParameterFileName = "parameters.json"

    @staticmethod
    def SetConnectionObject(conn):
        WorkflowExecutor.serverInterface.SetConnection(conn)

    ## Start the Execution on the cluster
    #
    @staticmethod
    def StartExcutionOnCluster(workflowAndParameterDic):
        try:
            hadErrors = False

            runId = str(uuid.uuid4())
            intermediateDataSet = 751
            workflowAndParameterDic["runId"] = runId
            workflowAndParameterDic["intermediateDataSet"] = intermediateDataSet
            unmodiviedParams = copy.deepcopy(workflowAndParameterDic["parameters"])

            name = ""
            if ("name" in workflowAndParameterDic):
                name= workflowAndParameterDic["name"]

            RunRepository.registerRun(runId, name)

            workingFolderName = runId  # create a temp folder on the cluster with this id
            workingFolderOnCluster = "omeroEnv/" + workingFolderName + "/"

            fullWorkingFolderOnCluster = WorkflowExecutor.serverInterface.GetHomePath() + workingFolderOnCluster;
            fullDeploymentFolderName = WorkflowExecutor.serverInterface.GetHomePath() + "omeroEnv/deployment/"

            RunRepository.updateStatusRun(runId, "Deploy environment")
            WorkflowExecutor.CreateTempFolderOnServer(fullWorkingFolderOnCluster)
            WorkflowExecutor.CreateTempFolderOnServer(fullWorkingFolderOnCluster + "PluginDeploy/" )
            WorkflowExecutor.CreateTempFolderOnServer(fullWorkingFolderOnCluster + "Tool/")
            LogWriter.logInfo("+ Check deployment and create deployment ")
            WorkflowExecutor.CheckOrDeployDeployment(fullDeploymentFolderName, fullWorkingFolderOnCluster)

            versions = workflowAndParameterDic["versions"]
            blocks = workflowAndParameterDic["blocks"]
            for i in range(0,len(versions)) :
                correspondingBlock = None
                for j in range(0,len (blocks)):
                    if( blocks[j]["elementId"] == versions[i][0]):
                        correspondingBlock = blocks[j]
                        break

                if not correspondingBlock is None :
                    git = correspondingBlock["GitRepo"]
                    path = correspondingBlock["GitFilePath"]
                    try:
                        pathToJar = JavaHelper.compileOrGetFromCache(git,path, versions[i][1], path)
                        if not pathToJar is None :
                            WorkflowExecutor.serverInterface.CopyToServer(fullWorkingFolderOnCluster + "PluginDeploy/" , pathToJar)

                            toolStuff = JavaHelper.checkForToolDependencies(pathToJar)
                            if not toolStuff is None and len(toolStuff) > 0:
                                LogWriter.logInfo("ToolStuff "+str(toolStuff))
                                tool_file = JavaHelper.getToolFromVersionControl(toolStuff[0][0],toolStuff[0][1],toolStuff[0][2],toolStuff[0][3],toolStuff[0][4])
                                if not tool_file is None:
                                    WorkflowExecutor.serverInterface.CopyToServer(fullWorkingFolderOnCluster + "Tool/", tool_file)
                                else:
                                    LogWriter.logDebug("No Tool file downloaded")

                        else :
                            LogWriter.logError("No compiled file created")
                    except Exception as e:
                        LogWriter.logError(e.message)
                        LogWriter.logError(traceback.format_exc())


            LogWriter.logInfo("+ Download Input files ")
            RunRepository.updateStatusRun(runId, "Download Inputs")
            imageIds = WorkFlowAnalyser.GetRequiredImageIdsFromWorkflow(workflowAndParameterDic)
            WorkflowExecutor.DownloadImageFilesToTempFolderOnCluster(fullWorkingFolderOnCluster, imageIds)

            fileIds = WorkFlowAnalyser.GetRequiredFileIdsFromWorkflow(workflowAndParameterDic)
            WorkflowExecutor.DownloadFilesToTempFolderOnCluster(fullWorkingFolderOnCluster, fileIds)

            # find Result images => import into Data Set
            imagesToUpLoadToDataSet = WorkFlowAnalyser.GetImageUploadsFromWorkflow(workflowAndParameterDic)
            imageNamesWithDatasetIds = WorkflowExecutor.CreateTempFileNamesForUploadsAndModifyParameters(imagesToUpLoadToDataSet, ".tiff")

            # find result file => image annotation
            dataFilesToAnnotate = WorkFlowAnalyser.GetImagesToAnnotateFromWorkflow(workflowAndParameterDic)
            dataFileNamesWithImageIds = WorkflowExecutor.CreateTempFileNamesForUploadsAndModifyParameters(dataFilesToAnnotate, ".txt")

            LogWriter.logInfo("+ Write Workflow file ")
            WorkflowExecutor.WriteWorkflowFileToCluster(workflowAndParameterDic, fullWorkingFolderOnCluster)

            #####################################################################################################
            #####################################################################################################
            #####################################################################################################
            #####################################################################################################
            #####################################################################################################
            #####################################################################################################
            #return

            #####################################################################################################
            #####################################################################################################

            LogWriter.logInfo("+ Start execution ")
            RunRepository.updateStatusRun(runId, "Execute Workflow")
            errorcode = WorkflowExecutor.StartWorkflowExecution(fullWorkingFolderOnCluster)
            if (errorcode >0 ):
                LogWriter.logInfo("+ Error starting execution: ErrorCode " + str(errorcode))
                RunRepository.updateStatusRun(runId, "Failed to execute Workflow Manager with error code : " + str(errorcode))
                return

            LogWriter.logInfo("+ Upload Results")
            RunRepository.updateStatusRun(runId, "Upload results")
            try:
                ids = WorkflowExecutor.UploadFiles(imageNamesWithDatasetIds, fullWorkingFolderOnCluster)
                LogWriter.logDebug("+ Uploaded Created files as:" + str(ids))
            except:
                LogWriter.logDebug("+ Upload results faild" )
                ids = []
                hadErrors = True

            WorkflowExecutor.AnnotateImagesWithResultFiles(dataFileNamesWithImageIds, fullWorkingFolderOnCluster)

            # annotate uploaded files with workflow description
            WorkFlowAnalyser.MergeReproducibilityParameters(unmodiviedParams, imageIds)
            resultAnnotationId = WorkflowExecutor.StoreWorkflowFile(ids, unmodiviedParams, workflowAndParameterDic)

            # get Intermediates from cluster
            RunRepository.updateStatusRun(runId, "Collect Intermediates")
            WorkflowExecutor.GetAndStoreIntermediates(fullWorkingFolderOnCluster, intermediateDataSet, runId)

            # get Statistics from cluster
            RunRepository.updateStatusRun(runId, "Collect Statistics")
            WorkflowExecutor.GetAndStoreStatistics(fullWorkingFolderOnCluster, intermediateDataSet, runId)

            # Cleanup
            #todo

            LogWriter.logInfo("+ Finished Execution ")
            RunRepository.FinishRun(runId, resultAnnotationId, hadErrors)

        except Exception as e:
            RunRepository.updateStatusRun(runId, "Failed with " + e.message)
            LogWriter.logError(e.message)
            LogWriter.logError(traceback.format_exc())

    @staticmethod
    def StoreWorkflowFile(ids, unmodiviedParams, workflowAndParameterDic):
        workflowAndParameterDic["parameters"] = unmodiviedParams
        tmpfile = WorkflowExecutor.WriteToFile(workflowAndParameterDic)
        LogWriter.logDebug("File :" + tmpfile.name)
        resultAnnotationId = WorkflowExecutor.AnnotateImagesWithFile(ids, tmpfile.name)
        os.remove(tmpfile.name)
        return resultAnnotationId

    @staticmethod
    def GetAndStoreIntermediates(fullWorkingFolderOnCluster, intermediateDataSet, runId):
        tempIntermediatePath = tempfile.mkdtemp()
        LogWriter.logInfo("+ Copy Intermediates to " + str(tempIntermediatePath))
        WorkflowExecutor.DownloadFilesFromClusterToHere(fullWorkingFolderOnCluster + "intermediates/",
                                                        tempIntermediatePath, True)
        tempIntermediatePath = tempIntermediatePath + "/intermediates/"
        RunRepository.updateStatusRun(runId, "Upload Intermediates")

        files = WorkflowExecutor.ToFileList(tempIntermediatePath)
        renamedFiles = WorkflowExecutor.PrefixFiles(files, "intermediate_" + str(runId) + "_")
        WorkflowExecutor.AnnotateDataSetsWithFiles([intermediateDataSet], renamedFiles)
        WorkflowExecutor.RemoveFilesOrFolder(tempIntermediatePath)


    @staticmethod
    def GetAndStoreStatistics(fullWorkingFolderOnCluster, intermediateDataSet, runId):
        tempStatisticsPath = tempfile.mkdtemp()
        LogWriter.logInfo("+ Copy Statistics to " + str(tempStatisticsPath))
        WorkflowExecutor.DownloadFilesFromClusterToHere(fullWorkingFolderOnCluster + "statistics/statistics.txt",
                                                        tempStatisticsPath, True)
        tempIntermediatePath = tempStatisticsPath + "/statistics.txt"
        RunRepository.updateStatusRun(runId, "Upload Statistics")

        files = WorkflowExecutor.ToFileList(tempIntermediatePath)
        renamedFiles = WorkflowExecutor.PrefixFiles(files, "statistics_" + str(runId) + "_")
        WorkflowExecutor.AnnotateDataSetsWithFiles([intermediateDataSet],renamedFiles)
        WorkflowExecutor.RemoveFilesOrFolder(tempIntermediatePath)


    @staticmethod
    def ToFileList(path):
        files = []
        if (os.path.isdir(path)):
            filesNames = os.listdir(path)
            for file in filesNames :
                files.append(path + file)

        elif (os.path.isfile(path)):
            files = [path]
        else:
            LogWriter.logError("Path is neither directory nor file: " + path)
        return files

    @staticmethod
    def RemoveFilesOrFolder(path):
        if (os.path.isdir(path)):
            shutil.rmtree(path)
        elif (os.path.isfile(path)):
            os.remove(path)

    @staticmethod
    def PrefixFiles(fileList, prefix):
        renamedFiles = []
        for fullPath in fileList:
            try:
                directoryname , filename = os.path.split(fullPath)
                renamedFileFull = directoryname + "/" + prefix + filename
                os.rename( fullPath, renamedFileFull)
                renamedFiles.append(renamedFileFull)
            except Exception as e:
                LogWriter.logError("+ Error renaming " + e.message + " " +fullPath + " => " + renamedFileFull)
                LogWriter.logError(traceback.format_exc())
        return renamedFiles

    @staticmethod
    def AnnotateImagesWithResultFiles(annotationDatasetIds, fullWorkingFolderOnCluster):
        for annotate in annotationDatasetIds:
            annotationFileName = annotate[0]
            WorkflowExecutor.DownloadFilesFromClusterToHere(fullWorkingFolderOnCluster + annotationFileName,
                                                            annotationFileName)

            if not os.path.exists(annotationFileName) :
                LogWriter.logError("Result file was not found => could not be annotated (" + annotationFileName + ")")
            else:
                WorkflowExecutor.AnnotateImagesWithFile([annotate[1]], annotationFileName)
                os.remove(annotationFileName)

    @staticmethod
    def CreateTempLocalFolder():
        folder = tempfile.mkdtemp()
        return folder

    @staticmethod
    def DownloadImageFilesToTempFolderOnCluster(workingFolderOnCluster, imageIds):
        if (len(imageIds) == 0):
            LogWriter.logInfo("no images to download")

        for i in range(len(imageIds)):
            # blockId | portName | value
            id = imageIds[i][2]
            WorkflowExecutor.DownloadImgeToFolderOnCluster(workingFolderOnCluster, id)
            LogWriter.logDebug("Download finished " + str(id))
            LogWriter.logDebug("ImageName finished " + WorkflowExecutor.GetImageName(id))

            # change parameter for graph transformatoni
            imageIds[i][1] = "Value"
            imageIds[i][2] = (WorkflowExecutor.GetImageName(id))
            imageIds[i][3] = "out"
            imageIds[i].append(WorkflowExecutor.GetFileInformation(workingFolderOnCluster + imageIds[i][2]))
            imageIds[i].append("OMERO ID:" + str(id))
            LogWriter.logDebug("Created Parameter " + str(imageIds[i]))

    @staticmethod
    def DownloadFilesToTempFolderOnCluster(workingFolderOnCluster, fileIds):
        if (len(fileIds) == 0):
            LogWriter.logInfo("no other files to download")

        for i in range(len(fileIds)):
            # blockId | portName | value
            id = fileIds[i][2]
            WorkflowExecutor.DownloadFileToFolderOnCluster(workingFolderOnCluster, id)
            LogWriter.logDebug("Download finished " + str(id))
            LogWriter.logDebug("FileName finished " + WorkflowExecutor.GetFileName(id))

            # change parameter for graph transformatoni
            fileIds[i][1] = "Value"
            fileIds[i][2] = (WorkflowExecutor.GetFileName(id))
            fileIds[i][3] = "out"
            fileIds[i].append( WorkflowExecutor.GetFileInformation(workingFolderOnCluster +  fileIds[i][2]))

            LogWriter.logDebug("Created Parameter " + str(fileIds[i]))



    @classmethod
    def CreateTempFileNamesForUploadsAndModifyParameters(self, filesToUpLoad, extension):
        result = []
        if (len(filesToUpLoad) == 0):
            LogWriter.logInfo("no files to upload")
            return result

        for i in range(len(filesToUpLoad)):
            tempFileName = str(uuid.uuid4()) + extension
            result.append([tempFileName, filesToUpLoad[i][2]])
            filesToUpLoad[i][1] = "Value"
            filesToUpLoad[i][2] = tempFileName
            filesToUpLoad[i][3] = "out"
        return result

    @staticmethod
    def DownloadImgeToFolderOnCluster(workingFolderOnCluster, imageId):
        WorkflowExecutor.serverInterface.DownloadImageFileToCluster(imageId, workingFolderOnCluster)
        return



    @staticmethod
    def DownloadFileToFolderOnCluster(workingFolderOnCluster, fileId):
        WorkflowExecutor.serverInterface.DownloadFileToCluster(fileId, workingFolderOnCluster)
        return

    @staticmethod
    def GetFileInformation(path):
        return WorkflowExecutor.serverInterface.GetFileInformationOnCluster(path)

    @classmethod
    def UploadFiles(self, fileNamesWithDatasetIds, fullWorkingFolderOnCluster):
        return WorkflowExecutor.serverInterface.UploadFiles(fileNamesWithDatasetIds, fullWorkingFolderOnCluster)

    @staticmethod
    def CheckOrDeployDeployment(fullDeploymentFolderName, fullWorkingFolderOnCluster):
        LogWriter.logInfo("Check if deployment exists")
        deploymentFile = "aDeployment.tgz"
        deploymentFolderExists = not WorkflowExecutor.serverInterface.isDeploymentExists(fullDeploymentFolderName)
        if not deploymentFolderExists:
            LogWriter.logInfo("No Deployment found: copy new")
            WorkflowExecutor.serverInterface.DeployDeployment(fullDeploymentFolderName, deploymentFile)
        else:
            LogWriter.logInfo("Deployment found")

        WorkflowExecutor.serverInterface.LinkFolderOnServer(fullDeploymentFolderName + "*", fullWorkingFolderOnCluster)
        # remap icy plugin folder for plugin detection to work
        WorkflowExecutor.serverInterface.LinkFolderOnServer(fullDeploymentFolderName + "Libs/Icy/plugins",
                                                            fullWorkingFolderOnCluster)

    @classmethod
    def CreateTempFolderOnServer(cls, fullWorkingFolderOnCluster):
        WorkflowExecutor.serverInterface.CreateFolderOnServer(fullWorkingFolderOnCluster)

    @classmethod
    def WriteWorkflowFileToCluster(cls, workflowAndParameterDic, fullWorkingFolderOnCluster):
        LogWriter.logInfo("ParameterDir: " + str(workflowAndParameterDic))

        localTempfolder = WorkflowExecutor.CreateTempLocalFolder()
        parameterFile = localTempfolder + "/" + WorkflowExecutor.jsonParameterFileName
        LogWriter.logDebug("Temp Workflow file : " + parameterFile)
        with open(parameterFile, 'w') as outfile:
            json.dump(workflowAndParameterDic, outfile)

        WorkflowExecutor.serverInterface.CopyToServer(fullWorkingFolderOnCluster, parameterFile)

    @classmethod
    def StartWorkflowExecution(self, fullWorkingFolderOnCluster):
        return WorkflowExecutor.serverInterface.StartWorkflowExecution(fullWorkingFolderOnCluster,
                                                                WorkflowExecutor.jsonParameterFileName)


    @staticmethod
    def GetImageName(id):
        return WorkflowExecutor.serverInterface.GetImageName(id)
        pass

    @staticmethod
    def GetFileName(id):
        return WorkflowExecutor.serverInterface.GetFileName(id)
        pass

    @staticmethod
    def AnnotateImagesWithFile(ids, filePath):
        return WorkflowExecutor.serverInterface.AnnotateImagesWithFile(ids, filePath)

    @staticmethod
    def AnnotateDataSetsWithFile(ids, filePath):
        return WorkflowExecutor.serverInterface.AnnotateDataSetsWithFile(ids, filePath)

    @staticmethod
    # Upload a list of filesomero, annotate a list of data set with them, return the file ids fo the uploaded file
    def AnnotateDataSetsWithFiles(datasetIds, fileList):
        fileIds = []
        for filename in fileList:
            try:
                fileIds.append(WorkflowExecutor.AnnotateDataSetsWithFile(datasetIds, filename))
            except Exception as e:
                LogWriter.logError("+ Error annotating " + e.message)
                LogWriter.logError(traceback.format_exc())
        return fileIds

    @staticmethod
    def WriteToFile(objectToWrite):
        tf = tempfile.NamedTemporaryFile(prefix="workflow", suffix=".json", delete=False)
        json.dump(objectToWrite, tf, sort_keys=True, indent=4)
        tf.close()
        return tf

    @staticmethod
    def GetResultFromServer(fileId):
        return WorkflowExecutor.serverInterface.GetResultFromServer(fileId)

    @staticmethod
    def GetAnnotationFileAndName(fileId):
        return WorkflowExecutor.serverInterface.GetAnnotationFileFromServer(fileId)

    @staticmethod
    def DownloadFilesFromClusterToHere(pathOnCluster, localPath, recursiv = False):
        WorkflowExecutor.serverInterface.CopyFromServer(pathOnCluster,localPath, recursiv)

    @staticmethod
    def GetDataSetAnnotations(datasetId):
        return WorkflowExecutor.serverInterface.GetDataSetAnnotations(datasetId)
