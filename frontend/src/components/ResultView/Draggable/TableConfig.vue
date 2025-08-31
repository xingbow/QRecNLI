<template>
  <div class="table-config">
    <h4>Table Configuration</h4>
    
    <!-- Pagination Settings -->
    <div class="config-section">
      <label>Rows per page:</label>
      <el-select v-model="rowsPerPage" @change="onPaginationChange" size="small">
        <el-option label="10" :value="10" />
        <el-option label="25" :value="25" />
        <el-option label="50" :value="50" />
        <el-option label="100" :value="100" />
      </el-select>
    </div>

    <!-- Table Styling -->
    <div class="config-section">
      <label>Table Style:</label>
      <el-select v-model="tableStyle" @change="onStyleChange" size="small">
        <el-option label="Default" value="default" />
        <el-option label="Striped" value="striped" />
        <el-option label="Bordered" value="bordered" />
        <el-option label="Compact" value="compact" />
      </el-select>
    </div>

    <!-- Column Width -->
    <div class="config-section">
      <label>Column Width:</label>
      <el-select v-model="columnWidth" @change="onColumnWidthChange" size="small">
        <el-option label="Auto" value="auto" />
        <el-option label="Fixed" value="fixed" />
        <el-option label="Responsive" value="responsive" />
      </el-select>
    </div>

    <!-- Apply/Reset Buttons -->
    <div class="config-actions">
      <el-button type="primary" size="small" @click="applyConfiguration">
        Apply Changes
      </el-button>
      <el-button size="small" @click="resetConfiguration">
        Reset
      </el-button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TableConfig',
  props: {
    currentConfig: {
      type: Object,
      default: () => ({})
    }
  },
  data() {
    return {
      rowsPerPage: 25,
      tableStyle: 'default',
      columnWidth: 'auto'
    }
  },
  mounted() {
    this.initializeFromCurrentConfig();
  },
  methods: {
    initializeFromCurrentConfig() {
      if (this.currentConfig.rowsPerPage) {
        this.rowsPerPage = this.currentConfig.rowsPerPage;
      }
      if (this.currentConfig.tableStyle) {
        this.tableStyle = this.currentConfig.tableStyle;
      }
      if (this.currentConfig.columnWidth) {
        this.columnWidth = this.currentConfig.columnWidth;
      }
    },
    
    onPaginationChange() {
      this.$emit('config-change', {
        type: 'pagination',
        value: this.rowsPerPage
      });
    },
    
    onStyleChange() {
      this.$emit('config-change', {
        type: 'style',
        value: this.tableStyle
      });
    },
    
    onColumnWidthChange() {
      this.$emit('config-change', {
        type: 'column-width',
        value: this.columnWidth
      });
    },
    
    applyConfiguration() {
      this.$emit('apply-config', {
        rowsPerPage: this.rowsPerPage,
        tableStyle: this.tableStyle,
        columnWidth: this.columnWidth
      });
    },
    
    resetConfiguration() {
      this.initializeFromCurrentConfig();
      this.$emit('reset-config');
    }
  }
}
</script>

<style scoped>
.table-config {
  padding: 15px;
  max-width: 400px;
}

.config-section {
  margin-bottom: 15px;
}

.config-section label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
  font-size: 14px;
}

.config-actions {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.el-select {
  width: 100%;
}
</style>
