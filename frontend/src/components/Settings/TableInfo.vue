<template>
  <div id="databaseMeta">
    <el-tree
      :data="tableColumns"
      :props="defaultProps"
      default-expand-all
      :render-content="renderContent"
    />
  </div>
</template>

<script>
const iconClassMap = {
  table: "fas fa-table",
  text: "fas fa-font",
  number: "fas fa-list-ol",
  key: "fas fa-key",
  time: "fas fa-clock",
};

export default {
  name: "TableInfo",
  props: {
    tableColumns: {
      type: Array,
      default: () => [],
    },
  },
  data() {
    return {
      defaultProps: {
        children: "children",
        label: "label",
      },
    };
  },
  methods: {
    renderContent(h, { node, data, store }) {
      /* eslint-disable-line */
      const columnType = data.type == "table" ? "table" : data.ctype;
      const iconClass = iconClassMap[columnType];
      return (
        <span class="custom-tree-node">
          <i class={iconClass}></i>
          <span class="column-name" style="margin-left: 10px">{node.label}</span>
        </span>
      );
    },
  },
};
</script>

<style scoped>
#databaseMeta {
  height: 690px;
  overflow: scroll;
  font-size: 14px;
}
</style>