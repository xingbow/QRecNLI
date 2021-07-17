<template>
  <div id="app" style="width: 1400px">
      <nav class="navbar sticky-top navbar-dark bg-dark" style="padding-top: 1px; padding-bottom: 1px; margin-bottom: 5px;">
          <div style="margin-top:5px; margin-left: 5px;">
              <span style="color:white; font-size:1.25rem; font-weight:500; user-select: none">seqNLI</span>
          </div>
      </nav>
      <div class="d-flex flex-row rowele">
        <div class="p border rounded rowchild" style="width: 25%;">
          <div class="align-self-center" style="margin-right:5px; width:20%"><h6>Dataset:</h6></div>
          <div style="width:80%; font-size:15px;">
            <v-select v-model="dbselected" :options="['Canada', 'United States']"/>
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
        <div class="p" style="width: 25%; text-align:start;"><Settings></Settings></div>
        <div class="p" style="width: 75%; text-align:start;"><ResultView></ResultView></div>
      </div>     
  </div>
</template>

<script>
import dataService from './service/dataService.js'
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
        userText: "",
        dbselected: "",
    }
  },
  watch: {
    dbselected: function(dbselected){
      console.log("selected db name:",dbselected);
    }
  },
  mounted: function () {
    console.log('d3: ', d3) /* eslint-disable-line */
    console.log('$: ', $) /* eslint-disable-line */
    console.log('_', _.partition([1, 2, 3, 4], n => n % 2)) /* eslint-disable-line */
  },
  methods: {
    search: function() {
      if(this.userText.length>0){
        dataService.initialization(this.userText, (data) => {
          console.log('user query result: ', data['data']) /* eslint-disable-line */
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
