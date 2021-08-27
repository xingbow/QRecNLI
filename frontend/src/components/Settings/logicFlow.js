/* global $*/
import LogicFlow from '@logicflow/core';
import '@logicflow/core/dist/style/index.css';


export function createLogicFlowConfig({
    containerId,
    nodeClickCallback
}) {

    const flowchartConfig = {
        height: 630,
        betweenNodeDistance: 50,
        rect: {
            radius: 5,
            height: 25,
            width: 0.9 * $("#" + containerId).width(),
            fill: "white", //'#87CEFA',
            stroke: '#1E90FF',
            strokeWidth: 0.5,
            class: "logic-flow-rect",
        },
        nodeText: {
            fontSize: 12,
        },
        line: {
            stroke: '#1E90FF',
            strokeWidth: 0.5,
            strokeDashArray: '1,0',
            hoverStroke: '#1E90FF',
            selectedStroke: '#1E90FF',
            selectedShadow: true,
            outlineColor: '#1E90FF',
            outlineStrokeDashArray: '3,3',
        },
    }

    const lf = new LogicFlow({
        container: document.querySelector('#logicFlow'),
        stopScrollGraph: true,
        stopZoomGraph: true,
        width: $("#" + containerId).width(),
        height: flowchartConfig["height"],
        background: {
            opacity: 0.2,
            color: "lightgray"
        },
        keyboard: {
            enabled: true
        },
        // tool config
        textEdit: true,
        isSilentMode: false,
        edgeType: 'line',
        snapline: true,
        // style config
        style: {
            rect: flowchartConfig["rect"],
            nodeText: flowchartConfig["nodeText"],
            line: flowchartConfig["line"]
        },
        adjustNodePosition: false,
        stopMoveGraph: true
    });
    // --- listen to users' interactions
    // lf.on('history:change', (eventObject) => {
    //     console.log("eventObject: ", eventObject);
    // });

    lf.on('node:click', (eventObject) => {
        console.log("click", eventObject)
        if (nodeClickCallback)
            nodeClickCallback(eventObject);
    });

    lf.on('node:dbclick', (eventObject) => {
        console.log("dbclick", eventObject)
    });


    return { 'flowchartConfig': flowchartConfig, 'lf': lf };
}

export function renderLogicFlowChart(historyData, containerId = "logicFlowContainer", nodeClickCallback = undefined) {
    const nodeData = [];
    const edges = [];
    const { flowchartConfig, lf } = createLogicFlowConfig({ containerId, nodeClickCallback })
    historyData.map((h, hi) => {
        // console.log(hi, h);
        nodeData.push({
            id: hi.toString(),
            type: 'rect',
            x: 1 / 2 * $("#" + containerId).width(),
            y: flowchartConfig["betweenNodeDistance"] * (hi + 1),
            text: h["nl"]
        });
        // --- draw edges
        if (hi - 1 >= 0) {
            edges.push({
                type: 'line',
                sourceNodeId: (hi - 1).toString(),
                targetNodeId: hi.toString(),
            });
        }
    });

    lf.render({
        nodes: nodeData,
        edges: edges,
    });
    // -- handle overflow
    if (flowchartConfig["betweenNodeDistance"] * (historyData.length + 1) >= flowchartConfig["height"]) {
        $(".lf-graph").css("height", flowchartConfig["betweenNodeDistance"] * (historyData.length + 1) + "px")
    }
}