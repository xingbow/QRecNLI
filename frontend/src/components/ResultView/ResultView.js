/* global d3 $ */
import pipeService from '../../service/pipeService.js';
import dataService from '../../service/dataService.js';
import DrawResult from './drawResult.js';
import SelectToken from './SelectToken.js';
import CondUnitToken from './CondUnitToken.js';
import VegaLiteChart from './VegaLiteChart.vue'
import DraggableTable from './DraggableTable.vue'
import DraggableChart from './DraggableChart.vue'
import draggable from "vuedraggable";
import VueVega from 'vue-vega';
import Vue from 'vue';

import VueDraggableResizable from "vue-draggable-resizable";
import "vue-draggable-resizable/dist/VueDraggableResizable.css";

Vue.use(VueVega);

export default {
    name: 'ResultView',
    components: {
        SelectToken,
        CondUnitToken,
        VegaLiteChart,
        draggable,
        DraggableTable,
        DraggableChart,
        VueDraggableResizable
    },
    props: {
        dbselected: "",
        tables: {},
    },
    data() {
        return {
            containerId: 'resultContainer',
            nl: "",

            // data for query results
            queryReturns: [],

            explanation: "",
            selectDecoded: [],
            whereDecoded: [],
            qSugg: {},

            visCounter: -1,
        }
    },
    computed: {},
    watch: {
        dbselected: function(dbselected) {
            dataService.SQLSugg(dbselected, (suggData) => {
                this.qSugg = suggData["nl"];
            });
        },
    },
    mounted: function() {
        this.drawResult = new DrawResult(this.containerId);
        pipeService.onSQL(sql => {
            this.nl = sql["sql"];
        });
        pipeService.onSQLTrans(SQLTrans => {
            this.explanation = SQLTrans.text;
            // this.sqlDecoded = SQLTrans.sqlDecoded;
            this.selectDecoded = SQLTrans.sqlDecoded['select'][1];
            this.whereDecoded = SQLTrans.sqlDecoded['where'].filter((d, i) => i % 2 === 0);
        });
        pipeService.onVLSpecs(queryReturns => {
            this.queryReturns = queryReturns.map(query => {
                this.visCounter += 1;
                return [...query, `origin-${this.visCounter}`];
            });
        });
        pipeService.onQuerySugg(qs => {
            this.qSugg = qs['nl'];
        });
        const vm = this;
        this.$nextTick(() => {
            dataService.SQLSugg(vm.dbselected, (suggData) => {
                console.log("suggestion data: ", suggData);
                this.qSugg = suggData["nl"];
            });
        });
    },
    methods: {
        selectQuery: function(nlidx) {
            if (this.qSugg) {
                console.log("receive nl query:", nlidx, this.qSugg[nlidx]);
                pipeService.emitSetQuery(this.qSugg[nlidx]);
            }
        },
        onDelete: function(index) {
            this.queryReturns.splice(index, 1);
        }
    }
}