<template>
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
</template>

<script>
/* global _ $*/

const maxWidth = 200;

export default {
  name: "Table",
  components: {},
  props: {
    dataContent: Array,
    columnNames: Array,
    width: Number,
  },
  computed: {
    columns: function () {
      return this.buildColumns(this.columnNames, this.dataContent, this.width);
    }
  },
  methods: {
    estimateWidth: function (dataContent, name) {
      const tokenLength = _.max(dataContent.map((col) => `${col[name]}`.length));
      const letterWidth = 10;
      return _.min([_.max([tokenLength, name.length]) * letterWidth, maxWidth]);
    },
    buildColumns: function (columnNames, dataContent, width) {
      let columns = columnNames.map((name) => ({
        key: name,
        prop: name,
        label: name,
        width: this.estimateWidth(dataContent, name),
      }));
      columns = this.onUpdateColumnWidth(columns, width);
      return columns;
    },
    onUpdateColumnWidth: function (columns, width) {
      if (width !== undefined) {
        const sudoWidth = _.sum(columns.map((col) => col.width));
        columns = columns.map((col) => ({
          ...col,
          width: _.min([(col.width * width) / sudoWidth, maxWidth]),
        }));
      }
      return columns;
    },
  },
};
</script>

<style scoped>
</style>
