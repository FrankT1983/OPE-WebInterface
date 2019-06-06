import pickle
import os

class WorkflowRepsitory:

    savedWorkflows = {"next" : 0}

    @staticmethod
    def getWorkflowFile():
        windowsFile = 'C:/PHD/Git/omero-parallel-processing/Django/WorkflowRepo_Workflows'
        linuxFile = '/home/omero/OMERO.server/Plugins/OPP/OPP/WorkflowRepo_Workflows'
        if (os.path.isfile(windowsFile)):
            return windowsFile
        return linuxFile

    @staticmethod
    def getIds():
        keys = WorkflowRepsitory.savedWorkflows.keys()
        keys.remove("next")
        return keys

    @staticmethod
    def saveWorkflow(workflow):
        next = WorkflowRepsitory.savedWorkflows["next"];
        WorkflowRepsitory.savedWorkflows["next"] = next+1;
        WorkflowRepsitory.savedWorkflows[next] = workflow
        WorkflowRepsitory.updateSerilalization()

    @staticmethod
    def updateSerilalization():
        #todo: this is potentialy not thread save?
        with open(WorkflowRepsitory.getWorkflowFile(), 'wb') as f:
            var = pickle.dump(WorkflowRepsitory.savedWorkflows,f)

    @staticmethod
    def getWorkflowCount():
        return len(WorkflowRepsitory.savedWorkflows)

    @staticmethod
    def getWorkflow(idStr):
        WorkflowRepsitory.loadSerilalization()
        try:
            id = int(idStr)
            return WorkflowRepsitory.savedWorkflows[id]
        except:
            return None


    @staticmethod
    def deleteWorkflow(idStr):
        WorkflowRepsitory.loadSerilalization()
        try:
            id = int(idStr)
            del WorkflowRepsitory.savedWorkflows[id]
            WorkflowRepsitory.updateSerilalization()
            return True
        except:
            return False


    @staticmethod
    def loadSerilalization():
        if (os.path.exists((WorkflowRepsitory.getWorkflowFile()))):
            with open(WorkflowRepsitory.getWorkflowFile(), 'rb') as f:
                WorkflowRepsitory.savedWorkflows = pickle.load(f)

                temp = WorkflowRepsitory.savedWorkflows
                # handel legacy code, transfer list to dict
                if isinstance(temp,list):
                    WorkflowRepsitory.savedWorkflows = { "next" : len(temp)+1}
                    for i in range(0,len(temp)) :
                        WorkflowRepsitory.savedWorkflows[i] = temp[i]

                    WorkflowRepsitory.updateSerilalization()



WorkflowRepsitory.loadSerilalization()