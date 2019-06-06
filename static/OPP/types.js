
var basicType = {
        connector: "StateMachine",
        paintStyle: { strokeStyle: "red", lineWidth: 4 },
        hoverPaintStyle: { strokeStyle: "blue" },
        overlays: [
            "Arrow"
        ]
    };

    // this is the paint style for the connecting lines..
    var connectorPaintStyle = {
            lineWidth: 4,
            strokeStyle: "#61B7CF",
            joinstyle: "round",
            outlineColor: "white",
            outlineWidth: 2
        },
    // .. and this is the hover style.
        connectorHoverStyle = {
            lineWidth: 4,
            strokeStyle: "#216477",
            outlineWidth: 2,
            outlineColor: "white"
        },
        endpointHoverStyle = {
            fillStyle: "#216477",
            strokeStyle: "#216477"
        }

var myFlowChartConnector = [ "Flowchart", { stub: [40, 60], gap: 10, cornerRadius: 5, alwaysRespectStubs: true } ]




    function createTargetPoint(label, maxConns)
            {
                var result =
                {
                    endpoint: "Dot",
                    paintStyle: { fillStyle: "#7AB02C", radius: 11 },
                    hoverPaintStyle: endpointHoverStyle,
                    maxConnections: maxConns,
                    dropOptions: { hoverClass: "hover", activeClass: "active" },
                    isTarget: true,
                    id:label,
                    parameters:{
                        "targetLabel" : label
                    },
                    overlays:
                    [
                         [ "Label", { location: [1, 1.5], label: label, cssClass: "endpointTargetLabel", visible:true } ]
                    ]
                }

                return result;
            }

    function createSourcePoint(label)
            {
                 result = {
                    id:label,
                    endpoint: "Dot",
                    paintStyle: {
                        strokeStyle: "#7AB02C",
                        fillStyle: "transparent",
                        radius: 7,
                        lineWidth: 3
                    },
                    maxConnections: -1,
                    isSource: true,
                    connector: myFlowChartConnector,
                    connectorStyle: connectorPaintStyle,
                    hoverPaintStyle: endpointHoverStyle,
                    connectorHoverStyle: connectorHoverStyle,
                    dragOptions: {},
                    parameters:{
                        "sourceLabel" : label
                    },
                    overlays: [
                        [ "Label", {
                            location: [1, 1.5],
                            label: label,
                            cssClass: "endpointSourceLabel",
                            visible:true
                        } ]
                    ]
                }

                return result;
            }