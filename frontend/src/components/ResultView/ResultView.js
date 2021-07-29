// /* global d3 $ */
import pipeService from '../../service/pipeService.js';
import DrawResult from './drawResult.js'

export default {
    name: 'ResultView',
    components: {},
    props: {},
    data() {
        return {
            containerId: 'resultContainer',
            nl: "",
            specs: "",
            explanations: ""
        }
    },
    watch: {},
    mounted: function() {
        this.drawResult = new DrawResult(this.containerId);
        pipeService.onSQL(sql => {
            this.nl = sql["sql"];
        })
    }
}