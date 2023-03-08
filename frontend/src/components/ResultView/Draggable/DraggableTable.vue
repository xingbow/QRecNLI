<template>
  <DraggableChart
    :w="width"
    :h="height"
    :onResize="onResize"
    :onDelete="onDelete"
    :defaultTitle="defaultTitle"
    class="draggable-table-container"
  >
    <Table
      :dataContent="dataContent"
      :columnNames="columnNames"
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
/* global _ $*/
import DraggableChart from "./DraggableChart.vue";
import Table from "./Table.vue";

const maxWidth = 200;

export default {
  name: "DraggableTable",
  components: { DraggableChart, Table },
  props: {
    dataContent: Array,
    columnNames: Array,
    onDelete: Function,
    defaultTitle: {
      type: String,
      default: "",
    },
  },
  data() {
    return {
      width: 500,
      height: 300,
    };
  },
  watch: {
    dataContent: function () {
      this.width = this.getTotalWidth();
    },
  },
  beforeMount() {
    this.width = this.getTotalWidth();
  },
  methods: {
    estimateWidth: function (name) {
      const tokenLength = _.max(
        this.dataContent.map((col) => `${col[name]}`.length)
      );
      const letterWidth = 10;
      return _.min([_.max([tokenLength, name.length]) * letterWidth, maxWidth]);
    },
    getTotalWidth: function () {
      return _.sum(this.columnNames.map((name) => this.estimateWidth(name)));
    },
    onResize: function (x, y, width, height) {
      if (width !== this.width || height !== this.height) {
        this.width = width;
        this.height = height;
      }
    },
  },
};
</script>

<style scoped>
</style>
