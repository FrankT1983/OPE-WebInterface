from OPP.classes.block import BlockClass, BlockIO

def object_decoder(obj):
    if '__type__' in obj and obj['__type__'] == 'JSonBlock':

        formInputs = []
        if ('FormInputs' in obj):
            formInputs = obj['FormInputs']

        version = "latest"
        if ('Version' in obj):
            version = obj['Version']

        gitRepo = ""
        gitFilePath = ""
        if ('GitRepo' in obj):
            gitRepo = obj['GitRepo']

            if ('GitFilePath' in obj):
                gitFilePath = obj['GitFilePath']

        block = BlockClass(obj['Name'],obj['Type'],obj['Id'], obj['Inputs'],obj['Outputs'],formInputs,version)
        block.SetGitPath(gitRepo,gitFilePath)
        return block

    if '__type__' in obj and obj['__type__'] == 'JSonBlockIO':
        return BlockIO(obj['Value'],obj['Id'])

    return obj