<template>
  <DraggableChart
    :w="width"
    :h="height"
    :onResize="onResize"
    :onDelete="onDelete"
    :defaultTitle="defaultTitle"
    class="draggable-table-container"
  >
    <el-table :data="dataContent" style="width: width" size="small">
      <el-table-column
        v-for="column in columns"
        :key="column.key"
        :prop="column.prop"
        :label="column.label"
        :width="column.width"
        :max-width="20"
      >
      </el-table-column>
    </el-table>
  </DraggableChart>
</template>

<script>
/* global _ $*/
import DraggableChart from "./DraggableChart.vue";

export default {
  name: "DraggableTable",
  components: { DraggableChart },
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
      columns: [],
      width: 500,
      height: 300,
    };
  },
  watch: {
    dataContent: function () {
      this.buildColumns();
    },
  },
  beforeMount() {
    this.buildColumns();
    this.width = _.sum(this.columns.map((col) => col.width));
  },
  methods: {
    estimateWidth: function (name) {
      const tokenLength = _.max(
        this.dataContent.map((col) => `${col[name]}`.length)
      );
      const letterWidth = 10;
      const maxWidth = 150;
      return _.min([_.max([tokenLength, name.length]) * letterWidth, maxWidth]);
    },
    buildColumns: function () {
      this.columns = this.columnNames.map((name) => ({
        key: name,
        prop: name,
        label: name,
        width: this.estimateWidth(name),
      }));
    },
    getTotalWidth: function () {
      console.log(_.sum(this.columns.map((col) => col.width)));
      return _.sum(this.columns.map((col) => col.width));
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
