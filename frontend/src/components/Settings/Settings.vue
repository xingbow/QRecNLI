<template>
  <div id="settings">
    <div class="card-block" id="settingsContainer" style="padding: 10px 10px">
      <el-tabs type="card">
        <el-tab-pane label="Tables" name="0">
          <TableInfo :tableColumns="treeData" />
        </el-tab-pane>
        <el-tab-pane label="History Queries" name="1">
          <HistoryPanel />
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script>
/* global _ $*/
import TableInfo from "./TableInfo";
import HistoryPanel from "./HistoryPanel";

import "../../assets/historyQuery.css";

export default {
  name: "Settings",
  components: {
    HistoryPanel,
    TableInfo,
  },
  props: {
    tables: {},
  },
  data() {
    return {
      // TODO: organize metadata in tree layout
      treeData: [],
    };
  },
  watch: {
    tables: function (tables) {
      console.log("table changed in Setting View:", tables);
      const treeData = Object.entries(tables).map((data) => {
        const [key, value] = data;
        return {
          type: "table",
          label: key,
          children: value.map((v) => ({
            type: "column",
            label: v[0],
            ctype: v[1],
          })),
        };
      });
      this.treeData = treeData;
    },
  },
};
</script>

<style scoped>
.card {
  margin-bottom: 10px;
  border-radius: 5px;
  border: none;
}

.card-header {
  font-size: 12px;
  padding: 5px 5px;
  height: 36px;
}

.card-block {
  padding: 0px;
  position: relative;
}

.nav {
  font-size: 13px;
}

#settingsContainer {
  height: 761px;
}
</style>
