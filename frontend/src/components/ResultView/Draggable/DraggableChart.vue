<template>
  <vue-draggable-resizable
    :w="w + margin.left + margin.right"
    :h="h + margin.top + margin.bottom"
    @resizing="_onResize"
  >
    <div class="draggable-chart-container">
      <div v-if="titleVisible === true">
        <span class="title">{{ title }}</span>
      </div>
      <el-row class="float-button-rol" v-if="inputVisible === false">
        <el-button
          plain
          size="mini"
          icon="el-icon-info"
          v-on:click="infoVisible = !infoVisible"
        ></el-button>
        <el-button
          plain
          size="mini"
          icon="el-icon-edit"
          v-on:click="inputVisible = true"
        ></el-button>
        <el-button
          plain
          size="mini"
          icon="el-icon-setting"
          v-on:click="settingVisible = !settingVisible"
        ></el-button>
        <el-button
          plain
          size="mini"
          icon="el-icon-delete"
          v-on:click="onDelete"
        ></el-button>
      </el-row>
      <div class="title-input-container" v-if="inputVisible === true">
        <el-input
          v-model="title"
          width="w"
          class="title-input"
          @blur="
            inputVisible = false;
            titleVisible = true;
          "
        ></el-input>
      </div>
      <el-popover
        class="popover-setting"
        placement="right"
        width="450"
        trigger="manual"
        v-model="settingVisible"
      >
        <el-button
          plain
          size="mini"
          type="text"
          icon="el-icon-close"
          class="popover-close"
          v-on:click="settingVisible = false"
        ></el-button>
        <slot name="setting-popover"></slot>
      </el-popover>
      <el-popover
        class="popover-info"
        placement="right"
        width="450"
        trigger="manual"
        v-model="infoVisible"
      >
        <el-button
          plain
          size="mini"
          type="text"
          icon="el-icon-close"
          class="popover-close"
          v-on:click="infoVisible = false"
        ></el-button>
        <slot name="info-popover"></slot>
      </el-popover>
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
  data() {
    return {
      settingVisible: false,
      infoVisible: false,
      inputVisible: false,
      titleVisible: true,
      title: "title",
      margin: {
        top: 10,
        bottom: 10,
        left: 10,
        right: 10,
      },
    };
  },
  props: {
    onDelete: {
      type: Function,
      default: () => "",
    },
    onResize: {
      type: Function,
      default: () => true,
    },
    w: {
      type: Number,
      default: 150,
    },
    h: {
      type: Number,
      default: 150,
    },
    defaultTitle: {
      type: String,
      default: "",
    },
  },
  mounted() {
    this.title = this.defaultTitle;
  },
  methods: {
    _onResize: function (x, y, width, height) {
      this.onResize(
        x,
        y,
        width - this.margin.left - this.margin.right,
        height - this.margin.top - this.margin.bottom
      );
    },
  },
};
</script>

<style scoped>
.draggable-chart-container {
  overflow: scroll;
  width: 100%;
  height: 100%;
  justify-content: center;
  padding: 10px;
}

.draggable-chart-container:hover .float-button-rol {
  display: block;
}

.float-button-rol {
  position: absolute;
  top: -45px;
  right: -5px;
  display: none;
  padding: 10px;
}

.el-button--mini {
  padding: 8px;
}

.popover-info,
.popover-setting {
  position: absolute;
  top: -50px;
  right: -10px;
}

.popover-close {
  position: absolute;
  right: 10px;
  top: -3px;
}

.title-input-container {
  /* margin: 0px 10px; */
  width: calc(100% - 20px);
  position: absolute;
}

.title-input {
  top: -55px;
}

.title {
  position: absolute;
  top: -35px;
}
</style>
