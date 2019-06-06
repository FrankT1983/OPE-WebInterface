import traceback

from django.http import HttpResponse
from django.shortcuts import render
from . import PreviewAttachment


import json
from PIL import Image, ImageDraw, ImageFont

import threading

# try to figure out if this is run locally or on a omero server
from OPP.classes.InterfaceFactory import InterfaceFactory
from OPP.classes.LogWriter import LogWriter
from OPP.classes.RunRepo import RunRepository
from OPP.classes.GitHelper import GitHelper

try:
    from omeroweb.webclient.decorators import login_required
    from omero.gateway import BlitzGateway
    import omero
    from OPP.classes.HistoryFromOmero import HistoryFromOmero
    history_getter = HistoryFromOmero()

    InterfaceFactory.useOmero= True
except:
    InterfaceFactory.useOmero = False

    from OPP.classes.FakeHierarchy import FakeHierarchy
    history_getter = FakeHierarchy()

    # mock the login_required attribute
    # not perfect, since each no parameter name has to be added by hand
    def login_required():
        def wrapp1 (func):
            def wrap_for_local_login_required(params, workflowId = None, runId = None, blockId= None, fileId = None , portId = None, datasetId = None, imageId=None):
                return func(params, workflowId= workflowId, runId = runId, fileId = fileId , imageId=imageId
                            , blockId = blockId, portId = portId , datasetId = datasetId)
            return wrap_for_local_login_required
        return wrapp1


from OPP.classes.Decoder import object_decoder
from OPP.classes.WorkflowRepo import WorkflowRepsitory
from OPP.classes.workFlowExecutor import WorkflowExecutor
from OPP.workFlowAnalyser import WorkFlowAnalyser
from OPP.classes.BlockRepo import BlockRepository


def save(request):
    if (request.method == 'POST'):
        data = request.POST['msg']
        WorkflowRepsitory.saveWorkflow(data)
        return HttpResponse("saved")

    return HttpResponse("no Post")

def oppWelcomePage(request):
    return render(request, 'OPP/Welcome.html',
          {
          })

def ViewWorkflows(request):
    list = []
    for i in WorkflowRepsitory.getIds():
        flow = WorkflowRepsitory.getWorkflow(i)
        workflow = json.loads(flow, object_hook=object_decoder)
        if "name" in workflow:
            list.append([ i, workflow["name"]] )
        else :
            list.append([i, None])

    return render(request, 'OPP/View.html',
          {
              'available_workflows': list
          })

def GetAugmentedWorkflow(workflowId):
    worflowJson = WorkflowRepsitory.getWorkflow(workflowId)
    workflow = json.loads(worflowJson, object_hook=object_decoder)

    blocks = workflow["blocks"]
    for b in range(len(blocks)):
        blockType = blocks[b]["blockType"]
        block = BlockRepository.getBlockFromType(blockType)

        if block is None:
            LogWriter.logError("Could get block from Repository: " + str(blockType))
            blocks[b]["Status"] = "not found"
            continue

        inputs = block.Inputs
        inputsList =[]
        for i in range(len(inputs)) :
            inputsList.append( inputs[i].Id)

        outputs = block.Outputs
        outputList = []
        for i in range(len(outputs)):
            outputList.append(outputs[i].Id)

        blocks[b]["Inputs"] = inputsList
        blocks[b]["Outputs"] = outputList

    return workflow

def GetWorkflow(request, workflowId):
    storedWorkflows = WorkflowRepsitory.getIds()
    id = int(workflowId)
    if (not id in storedWorkflows):
        return HttpResponse(json.dumps("unknown id. stored " + str(storedWorkflows) + " vs " + str(id)) ,  content_type="application/json")

    workflow = GetAugmentedWorkflow(workflowId)
    return HttpResponse( json.dumps(workflow), content_type="application/json")

def GetBlock(request, blocktype):
    block = BlockRepository.getBlockFromType(blocktype)

    if (block != None):
        return HttpResponse(block.to_JSON(), content_type="application/json")

    return HttpResponse("", content_type="application/json")

