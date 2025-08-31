<template>
  <div class="chart-config">
    <h4>Chart Configuration</h4>
    
    <!-- Chart Type Selection -->
    <div class="config-section">
      <label>Chart Type:</label>
      <el-select v-model="selectedChartType" @change="onChartTypeChange" size="small">
        <el-option
          v-for="type in availableChartTypes"
          :key="type.value"
          :label="type.label"
          :value="type.value"
        />
      </el-select>
    </div>

    <!-- Color Configuration -->
    <div class="config-section">
      <label>Color Scheme:</label>
      <el-select v-model="selectedColorScheme" @change="onColorSchemeChange" size="small">
        <el-option
          v-for="scheme in availableColorSchemes"
          :key="scheme.value"
          :label="scheme.label"
          :value="scheme.value"
        />
      </el-select>
    </div>

    <!-- Axis Configuration -->
    <div class="config-section">
      <label>X-Axis Title:</label>
      <el-input 
        v-model="xAxisTitle" 
        @blur="onAxisConfigChange"
        size="small"
        placeholder="X-axis label"
      />
    </div>
    
    <div class="config-section">
      <label>Y-Axis Title:</label>
      <el-input 
        v-model="yAxisTitle" 
        @blur="onAxisConfigChange"
        size="small"
        placeholder="Y-axis label"
      />
    </div>

    <!-- Reset Buttons -->
    <div class="config-actions">
      <el-button size="small" @click="resetConfiguration">
        Reset
      </el-button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ChartConfig',
  props: {
    currentSpec: {
      type: Object,
      default: () => ({})
    },
    chartId: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      selectedChartType: 'bar',
      selectedColorScheme: 'category10',
      xAxisTitle: '',
      yAxisTitle: '',
      chartWidth: 400,
      chartHeight: 300,
      
      availableChartTypes: [
        { value: 'bar', label: 'Bar Chart' },
        { value: 'line', label: 'Line Chart' },
        { value: 'area', label: 'Area Chart' },
        { value: 'point', label: 'Scatter Plot' },
        { value: 'circle', label: 'Circle Plot' },
        { value: 'square', label: 'Square Plot' },
        { value: 'tick', label: 'Tick Plot' }
      ],
      
      availableColorSchemes: [
        { value: 'category10', label: 'Category 10' },
        { value: 'category20', label: 'Category 20' },
        { value: 'viridis', label: 'Viridis' },
        { value: 'plasma', label: 'Plasma' },
        { value: 'inferno', label: 'Inferno' },
        { value: 'magma', label: 'Magma' }
      ]
    }
  },
  mounted() {
    this.initializeFromCurrentSpec();
  },
  watch: {
    currentSpec: {
      handler(newSpec) {
        this.initializeFromCurrentSpec();
      },
      deep: true
    }
  },
  methods: {
    initializeFromCurrentSpec() {
      if (this.currentSpec && this.currentSpec.mark) {
        this.selectedChartType = this.currentSpec.mark.type;
      }
      if (this.currentSpec && this.currentSpec.encoding) {
        if (this.currentSpec.encoding.x && this.currentSpec.encoding.x.title) {
          this.xAxisTitle = this.currentSpec.encoding.x.title;
        }
        if (this.currentSpec.encoding.y && this.currentSpec.encoding.y.title) {
          this.yAxisTitle = this.currentSpec.encoding.y.title;
        }
      }
      if (this.currentSpec && this.currentSpec.width) {
        this.chartWidth = this.currentSpec.width;
      }
      if (this.currentSpec && this.currentSpec.height) {
        this.chartHeight = this.currentSpec.height;
      }
    },
    
    onChartTypeChange() {
      this.$emit('config-change', {
        type: 'chart-type',
        value: this.selectedChartType
      });
    },
    
    onColorSchemeChange() {
      this.$emit('config-change', {
        type: 'color-scheme',
        value: this.selectedColorScheme
      });
    },
    
    onAxisConfigChange() {
      this.$emit('config-change', {
        type: 'axis-titles',
        value: {
          x: this.xAxisTitle,
          y: this.yAxisTitle
        }
      });
    },
    
    onSizeChange() {
      this.$emit('config-change', {
        type: 'size',
        value: {
          width: this.chartWidth,
          height: this.chartHeight
        }
      });
    },
    
    applyConfiguration() {
      this.$emit('apply-config', {
        chartType: this.selectedChartType,
        colorScheme: this.selectedColorScheme,
        xAxisTitle: this.xAxisTitle,
        yAxisTitle: this.yAxisTitle,
        width: this.chartWidth,
        height: this.chartHeight
      });
    },
    
    resetConfiguration() {
      this.initializeFromCurrentSpec();
      this.$emit('reset-config');
    }
  }
}
</script>

<style scoped>
.chart-config {
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

.size-controls {
  display: flex;
  align-items: center;
  gap: 10px;
}

.size-separator {
  font-size: 16px;
  color: #666;
}

.config-actions {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.el-select,
.el-input,
.el-input-number {
  width: 100%;
}

.el-input-number {
  width: 80px;
}
</style>
