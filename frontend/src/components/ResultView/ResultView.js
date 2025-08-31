/* global d3 $ */
import pipeService from '../../service/pipeService.js';
import DraggableTop from './Draggable/DraggableTop.vue'
import SQLExplanation from './SQLExplanation.vue'
import draggable from "vuedraggable";
import VueVega from 'vue-vega';
import Vue from 'vue';
import configStorageService from '../../service/configStorageService.js';

Vue.use(VueVega);

export default {
    name: 'ResultView',
    components: {
        SQLExplanation,
        draggable,
        DraggableTop,
    },
    props: {
        dbselected: "",
        tables: {},
    },
    data() {
        return {
            containerId: 'resultContainer',
            nlQuery: "",
            sqlQuery: "",

            // data for query results
            queryReturns: [],

            explanation: "",
            selectDecoded: [],
            whereDecoded: [],
            groupbyDecoded: [],

            visCounter: -1,
        }
    },
    mounted: function() {
        pipeService.onSQL(sqlRet => {
            const { sql, nl, SQLTrans, VLSpecs, savedConfigState } = sqlRet;
            this.sqlQuery = sql;
            this.nlQuery = nl;
            this.explanation = SQLTrans.text;
            // this.selectDecoded = SQLTrans.sqlDecoded['select'][1];
            // this.whereDecoded = SQLTrans.sqlDecoded['where'].filter((d, i) => i % 2 === 0);
            // this.groupbyDecoded = SQLTrans.sqlDecoded['groupBy'];
            this.queryReturns = VLSpecs.map(query => {
                this.visCounter += 1;
                const chartId = `origin-${this.visCounter}`;
                
                // Use saved state from history click if available, otherwise check storage using nlQuery
                let savedState = savedConfigState;
                if (!savedState) {
                    savedState = configStorageService.getChartState(nl);
                }
                
                return {...query,
                    id: chartId,
                    title: (savedState && savedState.title) || nl, // Use saved title if available
                    sqlQuery: sql,
                    nlQuery: nl,
                    nlExplanation: SQLTrans.text,
                    savedConfig: savedState && savedState.config, // Include saved config for restoration
                    // sqlDecoded: SQLTrans.sqlDecoded,
                };
            });
        });
    },
    methods: {
        onDelete: function(index) {
            this.queryReturns.splice(index, 1);
        }
    }
}