def CreateWorkflow(request):
    blocksFromJson = BlockRepository.getBlocks()
    return render(request, 'OPP/Create.html',
          {
              'available_blocks': blocksFromJson
          })


@login_required()
def PrepareRun(request, workflowId,  conn=None, **kwargs ):
    WorkflowRepsitory.loadSerilalization()

    storedWorkflows = WorkflowRepsitory.getIds()
    id = int(workflowId)
    if (not id in storedWorkflows) :
        return HttpResponse("unknown id. stored " + str(storedWorkflows) +  " vs " + str(id))

    worflowJson = WorkflowRepsitory.getWorkflow(id)

    if (worflowJson == None) :
        return HttpResponse("Workflow empty")

    workflow =  json.loads(worflowJson, object_hook= object_decoder)
    openInputs = WorkFlowAnalyser.CalculateUnconnectedInputs(workflow )

    hiddenInputs = []

    for  i in range(0,len(workflow["blocks"])):
        block = workflow["blocks"][i]
        blockId = block["elementId"]

        if ("inputList" in block):
            for j in range(0, len(block["inputList"])):
                formInputs = block["inputList"][j]
                name = formInputs["id"]
                value = formInputs["value"]
                hiddenInputs.append([blockId , name, value ])

    hist = history_getter.getHierarchyFromAllGroups(conn)

    return render(request, 'OPP/PrepRun.html',
                  {
                      'openInputs' : openInputs ,
                      'workflowId' : workflowId ,
                      'blockPortSeparator' : WorkFlowAnalyser.getBlockPortSeperator(),
                      'hiddenInputs' : hiddenInputs,
                      'full_hierarchy': json.dumps(hist),
                  })

work = []

def JoinSession(conn):
    try:
        LogWriter.logDebug("Connect To:" + str(conn.host) + " " + str(conn.port) + " "  + str(conn._getSessionId()))
        connection = BlitzGateway('OMERO.script', host=conn.host, port=conn.port)
        connection.connect(sUuid=conn._getSessionId())
        return connection
    except Exception as inst:
        LogWriter.logError("Connecting own session failed " + str(inst.message))
        LogWriter.logError(traceback.format_exc())
        return None


@login_required()
def ExecuteRun(request, workflowId,  conn=None, **kwargs ):
    LogWriter.logInfo("####################################################################")
    LogWriter.logInfo("Run Workflow " + workflowId)

    blockPortSeperator = WorkFlowAnalyser.getBlockPortSeperator()

    parameters = []
    versions = []
    recordIntermediates = False;
    #for key, value in request.GET.iteritems():
    for key, value in request.GET.items():
        if key == "intermediates" :
            recordIntermediates = value == "record"
            continue


        blockPort = key.split(blockPortSeperator,2)

        if (blockPort[1] == "Version"):
            versions.append([blockPort[0] ,value])
            continue
        parameters.append([blockPort[0],blockPort[1],value,"in"])

    workflow = GetAugmentedWorkflow(workflowId)
    workflow["parameters"] = parameters
    workflow["intermediates"] = recordIntermediates
    workflow["versions"] = versions
    
    #create own session because the given one will be disconnected
    myConn = JoinSession(conn)       
    WorkflowExecutor.SetConnectionObject(myConn)

    try:
        execution_thread = threading.Thread(target=WorkflowExecutor.StartExcutionOnCluster, args=[workflow])
        execution_thread.start()
        work.append(execution_thread)
        return HttpResponse("started")
    except Exception as inst:
        return HttpResponse("start failed " + str(inst.message))

@login_required()
def ViewResultFile(request, fileId, conn=None, **kwargs):
    WorkflowExecutor.SetConnectionObject(conn)
    workflow = WorkflowExecutor.GetResultFromServer(fileId)


    return render(request, 'OPP/ViewResult.html',
                  {
                      'blockPortSeparator': WorkFlowAnalyser.getBlockPortSeperator(),
                      'workflow': workflow ,
                      'found': not workflow is None,
                  })
    return HttpResponse("view file Id " + fileId)

