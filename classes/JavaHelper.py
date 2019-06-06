from OPP.classes.GitHelper import GitHelper
import tempfile
import os.path
from subprocess import check_output
import platform
from OPP.classes.LogWriter import LogWriter

class JavaHelper :
    @staticmethod
    def compileOrGetFromCache(git_url,file_path,rev , name):
        scriptFile = JavaHelper.getCompileShellScript()
        if scriptFile is None:
            return None

        code = GitHelper.getFileStringFromRevision(git_url, file_path, rev)

        compileFolder = tempfile.mkdtemp()
        sourceFileName =  compileFolder + "/" + name
        with open(sourceFileName, "w") as text_file:
            text_file.write(code)

        # strip the .java extention
        name = name.replace(".java", "")

        params = [scriptFile, sourceFileName, compileFolder, name]
        LogWriter.logDebug("Call Compiler: " + str(params))
        try:
            compileOut = check_output(params)
        except Exception as e:
            import traceback
            LogWriter.logError(e.message)
            LogWriter.logError(traceback.format_exc())
            LogWriter.logError(compileOut)

        LogWriter.logDebug("Compiler out: " + compileOut)

        resultpath = compileFolder + "/" + name + ".jar"
        LogWriter.logDebug("Should have compiled to: " + str(resultpath))
        if os.path.isfile(resultpath) and os.path.exists(resultpath):
            return os.path.abspath(resultpath)
        LogWriter.logDebug("Not Found: " + str(resultpath) + " \n Compiler output:\n" + str(compileOut))
        return None

    @staticmethod
    def checkForToolDependencies(jarPath):
        cliTool = "GetSourceControlInfo.jar"
        if not os.path.isfile(cliTool):
            return None

        LogWriter.logDebug("Absolut Path to tool tool: " + str(os.path.abspath(cliTool)))

        import subprocess
        consoleOut = check_output(['java', '-jar', cliTool, jarPath])
        lines = consoleOut.strip().split("\n")

        LogWriter.logDebug("Tool Console out: " + str(consoleOut))

        result = []
        for line in lines:
            parts = line.strip().split("::",5)
            if (len(parts)<4):
                continue

            result.append(parts)
        return result

    @staticmethod
    def getToolFromVersionControl(classname, version_control_system, repo, path, checkin):
        if not version_control_system.lower() == "GIT".lower():
            return

        return GitHelper.getFileFromRevision(repo,path,checkin)



    @staticmethod
    def getCompileShellScript():
        defaultScript = "compileJar.sh"
        if (platform.system() == 'Windows'):
            defaultScript ="compileJar.bat"

        LogWriter.logDebug("Absolut Path to Compile Script: " + str(os.path.abspath(defaultScript)))
        if os.path.isfile(defaultScript) and os.path.exists(defaultScript):
            return os.path.abspath(defaultScript)

        LogWriter.logError("could not find compile script. Create it: " + defaultScript )
        file = open(defaultScript, 'w+')
        file.close()
        return None

