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
    props: { tables: {} },
    data() {
        return {
            containerId: 'resultContainer',
            nl: "",
            vlSpecs: [],
            explanation: "",
            selectDecoded: [],
            whereDecoded: [],
            count: 0,
            activeNames: ["1"],
        }
    },
    watch: {},
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
            this.vlSpecs = vlSpecs;
        })
    },
    methods: {
    }
}