@login_required()
def ViewWorkResultPreview(request, runId, blockId,portId,datasetId,conn=None, **kwargs ):
    WorkflowExecutor.SetConnectionObject(conn)

    #"intermediate_4e075173-1bd8-4353-8123-1d0d362ccbac_1_Extracted.png"
    expectedName = "intermediate_"+runId + "_" + blockId + "_" + portId
    smallObjectsName = "intermediate_" + runId + "_smallObjects.txt"

    id = -1
    smallObjectsID = -1
    annotationList = WorkflowExecutor.GetDataSetAnnotations(datasetId)

    if (annotationList is None) :
        return PreviewAttachment.RenderTextAndWranInResult("Cannot find attachments of DS " + str(datasetId))

    for i in range(len(annotationList)):
        name = str(annotationList[i][1])
        if name.startswith(expectedName) :
            id = annotationList[i][0]

        if name.startswith(smallObjectsName) :
            smallObjectsID = annotationList[i][0]


    # no dedicated file, maybe in small objects
    if (smallObjectsID > 0):
        name, data = PreviewAttachment.GetAnnotationFileFromServer(conn, smallObjectsID)
        smallObjectsDic = json.loads(data)
        expectedKey = blockId + "_" + portId
        if (expectedKey in smallObjectsDic):
            return PreviewAttachment.RenderTextAndWranInResult(smallObjectsDic[expectedKey])

    if (id == -1):
        return PreviewAttachment.RenderTextAndWranInResult("Not Found")

    return PreviewAttachment.preview_file(id,conn)

@login_required()
def ViewRunStatistics(request, runId, datasetId,conn=None, **kwargs ):
    WorkflowExecutor.SetConnectionObject(conn)
    annotationList = WorkflowExecutor.GetDataSetAnnotations(datasetId)

    if (annotationList is None):
        return render(request, 'OPP/ViewRunStatistics.html',
                      { 'found': False})

    statisticsFileId = -1
    expectedName = "statistics_" + runId + "_statistics.txt"
    for i in range(len(annotationList)):
        name = str(annotationList[i][1])
        if name.startswith(expectedName):
            statisticsFileId = annotationList[i][0]

    if (statisticsFileId < 0):
        return render(request, 'OPP/ViewRunStatistics.html',
                      {'found': False})

    name, data = PreviewAttachment.GetAnnotationFileFromServer(conn, statisticsFileId)

    return render(request, 'OPP/ViewRunStatistics.html',
          {
              'found': True,
              'StatisticsData' : data
          })


def GetGitVersions(request,gitUrl, gitPath):

    LogWriter.logInfo("GetGitVersions    " + str(gitUrl) + " " + str(gitPath))
    res = {}
    try:
        commits = GitHelper.getCommits(gitUrl,gitPath)
    except Exception as e:
        import traceback
        LogWriter.logError(e.message)
        LogWriter.logError(traceback.format_exc())
    res["commits"] = commits
    return HttpResponse(json.dumps(res), content_type="application/json")


def ViewRunOverview(request):
    dict = RunRepository.getRuns()
    list = dict.items()
    sortedList = sorted(list, key=lambda entry: entry[1][1], reverse=True)    # sort by date

    return render(request, 'OPP/ViewRunOverview.html',
          {
              'runs': sortedList
          })

@login_required()
def DeleteWorkflow(request, workflowId,  conn=None, **kwargs ):
    if (WorkflowRepsitory.deleteWorkflow(workflowId)):
        return HttpResponse("deleted")
    else:
        return HttpResponse("error deleting")

@login_required()
def GetFileStructure(request, conn=None, **kwargs ):
    result = {}
    if (conn is None):
        return HttpResponse(json.dumps(result), content_type="application/json")



    return HttpResponse(json.dumps(result), content_type="application/json")


@login_required()
def getThumbAddress(request,imageId , conn=None, **kwargs ):
    url = history_getter.getThumbNail(conn,imageId)
    return HttpResponse(url)