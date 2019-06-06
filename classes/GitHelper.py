import git
import tempfile
import platform

from OPP.classes.LogWriter import LogWriter
import traceback
import time
from cachetools import TTLCache


class GitHelper :

    @staticmethod
    def checkAndModifyGitUrl(origpaht):
        git_url = origpaht
        if (not "github" in git_url):
            git_url = git_url.replace("https://", "git@")
            git_url = git_url.replace(".de/",
                                      ".de:")  # todo: this is a hack deconstruct old thing with regex and build new path
        return git_url

    @staticmethod
    def getCommitsInternal(concatPath):
        tmp = concatPath.split(GitHelper.seperatro,2)
        git_url = tmp[0]
        file_path = tmp[1]
        LogWriter.logInfo("System:  " + str(platform.system()))
        if (platform.system() == 'Windows'):
            # under my windows debug environment git does not work, since it does not use ssh
            #  return debug fill stuff
            return [[1,"just a test"],[2, "bar"],[3, "foo"]]

        try :
            repo_dir = tempfile.mkdtemp()
            git_url = GitHelper.checkAndModifyGitUrl(git_url)
            repo = git.Repo.clone_from(git_url, repo_dir)

            g = git.Git(repo_dir)
            commits = g.log("--follow", '--pretty=format:"%H - %an, %ar : %s', file_path).split("\n")
            result = []
            for c in commits:
                rev = c.split("-")[0].strip().replace("\"", "")
                other = c.split("-")[1].strip().replace("\"", "")
                result.append([rev, other])

            return result
        except Exception as e:
            LogWriter.logError("getCommits failed: " + e.message)
            LogWriter.logError(traceback.format_exc())
            return []


    commitCache = TTLCache(maxsize=4,missing=getCommitsInternal, ttl=60)
    seperatro =":||:"

    @staticmethod
    def getCommits(git_url, file_path):
        path=git_url+GitHelper.seperatro+file_path
        if not path in GitHelper.commitCache:
            GitHelper.commitCache[path] = GitHelper.getCommitsInternal(path)
        return GitHelper.commitCache[path]

    @staticmethod
    def getFileStringFromRevision(git_url, file_path,rev):
        if (platform.system() == 'Windows'):
            return GitHelper.getWindowsFallbackString(file_path)
        repo_dir = tempfile.mkdtemp()
        git_url = GitHelper.checkAndModifyGitUrl(git_url)
        repo = git.Repo.clone_from(git_url, repo_dir)
        g = git.Git(repo_dir)
        return g.execute(["git", "show", str(rev) + ":" + str(file_path)])

    @staticmethod
    def getFileFromRevision(git_url, file_path, rev):
        if (platform.system() == 'Windows'):
            return GitHelper.getWindowsFallback(file_path)

        repo_dir = tempfile.mkdtemp()
        git_url = GitHelper.checkAndModifyGitUrl(git_url)
        repo = git.Repo.clone_from(git_url, repo_dir)
        repo.git.checkout(rev)

        #name = GitHelper.repoNameFromUrl(git_url)
        #pathToFile = repo.git.working_dir + "/" + name  + "/" + file_path
        pathToFile = repo.git.working_dir + "/" + file_path
        LogWriter.logDebug("Path to local file from git: " + pathToFile)
        return pathToFile


    @staticmethod
    def getWindowsFallbackString( file_path):
        windowsBackupFileFolder = "C:/PHD/UnitTest/GitBackup/"
        path = windowsBackupFileFolder + file_path
        with open(path, 'r') as myfile:
            return myfile.read()

    @staticmethod
    def getWindowsFallback( file_path):
        windowsBackupFileFolder = "C:/PHD/UnitTest/GitBackup/"
        return windowsBackupFileFolder + file_path

    @staticmethod
    def repoNameFromUrl( git_url):
        parts = str(git_url).split("/")
        last = parts[len(parts)-1]
        return last.replace(".git","")
