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
      :tableConfig="tableConfig"
    />
    <template v-slot:setting-popover>
      <TableConfig 
        :currentConfig="tableConfig"
        @config-change="handleConfigChange"
        @apply-config="applyConfiguration"
        @reset-config="resetConfiguration"
      />
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
import TableConfig from "./TableConfig.vue";

const maxWidth = 200;

export default {
  name: "DraggableTable",
  components: { DraggableChart, Table, TableConfig },
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
      tableConfig: {
        rowsPerPage: 25,
        tableStyle: 'default',
        columnWidth: 'auto'
      }
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
    
    // Configuration methods
    handleConfigChange: function(configChange) {
      const { type, value } = configChange;
      
      switch(type) {
        case 'pagination':
          this.tableConfig.rowsPerPage = value;
          break;
        case 'style':
          this.tableConfig.tableStyle = value;
          break;
        case 'column-width':
          this.tableConfig.columnWidth = value;
          break;
      }
    },
    
    applyConfiguration: function(config) {
      this.tableConfig = { ...config };
      this.$forceUpdate();
    },
    
    resetConfiguration: function() {
      this.tableConfig = {
        rowsPerPage: 25,
        tableStyle: 'default',
        columnWidth: 'auto'
      };
      this.$forceUpdate();
    }
  },
};
</script>

<style scoped>
</style>
