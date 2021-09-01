<template>
  <div id="app" style="width: 100%">
    <nav
      class="navbar sticky-top navbar-dark bg-dark"
      style="padding-top: 1px; padding-bottom: 1px; margin-bottom: 5px"
    >
      <div style="margin-top: 5px; margin-left: 5px">
        <span
          style="
            color: white;
            font-size: 1.25rem;
            font-weight: 500;
            user-select: none;
            font-size: 30px;
          "
          >seqNLI</span
        >
      </div>
    </nav>
    <el-row>
      <el-col :span="6">
        <div
          class="p border-right rowchild"
          style="display: flex"
        >
          <div class="align-self-center" style="margin: 10px; width: 30%">
            <h6>Databases:</h6>
          </div>
          <div style="margin: 5px; width: 60%">
            <el-select v-model="dbselected">
              <el-option
                v-for="item in dbLists"
                :key="item"
                :label="item"
                :value="item"
              />
            </el-select>
          </div>
        </div>
        <div class="p border-right" style="text-align: start;">
          <Settings :tables="tables"></Settings>
        </div>
      </el-col>
      <el-col :span="18">
        <div class="p border-bottom border-right" style="display: flex;">
          <QueryPanel :dbselected="dbselected" :tables="tables" />
        </div>
        <div class="p" style="text-align: start">
          <ResultView :dbselected="dbselected" :tables="tables" />
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import dataService from "./service/dataService.js";
/* global d3 $ _ */
import Settings from "./components/Settings/Settings.vue";
import ResultView from "./components/ResultView/ResultView.vue";
import QueryPanel from "./components/QueryPanel/QueryPanel.vue";
import "vue-select/dist/vue-select.css";

export default {
  name: "app",
  components: {
    Settings,
    QueryPanel,
    ResultView,
  },
  data() {
    return {
      dataset: "spider",
      dbselected: "cinema",
      dbLists: [],
      dbInfo: [],
      tables: {},
    };
  },
  watch: {
    dbselected: function (dbselected) {
      console.log("selected db name:", dbselected);
      const _this = this;

      if (dbselected) {
        dataService.getTables(dbselected, (tableData) => {
          _this.tables = tableData;
        });
      }
    },
  },
  mounted: function () {
    console.log("d3: ", d3); /* eslint-disable-line */
    console.log("$: ", $); /* eslint-disable-line */
    console.log(
      "_",
      _.partition([1, 2, 3, 4], (n) => n % 2)
    ); /* eslint-disable-line */
    let dataset = this.dataset;
    let dbselected = this.dbselected;
    const _this = this;
    this.$nextTick(() => {
      dataService.initialization(dataset, (data) => {
        _this.dbLists = data;
        if (dbselected.length > 0) {
          dataService.getTables(dbselected, (tableData) => {
            _this.tables = tableData;
          });
        }
      });
    });
  },
};
</script>

<style>
#app {
  font-family: "Avenir", Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  width: 100%;
  margin: 0 auto;
}

.rowele {
  margin-left: 20px;
  margin-right: 20px;
  margin-bottom: 2px;
}

.rowchild {
  text-align: start;
  padding: 5px;
  border: lightgray;
  display: inline-flex;
  align-items: center;
}
</style>
