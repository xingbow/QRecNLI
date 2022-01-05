/* global d3 $ */
import pipeService from '../../service/pipeService.js';
import DraggableTop from './Draggable/DraggableTop.vue'
import SQLExplanation from './SQLExplanation.vue'
import draggable from "vuedraggable";
import VueVega from 'vue-vega';
import Vue from 'vue';

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
            const { sql, nl, SQLTrans, VLSpecs } = sqlRet;
            this.sqlQuery = sql;
            this.nlQuery = nl;
            this.explanation = SQLTrans.text;
            this.selectDecoded = SQLTrans.sqlDecoded['select'][1];
            this.whereDecoded = SQLTrans.sqlDecoded['where'].filter((d, i) => i % 2 === 0);
            this.groupbyDecoded = SQLTrans.sqlDecoded['groupBy'];
            this.queryReturns = VLSpecs.map(query => {
                this.visCounter += 1;
                // return [...query, `origin-${this.visCounter}`];
                return {...query,
                    id: `origin-${this.visCounter}`,
                    title: nl,
                    sqlQuery: sql,
                    nlQuery: nl,
                    nlExplanation: SQLTrans.text,
                    sqlDecoded: SQLTrans.sqlDecoded,
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