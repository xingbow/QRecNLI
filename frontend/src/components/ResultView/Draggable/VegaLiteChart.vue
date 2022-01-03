<template>
  <DraggableChart
    :w="width"
    :h="height"
    :onResize="onResize"
    :onDelete="onDelete"
    :onPlotData="onPlotData"
    :defaultTitle="defaultTitle"
  >
    <vega-lite
      :spec="vlSpec"
      v-if="showData === false"
      v-bind:id="`vega-lite-chart-${innerKey}`"
    ></vega-lite>
    <Table
      v-else-if="showData === true"
      :columnNames="columnNames"
      :dataContent="data"
      :width="width"
    />
    <template v-slot:setting-popover>
      <slot name="setting-popover"></slot>
    </template>
    <template v-slot:info-popover>
      <slot name="info-popover"></slot>
    </template>
  </DraggableChart>
</template>

<script>
/* global d3 $ */
import VueVega from "vue-vega";
import DraggableChart from "./DraggableChart.vue";
import Table from "./Table.vue";
import Vue from "vue";

Vue.use(VueVega);

export default {
  name: "VegaLiteChart",
  components: { DraggableChart, Table },
  props: {
    innerKey: String,
    vlSpecs: Array,
    data: Array,
    onDelete: Function,
    defaultTitle: {
      type: String,
      default: "",
    },
  },
  data() {
    return {
      width: 150,
      height: 150,
      innerWidth: 150,
      innerHeight: 150,
      vlSpecRecords: {},
      vlFocalMark: "",
      vlSpec: {},

      showData: false,
    };
  },
  computed: {
    columnNames: function () {
      return Object.keys(this.data[0]);
    },
  },
  watch: {
    vlSpecs: function () {
      this.transferVlSpecs();
      this.initChartStyle();
    },
  },
  mounted() {
    this.initChartStyle();
  },
  beforeMount() {
    this.transferVlSpecs();
  },
  methods: {
    initChartStyle: function () {
      this.$nextTick(() => {
        const outerEle = $(`#vega-lite-chart-${this.innerKey}`).children("svg");
        const innerEle = outerEle.find("path.background")[0];
        this.width = outerEle.width();
        this.height = outerEle.height();
        this.innerWidth = innerEle.getBBox().width;
        this.innerHeight = innerEle.getBBox().height;
      });
    },
    transferVlSpecs: function () {
      const vlSpecRecords = {};
      for (let i in this.vlSpecs) {
        const vlSpec = this.vlSpecs[i];
        const mark = vlSpec.mark.type;
        let index = 1;
        while (
          Object.keys(vlSpecRecords).includes(mark) &&
          Object.keys(vlSpecRecords).includes(`${mark}-${index}`)
        ) {
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
    onResize: function (x, y, width, height) {
      if (width !== this.width || height !== this.height) {
        this.innerWidth += width - this.width;
        this.innerHeight += height - this.height;
        this.width = width;
        this.height = height;
        this.vlSpec = {
          ...this.vlSpec,
          width: this.innerWidth,
          height: this.innerHeight,
        };
      }
    },
    onPlotData: function () {
      this.showData = !this.showData;
    },
  },
};
</script>

<style scoped>
.float-button-rol {
  position: absolute;
  /* top: -30px; */
  top: 2px;
  right: 2px;
}

.el-button--mini {
  padding: 7px;
}
</style>