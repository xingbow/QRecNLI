<template>
  <vue-draggable-resizable
    :w="w"
    :h="h"
    @resizing="onResize"
  >
    <div class="draggable-chart-container">
      <el-row class="float-button-rol">
        <el-button
          plain
          size="mini"
          icon="el-icon-delete"
          v-on:click="onDelete"
        ></el-button>
      </el-row>
      <slot></slot>
    </div>
  </vue-draggable-resizable>
</template>

<script>
/* global _ $*/
import VueDraggableResizable from "vue-draggable-resizable";
import "vue-draggable-resizable/dist/VueDraggableResizable.css";

export default {
  name: "DraggableChart",
  components: { VueDraggableResizable },
  props: {
    onDelete: {
      type: Function,
      default: () => ""
    },
    onResize: {
      type: Function,
      default: () => true
    },
    w: Number,
    h: Number,
  },
  methods: {
      elementMouseDown: function(e){
          console.log(e);
          e.stopPropagation();
      }
  },
};
</script>

<style scoped>
.draggable-chart-container {
    overflow: hidden;
    width: 100%;
    height: 100%;
}

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
