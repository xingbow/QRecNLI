/* global _ $*/
import vSelect from 'vue-select'
import 'vue-select/dist/vue-select.css';
import pipeService from '../../service/pipeService';
import draggable from "vuedraggable";
// import { renderLogicFlowChart } from './logicFlow'

import "../../assets/historyQuery.css"

export default {
    name: 'Settings',
    components: {
        vSelect, draggable
    },
    props: {
        tables: {},
    },
    data() {
        return {
            // containerId: "settingsContainer",
            tableCols: [],
            historyData: [],
            currentVl: [],
            // TODO: organize metadata in tree layout
            treedata: [],
            defaultProps: {
                children: 'children',
                label: 'label',
            },
            rightButtonVisible: false,
            visCounter: -1,
        }
    },
    watch: {
        tables: function (tables) {
            console.log("table changed in Setting View:", tables);
            let treedata = [];
            for (const [key, value] of Object.entries(tables)) {
                treedata.push({
                    "type": "table",
                    "label": key,
                    "children": value.map(v =>
                        ({ "type": "column", "label": v[0], "ctype": v[1] })
                    ),
                });
            }
            this.treedata = treedata;

        }
    },
    methods: {
        onAfterChange(obj) {
            console.log("after update: ", obj.item.itemMap);
        },
        findHistoryNodeByKey(key) {
            for (let hisId in this.historyData) {
                const history = this.historyData[hisId];
                if (history.key == key) {
                    return history;
                }
            }
            return undefined
        },
        // handleNodeClick({ data, e, position }) {
        handleNodeClick(key) {
            const history = this.findHistoryNodeByKey(key);
            pipeService.emitSQL(history.SQL);
            pipeService.emitSQLTrans(history.SQLTrans);
            pipeService.emitVLSpecs(history.VLSpecs);
            // pipeService.emitQuerySugg(history.QuerySugg);
            this.historyData.pop();
        },
        handleNodeClone({ key }) {
            const history = this.findHistoryNodeByKey(key);
            const specs = history.VLSpecs.map(spec => {
                this.visCounter += 1;
                return [...spec, `history-${this.visCounter}`];
            });
            return specs[0];
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
        },
    },
    mounted: function () {
        pipeService.onSQL(sql => {
            this.historyData.push({ 'SQL': sql, 'key': sql.nl });
        });

        pipeService.onSQLTrans(sqlTrans => {
            this.historyData[this.historyData.length - 1].SQLTrans = sqlTrans;
        });

        pipeService.onVLSpecs(VLSpecs => {
            this.historyData[this.historyData.length - 1].VLSpecs = VLSpecs;
            this.currentVl = VLSpecs;
        });

        // pipeService.onSetQuery(SetQuery => {
        //     this.historyData[this.historyData.length - 1].SetQuery = SetQuery;
        // });

        pipeService.onQuerySugg(QuerySugg => {
            this.historyData[this.historyData.length - 1].QuerySugg = QuerySugg;
        });
    }
}
