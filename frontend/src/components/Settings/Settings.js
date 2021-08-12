/* global $*/
import vSelect from 'vue-select'
import 'vue-select/dist/vue-select.css';
import dataService from '../../service/dataService';
import Tabulator from 'tabulator-tables';

import "../../assets/historyQuery.css"

import LogicFlow from '@logicflow/core';
import '@logicflow/core/dist/style/index.css';
import pipeService from '../../service/pipeService';

export default {
    name: 'Settings',
    components: {
        vSelect,
    },
    props: {
        tableLists: Array,
        tables: {},
    },
    data() {
        return {
            containerId: "settingsContainer",
            tabselected: "",
            tableCols: [],
            historyData: [],
            activeIdx: 0,
            // TODO: organize metadata in tree layout
            treedata: [],
            defaultProps: {
                children: 'children',
                label: 'label'
            }
        }
    },
    watch: {
        tables: function(tables){
            console.log("table changed in Setting View:", tables);
            let tableL = []; 
            for (const [key, value] of Object.entries(tables)) {
                // console.log(key, value);
                let children = value.map(v=>{return {"label": v[0]} });
                tableL.push({
                    "label": key,
                    "children": children,
                });
            }
            console.log("tableList: ", tableL);
            this.treedata = tableL;

        },
        tabselected: function(tabselected) {
            if (tabselected.length > 0) {
                console.log("select table:", tabselected);
                dataService.getTableCols(tabselected, data => {
                    console.log("columns: ", data["data"]);
                    let tableCols = data["data"];
                    dataService.loadTablesContent(tabselected, (data) => {
                        this.tableCols = tableCols
                        this.dataTable.setData(data["data"].slice(0, (data["data"].length >= 5) ? 5 : data["data"].length));
                    })
                })
            }
        }
    },
    methods: {
        onAfterChange(obj) {
            console.log("after update: ", obj.item.itemMap);
        },
        setActive(){
            this.activeIdx = Math.pow((this.activeIdx - 1), 2)
            $(`.nav-link`).removeClass("active");
            $(`.nav-link-`+this.activeIdx).addClass("active");
        },
        handleNodeClick(data) {
            console.log(data);
        },
    },
    mounted: function() {
        console.log("this is settings view");
        $('.nav-link-'+this.activeIdx).addClass("active");
        // 1. initialize table
        this.dataTable = new Tabulator("#data-table", {
            autoColumns: true, //create columns from data field names
            // pagination:"local",       //paginate the data
            // paginationSize:5,
        });
        // 2. draw flowchart
        let flowchartConfig = {
            height: 630,
            betweenNodeDistance: 50,
            rect: {
                radius: 5,
                height: 25,
                width: 0.9 * $("#" + this.containerId).width(),
                fill: "white", //'#87CEFA',
                stroke: '#1E90FF',
                strokeWidth: 0.5,
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
            width: $("#" + this.containerId).width(),
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
        });
        // --- listen to users' interactions
        lf.on('history:change', (eventObject) => {
            console.log("eventObject: ", eventObject);
        });

        pipeService.onSQL(sql => {
            this.historyData.push(sql);
            let nodeData = [],
                edges = [];
            this.historyData.map((h, hi) => {
                console.log(hi, h);
                nodeData.push({
                    id: hi.toString(),
                    type: 'rect',
                    x: 1 / 2 * $("#" + this.containerId).width(),
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
            if (flowchartConfig["betweenNodeDistance"] * (this.historyData.length + 1) >= flowchartConfig["height"]) {
                $(".lf-graph").css("height", flowchartConfig["betweenNodeDistance"] * (this.historyData.length + 1) + "px")
            }
        })

    }
}