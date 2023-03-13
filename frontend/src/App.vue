<template>
  <div id="app" style="width: 100%">
    <nav
      class="navbar sticky-top navbar-dark bg-dark"
      style="padding-top: 1px; padding-bottom: 1px; margin-bottom: 5px"
    >
      <div style="margin-top: 5px; margin-left: 5px; display:inline-flex;">
        <span style="color: white;font-size: 1.25rem;font-weight: 500;user-select: none;font-size: 30px;">Qrec-NLI</span>
      </div>
    </nav>
    <el-row>
      <!-- user logging -->
      <el-dialog
            title="User Experiment for Natural Language Interface"
            :visible.sync="userIdDialogVisible"
            :before-close="beginQuery"
            width="30%">
            <span style="margin-right: 10px;">User ID</span>
            <el-input placeholder="Please input user id" v-model="userid"></el-input>
            <br>
            <span style="margin-right: 10px;">User Name</span>
            <el-input placeholder="Please input user name" v-model="username"></el-input>
            <span slot="footer" class="dialog-footer">
              <!-- <el-button @click="userIdDialogVisible = true">Cancel</el-button> -->
              <el-button type="primary" @click="beginQuery">begin</el-button>
            </span>
      </el-dialog>
      <!-- user end query -->
      <el-dialog
            title="User Experiment for Natural Language Interface"
            :visible.sync="userEndDialogVisible"
            :before-close="handleEndClose"
            width="30%">
            <span style="margin-right: 10px;">Are you sure you have finished all the exploration tasks?</span>
            <!-- <el-input placeholder="Please input user id" v-model="userid"></el-input>
            <br>
            <span style="margin-right: 10px;">User Name</span>
            <el-input placeholder="Please input user name" v-model="username"></el-input> -->
            <span slot="footer" class="dialog-footer">
              <el-button type="primary" @click="endQuery">End</el-button>
              <el-button type="info" @click="userEndDialogVisible = false">Cancel</el-button>
            </span>
      </el-dialog>
      <!-- system main interface -->
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
          <div><el-button size="small" type="info" plain @click="userEndDialogVisible=true">End Query</el-button></div>
        </div>
        <div class="p border-bottom border-right" style="text-align: start;">
          <Settings :tables="tables"></Settings>
        </div>
      </el-col>
      <el-col :span="18">
        <div class="p border-bottom border-right" style="display: flex;">
          <QueryPanel :dbselected="dbselected" :tables="tables" />
        </div>
        <div class="p border-bottom" style="text-align: start">
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
import pipeService from './service/pipeService.js';

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
      userIdDialogVisible: true,
      userEndDialogVisible: false,
      originalSugg: {},
      userid: "",
      username: "",
      sysType: [{
        value: "base mode",
        label: "base mode"
      }, {
        value: "recommendation mode",
        label: "recommendation mode"
      }],
      sysval: "recommendation mode",
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

    // get original query suggestion data
    pipeService.onOriginalSugg((suggData)=>{
      console.log("receive original suggestion data: ", suggData);
      this.originalSugg = suggData;
    })

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
    handleEndClose: function(){
      this.userEndDialogVisible = false;
    },
    beginQuery: function(){
      if( (this.userid.length>0) && (this.username.length>0) ){
        this.userIdDialogVisible = false;
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
      console.log("this.historydata", this.$children[0].$children[2].$children[2].$children[0].$children[2].$children[0].historyData)
      let userQueryData = this.$children[0].$children[2].$children[2].$children[0].$children[2].$children[0].historyData
      // this.$children[5].$children[1].$children[0]._data.historySugg
      console.log("collect history query data", userQueryData);
      dataService.sendUserData({
        "userid": this.userid,
        "username": this.username,
        "starttime": this.curTime,
        "endtime": currtime,
        "systype": this.sysval,
        "userdata": {
          "origQuerySugg": this.originalSugg,
          "suerQueryData":userQueryData
        }
      },res=>{
        console.log("response: ",res);
        this.userEndDialogVisible = false;
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
