from OPP.classes.LogWriter import LogWriter
from OPP.classes.DummyDeploymentInterface import DummyDeploymentInterface
from OPP.classes.SshDeploymentInterface import SshDeploymentInterface
from OPP.classes.LocalDeploymentInterface import LocalDeploymentInterface


class InterfaceFactory :
    interfaceToUse = None

    useOmero = True

    @staticmethod
    def getServerInterface(omeroHost, clusterUserAndAddress, sessionId,homepath,mpipath , additionalRunparameter=None):
        if InterfaceFactory.interfaceToUse == None :
            if InterfaceFactory.useOmero:
                LogWriter.logInfo("Create OmeroInterface ")
                InterfaceFactory.interfaceToUse = SshDeploymentInterface(omeroHost, clusterUserAndAddress, sessionId,homepath,mpipath,additionalRunparameter)
            else:
                LogWriter.logInfo("Create Dummy OmeroInterface ")
                InterfaceFactory.interfaceToUse = DummyDeploymentInterface(omeroHost, clusterUserAndAddress, sessionId,homepath,mpipath,additionalRunparameter)
        return InterfaceFactory.interfaceToUse
