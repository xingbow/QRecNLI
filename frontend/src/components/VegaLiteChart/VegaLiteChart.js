/* global d3 $ */
import VueVega from 'vue-vega';
import VueDraggableResizable from 'vue-draggable-resizable'
import 'vue-draggable-resizable/dist/VueDraggableResizable.css'
import Vue from 'vue';

Vue.use(VueVega);

export default {
    name: 'VegaLiteChart',
    components: { VueDraggableResizable },
    props: {
        innerKey: "",
        vlSpecs: Array,
    },
    data() {
        return {
            width: 150,
            height: 150,
            vlSpecRecords: {},
            vlFocalMark: "",
            vlSpec: {},
        }
    },
    computed: {},
    watch: {
        vlSpecs: function() {
            this.transferVlSpecs();
            this.initChartStyle();
        }
    },
    mounted() {
        this.initChartStyle();
    },
    beforeMount() {
        this.transferVlSpecs();
    },
    methods: {
        initChartStyle: function() {
            this.$nextTick(() => {
                const d = $(`#vega-lite-chart-${this.innerKey}`).children('svg');
                this.width = d.width();
                this.height = d.height();
            })
        },
        transferVlSpecs: function() {
            const vlSpecRecords = {};
            for (let i in this.vlSpecs) {
                const vlSpec = this.vlSpecs[i];
                const mark = vlSpec.mark.type;
                let index = 1;
                while (Object.keys(vlSpecRecords).includes(mark) &&
                    Object.keys(vlSpecRecords).includes(`${mark}-${index}`)) {
                    i += 1;
                }
                if (Object.keys(vlSpecRecords).includes(mark)) {
                    vlSpecRecords[`${mark}-${index}`] = vlSpec;
                } else {
                    vlSpecRecords[mark] = vlSpec;
                }
            }
            const vlFocalMark = this.vlSpecs[0].mark.type;
            this.vlSpecRecords = vlSpecRecords;
            this.vlFocalMark = vlFocalMark;
            this.vlSpec = vlSpecRecords[vlFocalMark];
        },
        onResize: function(x, y, width, height) {
            this.width = width
            this.height = height
            this.vlSpec = {...this.vlSpec, width: this.width - 60, height: this.height - 55 };
        },
    }
}