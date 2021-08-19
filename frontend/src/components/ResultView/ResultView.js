// /* global d3 $ */
import pipeService from '../../service/pipeService.js';
import DrawResult from './drawResult.js';
import SelectToken from './SelectToken.js';
import CondUnitToken from './CondUnitToken.js';
import VueVega from 'vue-vega';
import Vue from 'vue';

Vue.use(VueVega);

export default {
    name: 'ResultView',
    components: { SelectToken, CondUnitToken },
    props: {
        tables: {},
        querySugg: {}
    },
    data() {
        return {
            containerId: 'resultContainer',
            nl: "",

            // data for query results
            results: [],
            resultType: "none",
            columns: [],

            explanation: "",
            selectDecoded: [],
            whereDecoded: [],
            count: 0,
            activeNames: ["1"],
            qSugg: {},
        }
    },
    computed: {},
    watch: {
        querySugg: function(querySugg) {
            if (Object.keys(querySugg).length > 0) {
                // console.log("query suggestion in the results view: ", querySugg);
                this.qSugg = querySugg;
            }
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
        pipeService.onVLSpecs(vlSpecs => {
            this.results = vlSpecs[0];
            this.resultType = vlSpecs[1];
            if (this.resultType === 'table' && this.results.length > 0)
                this.columns = Object.keys(this.results[0]);
        });
        pipeService.onQuerySugg(qs => {
            this.qSugg = qs;
        });
    },
    methods: {
        selectQuery: function(nlidx) {
            console.log("receive nl query:", nlidx, this.qSugg["nl"][nlidx]);
            pipeService.emitSetQuery(this.qSugg["nl"][nlidx]);
        }
    }
}