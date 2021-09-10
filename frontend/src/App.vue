<template>
  <div id="app" style="width: 100%">
    <nav
      class="navbar sticky-top navbar-dark bg-dark"
      style="padding-top: 1px; padding-bottom: 1px; margin-bottom: 5px"
    >
      <div style="margin-top: 5px; margin-left: 5px; display:inline-flex;">
        <span
          style="
            color: white;
            font-size: 1.25rem;
            font-weight: 500;
            user-select: none;
            font-size: 30px;
          "
          >seqNLI</span>
          <!-- user id -->
          <div style="
          margin-left: 5px;
            color: white;
            font-size: 1.25rem;
            font-weight: 500;
            user-select: none;
            font-size: 15px;
          ">ID: </div>
          <el-input
          style="width:200px;"
            placeholder="Please input user id"
            v-model="userid"
            clearable>
          </el-input>
          <!-- user name -->
          <div style="
          margin-left: 5px;
            color: white;
            font-size: 1.25rem;
            font-weight: 500;
            user-select: none;
            font-size: 13px;
          ">Name: </div>
          <el-input
            style="width:200px;"
            placeholder="Please input name"
            v-model="username"
            clearable>
          </el-input>
          <!-- system selection -->
          <div style="
          margin-left: 5px;
            color: white;
            font-size: 1.25rem;
            font-weight: 500;
            user-select: none;
            font-size: 13px;
          ">System type: </div>
          <el-select v-model="sysval" clearable placeholder="Select">
            <el-option
            style="width:200px;"
              v-for="item in sysType"
              :key="item.value"
              :label="item.label"
              :value="item.value">
            </el-option>
          </el-select>
      </div>
      <div style="float:right;color:white">
        <el-button plain v-show="start" v-on:click="beginQuery">Begin Query</el-button>
        <el-button plain v-show="!start" v-on:click="endQuery">End Query</el-button>
      </div>
    </nav>
    <el-row>
      <el-col :span="6">
        <div
          class="p border-right rowchild"
          style="display: flex"
        >
          <div class="align-self-center" style="margin: 10px; width: 70px">
            <h6>Databases:</h6>
          </div>
          <div style="margin: 5px 15px; width: 220px">
            <el-select v-model="dbselected" style="width: 100%">
              <el-option
                v-for="item in dbLists"
                :key="item"
                :label="item"
                :value="item"
              />
            </el-select>
          </div>
        </div>
        <div class="p border-bottom border-right" style="text-align: start;">
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
      dbselected: "customers_and_addresses",
      // dbselected: "department_management",
      dbLists: [],
      dbInfo: [],
      tables: {},
      // user study info
      userid: "",
      username: "",
      sysType: [{
        value: "base mode",
        label: "base mode"
      }, {
        value: "recommendation mode",
        label: "recommendation mode"
      }],
      sysval: "",
      start: true,
      curTime: 0,
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
    console.log("this: ", this, this.components);
    console.log(
      "_",
      _.partition([1, 2, 3, 4], (n) => n % 2)
    ); /* eslint-disable-line */
    let dataset = this.dataset;
    let dbselected = this.dbselected;
    const _this = this;
    this.$nextTick(() => {
      dataService.initialization(dataset, (data) => {
        data.sort()
        _this.dbLists = data;
        _this.dbLists.sort();
        if (dbselected.length > 0) {
          dataService.getTables(dbselected, (tableData) => {
            _this.tables = tableData;
          });
        }
      });
    });
  },
  methods: {
    beginQuery: function(){
      if( (this.userid.length>0) && (this.username.length>0) ){
        this.start = !this.start;
        let currtime = new Date().getTime()
        this.curTime = currtime;
        console.log("currtime: ", currtime);
        if(this.sysval == "base mode"){
          $(".next-query-trigger").hide();
          $(".recommend").hide();
        }else{
          $(".next-query-trigger").show();
          $(".recommend").show();
        }
      }else{
        alert("please input userid and username!");
      }
    },
    endQuery: function(){
      this.start = !this.start;
      let currtime = new Date().getTime();
      console.log("currtime (end): ", currtime, (currtime-this.curTime)/1000);
      let userQueryData = this.$children[5].$children[1].$children[0]._data.historySugg
      console.log("collect history query data", userQueryData);
      dataService.sendUserData({
        "userid": this.userid,
        "username": this.username,
        "starttime": this.curTime,
        "endtime": currtime,
        "systype": this.sysval,
        "userdata": userQueryData
      },res=>{
        console.log("response: ",res);
      });
      
    }
  }
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
