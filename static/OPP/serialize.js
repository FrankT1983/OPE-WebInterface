function serialize (plumbInstance, canvas, name)
{
    const connections = plumbInstance.getConnections();

    var links = []
    for( c =0; c < connections.length; c++ )
    {
        var con = connections[c]
        var params = con.getParameters();
        var test = {
                        targetBlock: con.targetId,
                        targetPort : params["targetLabel"],     // needed to preserve the script
                        sourceBlock: con.sourceId,
                        sourcePort: params["sourceLabel"],       // needed to preserve the script

                        // needed for jsplumb to connect correctly
                        // see: http://stackoverflow.com/questions/20620719/save-and-load-jsplumb-flowchart-including-exact-anchors-and-connections
                        anchors: $.map(con.endpoints, function(endpoint) {
                                return [[endpoint.anchor.x,
                                         endpoint.anchor.y,
                                         endpoint.anchor.orientation[0],
                                         endpoint.anchor.orientation[1],
                                         endpoint.anchor.offsets[0],
                                         endpoint.anchor.offsets[1]]];
                                })
                        };
        links.push(test);
    }

    var blocks = []

    canvas.each(function (idx, elem) {
        var $elem = $(elem);

        var inputs= $elem.find("input")

        var inputList =[];
        for ( i=0 ; i< inputs.length ; i++)
        {
            inputList.push( { id :inputs[i].id, value : inputs[i].value })
        }

        blockDict = {
            elementId : $elem.attr('id'),
            blockId: $elem.attr('data-block-id'),
            blockName: $elem.attr('data-block-name'),
            blockType: $elem.attr('data-block-type'),
            positionX: parseInt($elem.css("left"), 10),
            positionY: parseInt($elem.css("top"), 10),
            inputList: inputList
        };

        if ($elem.attr("data-git-Repo"))
        {
            blockDict["GitRepo"] = $elem.attr('data-git-Repo')
            blockDict["GitFilePath"] = $elem.attr('data-git-Path')
        }

        blocks.push(blockDict);
    });

    var graph = { name : name, blocks : blocks , links: links }

    return JSON.stringify(graph);
}

function drawFromInstance (graph)
{
    var index
    drawBlocks(graph)
    connectBlocks(graph)
}


function deSerialize (jsonUrl, blockUrl,gitVersionsUrl)
{
    var resultData
    var graph
    return $.getJSON(jsonUrl, function(result)
        {
            graph = result
            if ("unknown" in result)
            {
                alert(result);
                graph = ""
            }

        }).then
        (function()
        {
            if (graph == "")
                return;
           drawBlocks(graph,gitVersionsUrl)
           connectBlocks(graph)
         });
}

loadedConnections = []

function drawBlocks(graph,gitVersionsUrl)
{
    for( index in graph.blocks)
    {
        var block = graph.blocks[index]

        outputs = []
        try
        {
            for (i  = 0 ; i<block.Outputs.length; i++ )
            {
                outputs.push(block.Outputs[i]);
            }
        }catch (e)
        {
        }

        inputs = []
        try
        {
            for (i  = 0 ; i<block.Inputs.length; i++ )
            {
                inputs.push(block.Inputs[i]);
            }
        }catch (e)
        {
        }

        formInputs =[];
        try
        {
            for (i  = 0 ; i<block.inputList.length; i++ )
            {
                formInputs.push(block.inputList[i]);
            }
        }catch (e)
        {
        }

        invalidBlock = false
        if ("Status" in block)
        {
            invalidBlock = block["Status"] == "not found"
        }

        versions = []
        if (gitVersionsUrl && block.GitRepo)
        {
            url = gitVersionsUrl.replace("gitUrlReplace",  encodeURIComponent(block.GitRepo)).replace("gitPathReplace", encodeURIComponent(block.GitFilePath))
            // synchronous. i know this is deprecated, but don't want to go throught the trouble of creating a closure here
            $.ajax({
                url : url,
                 dataType: 'json',
                 async: false,
                 success: function(data) {
                    for (d in data.commits)
                    {
                        versions.push(data.commits[d])
                    }
                }
            });
        }

        blockElement = createBlock(block.elementId,block.blockName,block.blockId, block.blockType, inputs, outputs, formInputs , block.positionX , block.positionY, true, false,invalidBlock, versions)
    }
}

function connectBlocks(graph)
{
    links = graph.links;
    for (l=0; l<links.length;l++)
    {
        currentLink = links[l];

        sourceBlock = $("#" + currentLink.sourceBlock)
        targetBlock = $("#" + currentLink.targetBlock)
        if ((sourceBlock.exists()) && (targetBlock.exists()))
        {

            linkHash = currentLink.sourceBlock + "|" + currentLink.sourcePort+ "|" + currentLink.targetBlock+ "|" + currentLink.targetPort;
            if (loadedConnections.findIndex(function(s) { return s == linkHash })> -1)
                continue;

            loadedConnections.push(linkHash)


            var connection1 = instance.connect({
                    source: currentLink.sourceBlock,
                    target: currentLink.targetBlock,
                    anchors: currentLink.anchors,
                    paintStyle : connectorPaintStyle,
                    connector: myFlowChartConnector,
                    // connecting this way will not get the endpoints and thus their parameters as I do in the creation
                     // web page => use parameters on the connection to preserver that information
                     parameters:
                     {
                        "sourceBlock":currentLink.sourceBlock,
                        "sourcePort":currentLink.sourcePort,
                        "targetBlock":currentLink.targetBlock,
                        "targetPort":currentLink.targetPort,
                     }
            });
        }
    }
}

function clearCanvas()
{
    instance.reset();
    loadedConnections = [];
    $("#jsPlumbCanvas").empty()
}

$.fn.exists = function () {
    return this.length !== 0;
}