// /* global d3 $ */
import pipeService from '../../service/pipeService.js';
import DrawResult from './drawResult.js';
import SelectToken from './SelectToken.js';
import VueVega from 'vue-vega';
import Vue from 'vue';

Vue.use(VueVega);

export default {
    name: 'ResultView',
    components: { SelectToken },
    props: { tables: {} },
    data() {
        return {
            containerId: 'resultContainer',
            nl: "",
            vlSpecs: [],
            explanation: "",
            selectDecoded: [],
            count: 0,
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
        });
        pipeService.onVLSpecs(vlSpecs => {
            this.vlSpecs = vlSpecs;
        })
    },
    methods: {
        load() {
            this.count += 2
        }
    }
}