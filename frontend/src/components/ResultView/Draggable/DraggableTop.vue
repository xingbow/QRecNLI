<template>
  <div class="vis-container" v-if="qRet.type === 'vega-lite'">
    <VegaLiteChart
      :vlSpecs="qRet.content"
      :innerKey="qRet.id"
      :onDelete="onDelete"
    >
      <template v-slot:setting-popover>
        <slot name="setting-popover"></slot>
      </template>
      <template v-slot:info-popover>
        <slot name="info-popover"></slot>
      </template>
    </VegaLiteChart>
  </div>
  <div class="vis-container" v-else-if="qRet.type === 'table'">
    <DraggableTable
      :dataContent="qRet.content"
      :columnNames="Object.keys(qRet.content[0])"
      :onDelete="onDelete"
    >
      <template v-slot:setting-popover>
        <slot name="setting-popover"></slot>
      </template>
      <template v-slot:info-popover>
        <slot name="info-popover"></slot>
      </template>
    </DraggableTable>
  </div>
  <div
    class="vis-container"
    v-else-if="qRet.type === 'data'"
    @mousedown.stop=""
  >
    <DraggableChart
      :w="80"
      :h="50"
      :onDelete="onDelete"
    >
      <span class="result-text">{{ qRet.content }}</span>
      <template v-slot:setting-popover>
        <slot name="setting-popover"></slot>
      </template>
      <template v-slot:info-popover>
        <slot name="info-popover"></slot>
      </template>
    </DraggableChart>
  </div>
</template>

<script>
import VegaLiteChart from "./VegaLiteChart.vue";
import DraggableTable from "./DraggableTable.vue";
import DraggableChart from "./DraggableChart.vue";

export default {
  name: "DraggableTop",
  components: {
    VegaLiteChart,
    DraggableTable,
    DraggableChart,
  },
  props: {
    qRet: {
      type: Object,
      default: () => {},
    },
    onDelete: {
      type: Function,
      default: () => "",
    },
  },
};
</script>

<style scoped>
.vis-container {
  /* display: inline-flex; */
  position: absolute;
  top: 200px;
}

.vdr {
  border: 1px solid lightgray;
  border-radius: 5px;
}

.result-text {
  font-size: 40px;
  margin: 10px;
}
</style>


