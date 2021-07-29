<template>
  <div id="app" style="width: 1400px">
      <nav class="navbar sticky-top navbar-dark bg-dark" style="padding-top: 1px; padding-bottom: 1px; margin-bottom: 5px;">
          <div style="margin-top:5px; margin-left: 5px;">
              <span style="color:white; font-size:1.25rem; font-weight:500; user-select: none">seqNLI</span>
          </div>
      </nav>
      <div class="d-flex flex-row rowele">
        <div class="p border rounded rowchild" style="width: 25%;">
          <div class="align-self-center" style="margin-right:5px; width:30%"><h6>Databases:</h6></div>
          <div style="width:70%; font-size:15px;">
            <v-select v-model="dbselected" :options="dbLists"/>
            </div>
        </div>
        <div class="p border rounded rowchild" style="width: 75%;">
          <div class="align-self-center" style="margin-right:5px;"><h6>Query:</h6></div>
          <div style="width:90%">
            <div class="input-group" style="font-size:14px;">
              <input type="text" class="form-control" v-model="userText" placeholder="show me the film with the largest cost." style="font-size:14px;"/>
              <div class="input-group-append">
                <button class="btn btn-outline-secondary btn-sm speaker" type="button"><i class="fas fa-microphone"></i></button>
                <button class="btn btn-outline-secondary btn-sm" type="button" v-on:click="search">Search</button>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="d-flex flex-row rowele">
        <div class="p" style="width: 25%; text-align:start;">
          <Settings :tableLists="tableLists"></Settings>
        </div>
        <div class="p" style="width: 75%; text-align:start;"><ResultView></ResultView></div>
      </div>     
  </div>
</template>

<script>
import dataService from './service/dataService.js'
import pipeService from "./service/pipeService.js"
/* global d3 $ _ */
import Settings from './components/Settings/Settings.vue'
import ResultView from './components/ResultView/ResultView.vue'
import vSelect from 'vue-select'
import 'vue-select/dist/vue-select.css';

export default {
  name: 'app',
  components: {
    Settings,
    ResultView,
    vSelect
  },
  data() {
    return {
        dataset: "spider",
        userText: "",
        dbselected: "cinema",
        dbLists: [],
        tableLists: [],
    }
  },
  watch: {
    dbselected: function(dbselected){
      console.log("selected db name:",dbselected);
      dataService.getTables(dbselected, (data)=>{
        this.tableLists = data["data"];
        console.log("tables: ", this.tableLists);
      });
    }
  },
  mounted: function () {
    console.log('d3: ', d3) /* eslint-disable-line */
    console.log('$: ', $) /* eslint-disable-line */
    console.log('_', _.partition([1, 2, 3, 4], n => n % 2)) /* eslint-disable-line */
    let dataset = this.dataset;
    let dbselected = this.dbselected;
    const _this = this;
    this.$nextTick(()=>{
        dataService.initialization(dataset, (data)=>{
          _this.dbLists = data["data"];
          if(dbselected.length>0){
            dataService.getTables(dbselected, (data)=>{
              _this.tableLists = data["data"];
              console.log("tables: ", _this.tableLists)
            })
          }
      });
    })
    
  },
  methods: {
    search: function() {
      if(this.userText.length>0){
        let userText = this.userText;
        dataService.text2SQL([this.userText,this.dbselected], (data) => {
          let sqlResult = {
            "sql": data["data"]["sql"].trim(),
            "data": data["data"]["data"],
            "nl": userText.trim()
          }
          console.log('user query result: ', sqlResult); /* eslint-disable-line */
          // send "sql" to settings and record sql history
          if(sqlResult["sql"].length>0){
            dataService.SQL2VL(sqlResult["sql"], this.dbselected, (data) => {
              console.log('vl specification result: ', data["data"]); /* eslint-disable-line */
              sqlResult.vlSpecs = data["data"];
              pipeService.emitSql(sqlResult);
            })
          }
        });
      }else{
        alert("input text is empty");
      }
    }
  }
}
</script>

<style>
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
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
  margin-bottom:2px;
}

.rowchild {
  text-align:start; 
  padding:5px; 
  border:lightgray; 
  display:inline-flex;
}

.input-group {
  font-size: 14px;
}

.speaker:hover {
/* color: #fff !important; */
text-decoration: none;
}


</style>
