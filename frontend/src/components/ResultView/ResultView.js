// /* global d3 $ */
import DrawResult from './drawResult.js'

export default {
    name: 'ResultView',
    components: {
    },
    props: {
    },
    data() {
        return {
            containerId: 'resultContainer',
        }
    },
    watch: {
    },
    mounted: function () {
        this.drawResult = new DrawResult(this.containerId)
    }
}
