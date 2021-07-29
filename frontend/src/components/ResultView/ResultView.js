// /* global d3 $ */
import pipeService from '../../service/pipeService.js';
import DrawResult from './drawResult.js';
import Vue from 'vue'
import VueVega from 'vue-vega'

Vue.use(VueVega)

export default {
    name: 'ResultView',
    components: {},
    props: {},
    data() {
        return {
            containerId: 'resultContainer',
            nl: "",
            vlSpecs: [],
            explanations: "",
        }
    },
    watch: {},
    mounted: function() {
        this.drawResult = new DrawResult(this.containerId);
        pipeService.onSQL(sql => {
            this.nl = sql["sql"];
            this.vlSpecs = sql["vlSpecs"];
        })
    }
}