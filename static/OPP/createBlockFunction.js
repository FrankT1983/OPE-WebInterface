 var nextId = 5;

 function removeBlock()
 {
 console.log("remove  " + 5+ " ");
 }


function createBlock(elementId,name,id, type, inputs, outputs, formInputs , x , y, draggable ,deletable, invalid, versions)
{
    var iDiv = document.createElement('div');
    iDiv.id = elementId;

    iDiv.setAttribute("data-block-id" ,id )
    iDiv.setAttribute("data-block-name" ,name )
    iDiv.setAttribute("data-block-type" ,type )

    if (deletable)
    {
        var deleteButton = document.createElement("button")
        deleteButton.innerText = "x"
        deleteButton.onclick= function temp(elementId_Copy)
        {
         return function()
            {
                console.log("remove  " + elementId_Copy+ " ");
                idString = ""+elementId_Copy + "";
                instance.detachAllConnections(idString);
                instance.removeAllEndpoints(idString);
                instance.detach(idString);
                iDiv.remove()
            }
        }(elementId)

        iDiv.appendChild(deleteButton)
    }

    iDiv.className = 'window jtk-node';
    var t = document.createTextNode(name);
    iDiv.appendChild(t)

    if (invalid)
    {
        iDiv.style.backgroundColor = "red"
    }

    iDiv.style.position = "absolute";
    iDiv.style.left  = x +'px' ;
    iDiv.style.top  = y+'px';

    iDiv.style.height = Math.max(80, 34 * Math.max(inputs.length,outputs.length)) + 'px';

    document.getElementById("jsPlumbCanvas").appendChild(iDiv);

    if (formInputs.length > 0)
    {
        var table= document.createElement("table")
        iDiv.appendChild(table)

        for ( i=0; i<formInputs.length;i++)
        {
            var row = document.createElement("tr")

            var data =  formInputs[i];

            var label = document.createElement("td")
            var text = document.createElement("b")
            if (typeof data === "string"  )
            {
                text.innerHTML = data    
            }
            else
            {
                text.innerHTML = data.id
            }
            
            label.appendChild(text);
            row.appendChild(label);

            var input = document.createElement("td")
            var text = document.createElement("input")
            text.type = "text"
            if (typeof data === "string"  )
            {
                text.id = data;
            }
            else
            {
                text.id = data.id;
                text.value = data.value;
            }

            if (!deletable)
            {
                text.disabled = true;   
            }

            input.appendChild(text);
            row.appendChild(input);

            table.appendChild(row)
        }
    }

    if (versions && versions.length>0)
    {
        var versionSelect = document.createElement('select');
        versionSelect.id = "VersionSelect"
        iDiv.appendChild(versionSelect)

        for ( i=0; i<versions.length;i++)
        {
            var data = versions[i];
            var entry = document.createElement('option');
            entry.label = data[1]
            entry.textContent = data[1]
            entry.value = data[1]
            entry.setAttribute("commit_hash" , data[0] )
            versionSelect.appendChild(entry)
        }

        $(versionSelect).selectmenu({style:'popup'});
    }

    ////////////////////////////////////////////////////////////////////////
    // do everything that changes the size of the div before this point !!
    ////////////////////////////////////////////////////////////////////////

    if (draggable)
    {
        instance.draggable(iDiv);
    }

    var increment = 1 / (inputs.length + 1)
    var current =  increment;
    for ( i=0; i<inputs.length;i++)
    {
        input = inputs[i]
        maxCons = -1
        // hack: The load Image block can only be used at the beginning of a workflow, since the image
        // download has to be done via the djange/web part
        // (the workflow executor on the cluster can not guarantee that a given working node has access to the omero)
        //  (( Discuss advantages and disadvantages ?? : More secure, but delays start  ))
        if (name === "OmeroImage")
        {
            maxCons = 0
        }

        instance.addEndpoint(iDiv, createTargetPoint(input,maxCons),
                {   anchor: [ 0, current, -1, 0 ],
                    uuid: iDiv.id+input,
                    paintStyle:{ fillStyle:"blue", outlineColor:"black", outlineWidth:1 }});
        current += increment
    }

    increment = 1 / (outputs.length + 1)
    current =  increment;

    for ( i=0; i<outputs.length;i++)
    {
        output = outputs[i]
        point = instance.addEndpoint(iDiv, createSourcePoint(output),
               { anchor: [ 1, current, 1, 0 ], uuid: iDiv.id+output });
        current += increment
    }

     return iDiv
}
