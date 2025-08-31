<template>
  <DraggableChart
    :w="width"
    :h="height"
    :onResize="onResize"
    :onDelete="onDelete"
    :onPlotData="onPlotData"
    :defaultTitle="defaultTitle"
    :chartId="innerKey"
    :nlQuery="nlQuery"
    @bookmark-changed="onBookmarkChanged"
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
      <ChartConfig 
        :currentSpec="vlSpec"
        :chartId="innerKey"
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
/* global d3 $ */
import VueVega from "vue-vega";
import DraggableChart from "./DraggableChart.vue";
import Table from "./Table.vue";
import ChartConfig from "./ChartConfig.vue";
import configStorageService from "../../../service/configStorageService.js";
import Vue from "vue";

Vue.use(VueVega);

export default {
  name: "VegaLiteChart",
  components: { DraggableChart, Table, ChartConfig },
  props: {
    innerKey: String,
    vlSpecs: Array,
    data: Array,
    onDelete: Function,
    defaultTitle: {
      type: String,
      default: "",
    },
    savedConfig: {
      type: Object,
      default: null,
    },
    nlQuery: {
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
      
      // Configuration state
      currentConfig: {
        chartType: 'bar',
        colorScheme: 'category10',
        xAxisTitle: '',
        yAxisTitle: '',
        width: 400,
        height: 300
      }
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
      this.restoreConfiguration();
    },
  },
  mounted() {
    this.initChartStyle();
    this.restoreConfiguration();
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
    
    // Configuration methods
    handleConfigChange: function(configChange) {
      const { type, value } = configChange;
      
      switch(type) {
        case 'chart-type':
          this.currentConfig.chartType = value;
          this.updateChartType(value);
          break;
        case 'color-scheme':
          this.currentConfig.colorScheme = value;
          this.updateColorScheme(value);
          break;
        case 'axis-titles':
          this.currentConfig.xAxisTitle = value.x;
          this.currentConfig.yAxisTitle = value.y;
          this.updateAxisTitles(value);
          break;
        case 'size':
          this.currentConfig.width = value.width;
          this.currentConfig.height = value.height;
          this.updateChartSize(value);
          break;
      }
      
      // Auto-save configuration changes
      this.saveConfiguration();
    },
    
    updateChartType: function(chartType) {
      if (this.vlSpec && this.vlSpec.mark) {
        this.vlSpec = {
          ...this.vlSpec,
          mark: { ...this.vlSpec.mark, type: chartType },
          // Enable auto-sizing when chart type changes
          autosize: {
            type: "fit",
            // contains: "padding"
          }
        };
        this.$forceUpdate();
      }
    },
    
    updateColorScheme: function(colorScheme) {
      if (this.vlSpec && this.vlSpec.encoding) {
        // Update color encoding if it exists
        if (this.vlSpec.encoding.color) {
          this.vlSpec = {
            ...this.vlSpec,
            encoding: {
              ...this.vlSpec.encoding,
              color: {
                ...this.vlSpec.encoding.color,
                scale: { scheme: colorScheme }
              }
            }
          };
        }
        this.$forceUpdate();
      }
    },
    
    updateAxisTitles: function(titles) {
      if (this.vlSpec && this.vlSpec.encoding) {
        const newEncoding = { ...this.vlSpec.encoding };
        
        if (newEncoding.x) {
          newEncoding.x = { ...newEncoding.x, title: titles.x };
        }
        if (newEncoding.y) {
          newEncoding.y = { ...newEncoding.y, title: titles.y };
        }
        
        this.vlSpec = {
          ...this.vlSpec,
          encoding: newEncoding
        };
        this.$forceUpdate();
      }
    },
    
    updateChartSize: function(size) {
      this.width = size.width;
      this.height = size.height;
      this.innerWidth = size.width;
      this.innerHeight = size.height;
      
      this.vlSpec = {
        ...this.vlSpec,
        width: size.width,
        height: size.height
      };
      this.$forceUpdate();
    },
    
    applyConfiguration: function(config) {
      // Apply all configuration changes at once
      this.currentConfig = { ...config };
      this.updateChartType(config.chartType);
      this.updateColorScheme(config.colorScheme);
      this.updateAxisTitles({ x: config.xAxisTitle, y: config.yAxisTitle });
      this.updateChartSize({ width: config.width, height: config.height });
    },
    
    resetConfiguration: function() {
      // Reset to original specification
      this.transferVlSpecs();
      this.initChartStyle();
      this.currentConfig = {
        chartType: (this.vlSpec && this.vlSpec.mark && this.vlSpec.mark.type) || 'bar',
        colorScheme: 'category10',
        xAxisTitle: (this.vlSpec && this.vlSpec.encoding && this.vlSpec.encoding.x && this.vlSpec.encoding.x.title) || '',
        yAxisTitle: (this.vlSpec && this.vlSpec.encoding && this.vlSpec.encoding.y && this.vlSpec.encoding.y.title) || '',
        width: this.width,
        height: this.height
      };
    },

    restoreConfiguration: function() {
      // First check if there's a savedConfig prop passed from parent (for history restoration)
      if (this.savedConfig) {
        this.currentConfig = this.savedConfig;
        this.applyConfiguration(this.savedConfig);
        return;
      }
      
      // Otherwise, try to load from storage using nlQuery as key for consistency
      const storageKey = this.nlQuery || this.innerKey;
      const savedConfig = configStorageService.getChartConfig(storageKey);
      if (savedConfig) {
        this.currentConfig = savedConfig;
        this.applyConfiguration(savedConfig);
      }
    },

    saveConfiguration: function() {
      // Use nlQuery as storage key for consistency across sessions
      const storageKey = this.nlQuery || this.innerKey;
      if (storageKey) {
        configStorageService.saveChartState(
          storageKey, 
          this.currentConfig, 
          this.defaultTitle
        );
      }
    },
    
    // Clean up configuration when chart is deleted
    cleanupConfiguration: function() {
      if (this.innerKey) {
        configStorageService.deleteChartState(this.innerKey);
      }
    },
    
    // Pass through bookmark events
    onBookmarkChanged: function(bookmarkData) {
      this.$emit('bookmark-changed', bookmarkData);
    }
  },
  
  // Clean up configuration when component is destroyed
  beforeDestroy() {
    this.cleanupConfiguration();
  }
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