from OPP.classes.BlockRepo import BlockRepository
from OPP.classes.LogWriter import LogWriter


class WorkFlowAnalyser:
    @staticmethod
    def CalculateUnconnectedInputs(graphDic):
        blocks = graphDic["blocks"]
        links = graphDic["links"]

        allInputs = []

        for b in range(len(blocks)):
            try:
                currentBlock  = blocks[b]
                blockType = currentBlock['blockType']
                id = currentBlock['elementId']
                block = BlockRepository.getBlockFromType(blockType)
                if (block is None):
                    LogWriter.logError("Could retreve block from Repository: " + str(blockType))
                    continue
                inputs = block.Inputs

                special = ""

                if (block.Id == "OmeroImage"):
                    special = "image"
                if (block.Id == "OmeroImageSaveToDataSet"):
                    special = "dataset"


                for i in range(len(inputs)):
                    allInputs.append([id, inputs[i].Id, special])
            except:
                LogWriter.logError("Could not get get ports of block: " + str(blockType))

        # filter all inputs that are a destination of a link
        for l in range((len(links))):
            currentLink = links[l]
            tuple = [currentLink['targetBlock'],currentLink['targetPort']]
            for rem in range((len(allInputs))):
                if (allInputs[rem][0] == tuple[0] and allInputs[rem][1] == tuple[1]):
                    allInputs.pop(rem)
                    break

        return allInputs

    @staticmethod
    def getBlockPortSeperator ():
        return "-_-_-"


    @staticmethod
    def IsBlockForLoadingImage(block):
        loadImageBlockType = "plugins.Frank.de.c3e.ProcessManager.OmeroImageInputBlock"
        return block['blockType'] == loadImageBlockType

    @staticmethod
    def GetParametersForBlock(block,workflowAndParameterDic):
        parameters = workflowAndParameterDic["parameters"]
        for paramI in range(len(parameters)):
            if ((parameters[paramI][0] == block['elementId'])):
                return parameters[paramI]
        return None


    @staticmethod
    def GetRequiredImageIdsFromWorkflow(workflowAndParameterDic):
        result = []
        blocks = workflowAndParameterDic["blocks"]

        loadImageBlockIdInput = "ImageId"
        for b in range(len(blocks)):
            currentBlock = blocks[b]
            if not(WorkFlowAnalyser.IsBlockForLoadingImage(currentBlock)):
                continue

            curPar = WorkFlowAnalyser.GetParametersForBlock(currentBlock,workflowAndParameterDic)
            if curPar is None:
                continue

            # figure out the input of this load block
            if ((curPar[1] == loadImageBlockIdInput)):
                result.append(curPar)
                break
        return result

    @staticmethod
    def GetRequiredFileIdsFromWorkflow(workflowAndParameterDic):
        result = []
        blocks =  workflowAndParameterDic["blocks"]
        parameters = workflowAndParameterDic["parameters"]

        loadImageBlockType = "OmeroTextFileInputBlock"
        loadImageBlockIdInput = "FileId"

        for b in range(len(blocks)):
            currentBlock = blocks[b]
            if (not( currentBlock['blockType'] == loadImageBlockType)):
                continue

            # figure out the input of this load block
            for paramI in range(len(parameters)):
                if ((parameters[paramI][0] == currentBlock['elementId']) and (parameters[paramI][1] == loadImageBlockIdInput)) :
                    result.append( parameters[paramI])
                    break
        return result

    @staticmethod
    # find Result images => Data Set
    # find all the result images that have to be added to a data set
    def GetImageUploadsFromWorkflow(workflowAndParameterDic):
        result = []
        blocks =  workflowAndParameterDic["blocks"]
        parameters = workflowAndParameterDic["parameters"]

        saveImageBlockType = "plugins.Frank.de.c3e.ProcessManager.OmeroImageSaveToDataSet"
        dataSetId = "DataSet Id"

        for b in range(len(blocks)):
            currentBlock = blocks[b]
            if (not( currentBlock['blockType'] == saveImageBlockType)):
                LogWriter.logInfo("Checked block " + str(currentBlock['blockType']))
                continue

            LogWriter.logInfo("Found block " + str(currentBlock['blockType']))
            # figure out the data set parameter
            for paramI in range(len(parameters)):
                if ((parameters[paramI][0] == currentBlock['elementId']) and (parameters[paramI][1] == dataSetId)) :
                    result.append(parameters[paramI])
                    break

        return result

    @staticmethod
    # find result file => image
    # find all the result files that have to be annotate to an image
    def GetImagesToAnnotateFromWorkflow(workflowAndParameterDic):
        result = []
        blocks =  workflowAndParameterDic["blocks"]
        parameters = workflowAndParameterDic["parameters"]

        annotateImageBlockType = "AnnotateImageWithData"
        parameterName = "ImageId"

        for b in range(len(blocks)):
            currentBlock = blocks[b]
            if (not( currentBlock['blockType'] == annotateImageBlockType)):
                continue

            # figure out the parameter that has to be passed through the parameter file
            for paramI in range(len(parameters)):
                if ((parameters[paramI][0] == currentBlock['elementId']) and (parameters[paramI][1] == parameterName)) :
                    result.append( parameters[paramI])
                    break

        return result


    @staticmethod
    def ReplaceImageIdParametersWithFileNames(workflowAndParameterDic, imageIds):
        parameters = workflowAndParameterDic["parameters"]
        for paramI in range(len(parameters)):
            for imageI in range(len(imageIds)) :
                if (parameters[paramI][0] == imageIds[imageI][0] ):
                    parameters[paramI][1] = "Value"
                    parameters[paramI][2] = imageIds[imageI][3]

        pass

    @staticmethod
    def MergeReproducibilityParameters(unmodiviedParams, imageIds):
        parameterNameImages = "ImageId"
        for i  in range(len(unmodiviedParams)):
            # [0] : Block ID
            # [1] : Port Name
            # [2] : value
            # [3] : port type
            LogWriter.logInfo("Parameter: " + str(unmodiviedParams[i]))
            if (unmodiviedParams[i][1] == parameterNameImages ):
                LogWriter.logInfo(" Is input image")
                # find corresponding parameter
                for j  in range(len(imageIds)):

                    LogWriter.logInfo(" Check corresponding " + str(imageIds[j]))

                    if len(imageIds[j])< 6:
                        continue

                    if not str(imageIds[j][5]).startswith("OMERO ID"):
                        continue

                    splits = str(imageIds[j][5]).split(":",2);
                    if not len(splits) is 2:
                        LogWriter.logInfo(" Not enough splitts")
                        continue

                    if (str(unmodiviedParams[i][2]).strip() ==  splits[1].strip()):
                        unmodiviedParams[i].append(imageIds[j][4])
                    else:
                        LogWriter.logInfo(" Missmatch \"" + str(unmodiviedParams[i][2])+ "\" \"" +splits[1] + "\"")

                    LogWriter.logInfo(" Modified " + str(unmodiviedParams[i]))
        return
