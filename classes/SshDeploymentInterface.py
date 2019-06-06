from OPP.classes.LogWriter import LogWriter
from OPP.classes.CommandFactory import CommandFactory

from subprocess import check_output, CalledProcessError
import tempfile
import traceback
import collections


#class to abstract away some of details needed to execut commands on the server.
class SshDeploymentInterface:
    namespace = "de.c3e.workflow"

    def __init__(self, omeroHost, clusterUserAndAddress, sessionId,homepath, mpipath, additionalRunparameter):
        self.sessionId = sessionId
        self.hostName = omeroHost
        self.clusterUserAndAddress = clusterUserAndAddress
        self.homePath = homepath
        self.mpiPaht = mpipath
        self.additionalRunparameter = additionalRunparameter

    def SetConnection(self, conn):
        self.connection = conn
        self.sessionId = conn._getSessionId()
        pass

    def GetHomePath(self):
        return self.homePath

    def ExecuteCommandOnServer(self, command):
        LogWriter.logInfo("ssh " + self.clusterUserAndAddress + " \"" + command + "\"")
        try:
            consoleOut = check_output(["ssh", self.clusterUserAndAddress, command])
            LogWriter.logDebug("Console out :\n" + str(consoleOut))
            return 0
        except CalledProcessError, e:
            LogWriter.logDebug("Console out ("+ str(e.returncode) + "):\n" + str(e.output))
            return e.returncode

    def ExecuteCommandOnServerOutput(self, command):
        LogWriter.logInfo("ssh " + self.clusterUserAndAddress + " " + command)
        try:
            consoleOut = check_output(["ssh", self.clusterUserAndAddress, command])
            LogWriter.logDebug("Console out :\n" + str(consoleOut))
            return ""
        except CalledProcessError, e:
            LogWriter.logDebug("Console out (" + str(e.returncode) + "):\n" + str(e.output))
            return str(e.output)

    def ExecuteCommandOnServerOutput2(self, command):
        LogWriter.logInfo("ssh " + self.clusterUserAndAddress + " " + command)
        try:
            consoleOut = check_output(["ssh", self.clusterUserAndAddress, command])
            LogWriter.logDebug("Console out :\n" + str(consoleOut))
            return consoleOut
        except CalledProcessError, e:
            LogWriter.logDebug("Console out (" + str(e.returncode) + "):\n" + str(e.output))
            return str(e.output)


    def CopyToServer(self, fullDeploymentFolderName, localFile):
        LogWriter.logDebug("scp " + localFile + " " + self.clusterUserAndAddress + ":" + fullDeploymentFolderName)
        try:
            consoleOut = check_output(["scp", localFile, self.clusterUserAndAddress + ":" + fullDeploymentFolderName])
            LogWriter.logDebug("Console out: \n " + str(consoleOut))
            return 0
        except CalledProcessError, e:
            LogWriter.logDebug("Console out (" + str(e.returncode) + ") : \n" + str(e.output))
            return e.returncode

    def CopyFromServer(self, pathOnCluster, localPath , recursive):
        if (recursive):
            LogWriter.logDebug(
            "scp -r " + self.clusterUserAndAddress + ":" + pathOnCluster + " " + localPath + " ")
        else:
            LogWriter.logDebug(
                "scp " + self.clusterUserAndAddress + ":" + pathOnCluster + " " + localPath + " ")

        try:
            if (recursive):
                consoleOut = check_output(["scp","-r", self.clusterUserAndAddress + ":" + pathOnCluster, localPath])
            else:
                consoleOut = check_output(["scp", self.clusterUserAndAddress + ":" + pathOnCluster, localPath])
            LogWriter.logDebug("Console out: \n " + str(consoleOut))
            return 0
        except CalledProcessError, e:
            LogWriter.logDebug("Console out (" + str(e.returncode) + ") : \n" + str(e.output))


    def DownloadImageFileToCluster(self, id , workingFolderOnCluster):
        command = CommandFactory.GetDownloadCommand(id,workingFolderOnCluster , self.hostName, self.sessionId)
        self.ExecuteCommandOnServer(command)

    def DownloadFileToCluster(self, id , workingFolderOnCluster):
        command = CommandFactory.GetDownloadCommandFile(id,workingFolderOnCluster , self.hostName, self.sessionId)
        self.ExecuteCommandOnServer(command)


    def GetFileInformationOnCluster(self, path):
        infors = self.ExecuteCommandOnServerOutput2("stat " + path)
        hash = self.ExecuteCommandOnServerOutput2("sha256sum " + path + " | cut -f 1 -d \" \"")
        return "FileInfo:"+ infors.replace("\n"," ").replace("\t", " ") + " Hash sha256sum: " + hash.strip()

    def UploadFiles(self, fileNamesWithDatasetIds, fullWorkingFolderOnCluster):
        ids = []
        for i in range(len(fileNamesWithDatasetIds)):
            command = CommandFactory.GetUploadCommand(fileNamesWithDatasetIds[i][0], fileNamesWithDatasetIds[i][1],
                                                      fullWorkingFolderOnCluster, self.hostName, self.sessionId)

            # can't use return code, since linux return code is mod 256
            # => cli will output  "Return with code: 720 " in its last line
            output = self.ExecuteCommandOnServerOutput(command)
            lines = output.splitlines()
            lastline = lines[len(lines)-1]
            LogWriter.logDebug("Last Line of Upload "+ str(lastline))
            splitted = lastline.split(":")
            idString = (splitted[len(splitted)-1])
            ids.append(int(idString))
        return ids;

    def isDeploymentExists(self, fullDeploymentFolderName):
        return self.ExecuteCommandOnServer("stat " + fullDeploymentFolderName)

    def DeployDeployment(self,fullDeploymentFolderName, deploymentFile):
        self.ExecuteCommandOnServer("mkdir " + fullDeploymentFolderName)
        self.CopyToServer(deploymentFile , fullDeploymentFolderName)
        self.ExecuteCommandOnServer("tar -xzf " + fullDeploymentFolderName + "aDeployment.tgz -C " + fullDeploymentFolderName)

    def LinkFolderOnServer(self, sourcefolder, targetFolder) :
        self.ExecuteCommandOnServer( "ln -s " + sourcefolder + " " + targetFolder)

    def CreateFolderOnServer(self, folder) :
        self.ExecuteCommandOnServer("mkdir " + folder)

    def StartWorkflowExecution(self, fullWorkingFolderOnCluster, jsonFile):
        goToFolder = "cd " + fullWorkingFolderOnCluster
        command = CommandFactory.GetRunProcessManagerCommandJson(fullWorkingFolderOnCluster,jsonFile, self.mpiPaht)
        if self.additionalRunparameter :
            command = command + str(self.additionalRunparameter)
        return self.ExecuteCommandOnServer(goToFolder + " ; " + command)
        pass

    def GetImageName(self,id):
        imageObject = self.connection.getObject("Image",id)
        return imageObject.getName()

    def GetFileName(self,id):
        fileObject = self.connection.getObject("OriginalFile",id)
        return fileObject.getName()

    # Upload a file to omero, annotate a list of images with it, return the file id fo the uploaded file
    def AnnotateImagesWithFile(self,ids, filePath):
        if not isinstance(ids, collections.Sequence):
            ids = [ids]

        fileAnn = self.connection.createFileAnnfromLocalFile(filePath, mimetype="text/plain", ns=self.namespace, desc=None)
        for i in range(len(ids)):
            try:
                image = self.connection.getObject("Image", ids[i])
                if image is None:
                    LogWriter.logError("DataSet " + ids[i] + " not found")
                    continue
                image.linkAnnotation(fileAnn)
            except :
                LogWriter.logError("Could not annotate id " + str(ids[i]) + str(traceback.format_exc()))
        return fileAnn.getId()

    # Upload a file to omero, annotate a list of data set with it, return the file id fo the uploaded file
    def AnnotateDataSetsWithFile(self,ids, filePath):
        if not isinstance(ids, collections.Sequence):
            ids = [ids]

        fileAnn = self.connection.createFileAnnfromLocalFile(filePath, mimetype="text/plain", ns=self.namespace, desc=None)
        for i in range(len(ids)):
            LogWriter.logDebug("Annotate Dataset " + str(ids[i]) + "with " + str(filePath))

            try:
                ds = self.connection.getObject("DataSet", ids[i])
                if ds is None:
                    LogWriter.logError("DataSet " + ids[i] + " not found")
                    continue

                ds.linkAnnotation(fileAnn)

                LogWriter.logDebug("Annotate Dataset " + str(ids[i]) + "with " + str(filePath) + " Succsessfull")
            except :
                LogWriter.logError("Could not annotate id " + str(ids[i]) + str(traceback.format_exc()))
        return fileAnn.getId()

    def GetResultFromServer(self, fileId):
        data = ""
        try:
            ann = self.connection.getObject("FileAnnotation", fileId)

            if ann is None :
                LogWriter.logError("Could not get file annotation with id " + fileId)
                return None

            tf = tempfile.NamedTemporaryFile(prefix="workflow", suffix=".json", delete=False)
            f = open(str(tf.name), 'w')
            try:
                for chunk in ann.getFileInChunks():
                    f.write(chunk)
            finally:
                f.close()

            with open(tf.name, 'r') as myfile:
                data = myfile.read().replace('\n', '')
                LogWriter.logDebug(data)
        except:
            LogWriter.logError("Could not load file annotation" + str(traceback.format_exc()))
        return data


    def GetAnnotationFileFromServer(self, fileId):
        data = None
        name = ""
        try:
            ann = self.connection.getObject("FileAnnotation", fileId)
            name=ann.getFileName()
            for chunk in ann.getFileInChunks():
                if data is None:
                    data = chunk
                else:
                    data += chunk
            LogWriter.logDebug("Downloaded " + str(name) + " " + str(len(data)) + " size")
        except:
            LogWriter.logError("Could not load file annotation" + str(traceback.format_exc()))
        return name, data

    def GetDataSetAnnotations(self, datasetId):
        ds = self.connection.getObject("DataSet",datasetId)
        if ds is None:
            return None

        ann = list(ds.listAnnotations())
        result = []
        for i in range(len(ann)):
            # check NS?
            result.append([ann[i].getId(),ann[i].getFileName()])
        return result
