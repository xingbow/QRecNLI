/* global d3 $ */
import pipeService from '../../service/pipeService.js';
import dataService from '../../service/dataService.js';
import DrawResult from './drawResult.js';
import SelectToken from './SelectToken.js';
import CondUnitToken from './CondUnitToken.js';
import VegaLiteChart from '../VegaLiteChart/VegaLiteChart.vue'
import VueVega from 'vue-vega';
import Vue from 'vue';

Vue.use(VueVega);

export default {
    name: 'ResultView',
    components: { SelectToken, CondUnitToken, VegaLiteChart },
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
        }
    },
    computed: {},
    watch: {
        dbselected: function(dbselected) {
            dataService.SQLSugg(dbselected, (suggData) => {
                this.qSugg = suggData["nl"];
            });
        }
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
            this.queryReturns = queryReturns;
        });
        pipeService.onQuerySugg(qs => {
            this.qSugg = qs['nl'];
        });
        const vm = this;
        this.$nextTick(() => {
            dataService.SQLSugg(vm.dbselected, (suggData) => {
                this.qSugg = suggData["nl"];
            });
        })
    },
    methods: {
        selectQuery: function(nlidx) {
            if (this.qSugg) {
                console.log("receive nl query:", nlidx, this.qSugg[nlidx]);
                pipeService.emitSetQuery(this.qSugg[nlidx]);
            }
        }
    }
}