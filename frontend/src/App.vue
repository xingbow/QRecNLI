<template>
  <div id="app" style="width: 1400px">
      <nav class="navbar sticky-top navbar-dark bg-dark" style="padding-top: 1px; padding-bottom: 1px; margin-bottom: 5px;">
          <div style="margin-top:5px; margin-left: 5px;">
              <span style="color:white; font-size:1.25rem; font-weight:500; user-select: none">seqNLI</span>
          </div>
      </nav>
      <div class="d-flex flex-row rowele">
        <div class="p border-bottom border-right rowchild" style="width: 25%;">
          <div class="align-self-center" style="margin-right:5px; width:30%"><h6>Databases:</h6></div>
          <div style="width:70%; font-size:15px;">
            <v-select v-model="dbselected" :options="dbLists"/>
            </div>
        </div>
        <QueryPanel :dbselected = "dbselected"/>
      </div>
      <div class="d-flex flex-row rowele">
        <div class="p border-right" style="width: 25%; text-align:start;">
          <Settings :tableLists="tableLists" :tables="tables"></Settings>
        </div>
        <div class="p" style="width: 75%; text-align:start;"><ResultView /></div>
      </div>     
  </div>
</template>

<script>
import dataService from './service/dataService.js'
/* global d3 $ _ */
import Settings from './components/Settings/Settings.vue'
import ResultView from './components/ResultView/ResultView.vue'
import QueryPanel from './components/QueryPanel/QueryPanel.vue'
import vSelect from 'vue-select'
import 'vue-select/dist/vue-select.css';

export default {
  name: 'app',
  components: {
    Settings,
    QueryPanel,
    ResultView,
    vSelect
  },
  data() {
    return {
        dataset: "spider",
        dbselected: "cinema",
        dbLists: [],
        dbInfo: [],
        tables: {},
        tableLists: [],
    }
  },
  watch: {
    dbselected: function(dbselected){
      console.log("selected db name:",dbselected);
      dataService.getTables(dbselected, (data)=>{
        this.tables = data;
        this.tableLists = Object.keys(data);
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
          _this.dbLists = data;
          if(dbselected.length>0){
            dataService.getTables(dbselected, (data)=>{
              _this.tables = data;
              _this.tableLists = Object.keys(data);
              console.log("tables: ", _this.tableLists)
            })
          }
      });
    })
  },
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

</style>
