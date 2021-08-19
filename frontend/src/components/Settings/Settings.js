/* global $*/
import vSelect from 'vue-select'
import 'vue-select/dist/vue-select.css';
import dataService from '../../service/dataService';
// import Tabulator from 'tabulator-tables';

import "../../assets/historyQuery.css"

import '@logicflow/core/dist/style/index.css';
import pipeService from '../../service/pipeService';
import {renderLogicFlowChart} from './logicFlow'

export default {
    name: 'Settings',
    components: {
        vSelect,
    },
    props: {
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
                label: 'label',
            },
            rightButtonVisible: false,

        }
    },
    watch: {
        tables: function (tables) {
            console.log("table changed in Setting View:", tables);
            let tableL = [];
            for (const [key, value] of Object.entries(tables)) {
                // console.log(key, value);
                const children = value.map(v => { return { "type": "column", "label": v[0], "ctype": v[1] } });
                tableL.push({
                    "type": "table",
                    "label": key,
                    "children": children,
                });
            }
            console.log("tableList: ", tableL);
            this.treedata = tableL;

        },
        tabselected: function (tabselected) {
            if (tabselected.length > 0) {
                console.log("select table:", tabselected);
                dataService.getTableCols(tabselected, data => {
                    const tableCols = data;
                    dataService.loadTablesContent(tabselected, (data) => {
                        this.tableCols = tableCols
                        this.dataTable.setData(data.slice(0, (data.length >= 5) ? 5 : data.length));
                    })
                })
            }
        }
    },
    methods: {
        onAfterChange(obj) {
            console.log("after update: ", obj.item.itemMap);
        },
        setActive() {
            this.activeIdx = Math.pow((this.activeIdx - 1), 2)
            $(`.nav-link`).removeClass("active");
            $(`.nav-link-` + this.activeIdx).addClass("active");
        },
        handleNodeClick(data) {
            // console.log(data);
        },
        renderContent(h, { node, data, store }) { /* eslint-disable-line */
            if (data.type == "table") {
                return (
                    <span class="custom-tree-node">
                        <i class="fas fa-table"></i>
                        <span style="margin-left:5px;">{node.label}</span>
                    </span>
                );
            } else if (data.type == "column") {
                if (data.ctype == "text") {
                    return (
                        <span class="custom-tree-node">
                            <i class="fas fa-font"></i>
                            <span style="margin-left:5px;">{node.label}</span>
                        </span>
                    );
                } else if (data.ctype == "number") {
                    return (
                        <span class="custom-tree-node">
                            <i class="fas fa-list-ol"></i>
                            <span style="margin-left:5px;">{node.label}</span>
                        </span>
                    );
                } else if (data.ctype == "key") {
                    return (
                        <span class="custom-tree-node">
                            <i class="fas fa-key"></i>
                            <span style="margin-left:5px;">{node.label}</span>
                        </span>
                    );
                }

            }
        }
    },
    mounted: function () {
        console.log("this is settings view");
        $('.nav-link-' + this.activeIdx).addClass("active");

        pipeService.onSQL(sql => {
            this.historyData.push(sql);
            renderLogicFlowChart(this.historyData, this.containerId);
        })
    }
}
