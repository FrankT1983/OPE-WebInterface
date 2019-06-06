import json

class BlockClass:
    def __init__(self, name, type, id ,inputs, outputs,formInputs,version):
        self.Name = name
        self.Type = type
        self.Id = id
        self.Inputs = inputs
        self.Outputs = outputs
        self.FormInputs = formInputs
        self.Version = version
        self.GitRepo = None
        self.GitFilePath = None

    def getName(self):
        return self.Name

    def dumpList(self,list):
        jsonString = '\t[\n'
        for i in range(len(list)):
            if (i > 0):
                jsonString += ',\n'
            o = list[i]
            if (type(o) is BlockIO) :
                jsonString +=  list[i].to_JSON();

            if (type(o) is dict):
                jsonString += BlockIO.jsonTemplate(o["Id"], o["Value"])

        jsonString += '\n\t]'
        return jsonString

    def to_JSON(self):
        jsonString = '{ \n '                        \
                        '\t\"__type__\": \"JSonBlock\", \n' \
                        '\t\"Type\": \" ' + self.Type + '\", \n' \
                        '\t\"Id\": \" ' + self.Id+ '\", \n' \
                        '\t\"Name\": \" ' + self.Name + '\", \n' \
                        '\t\"Version\": \" ' + self.Version + '\", \n' \
                        '\t\"Outputs\": \n'
        jsonString += self.dumpList(self.Outputs) + ","

        if (not self.GitRepo is None) :
            jsonString +='\t\"GitRepo\": \" ' + self.GitRepo + '\", \n' \
                         '\t\"GitFilePath\": \" ' + self.GitFilePath+ '\", \n' \


        jsonString += '\n\t\"Inputs\": \n'
        jsonString += self.dumpList(self.Inputs)
        jsonString += '\n}';

        jsonString += '\n\t\"FormInputs\": \n'
        jsonString += self.dumpList(self.FormInputs)
        jsonString += '\n}';

        return jsonString

    def SetGitPath(self, gitRepo, gitFilePath):
        self.GitRepo = gitRepo
        self.GitFilePath = gitFilePath
        pass


class BlockIO:
    def __init__(self, value, id):
        self.Value = str(value)
        self.Id = str(id)

    @staticmethod
    def jsonTemplate(id, value):
        return '\t\t{ \n' \
               '\t\t\t\"__type__\": \"JSonBlockIO\", \n' \
               '\t\t\t\"Id\": \"' + id + '\",\n' \
               '\t\t\t\"Value\": \"' + value + ' \" \n' \
               '\t\t}'

    def to_JSON(self):
        return BlockIO.jsonTemplate(self.Id,self.Value)




