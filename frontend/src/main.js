import Vue from 'vue'
import App from './App.vue'

import 'bootstrap'
import 'bootstrap/dist/css/bootstrap.min.css'
import 'video.js/dist/video-js.min.css'

import _ from 'lodash'
window._ = _

import * as d3 from 'd3'
window.d3 = d3

import $ from 'jquery'
window.$ = $

require('../node_modules/@fortawesome/fontawesome-free/css/all.css');

Vue.config.productionTip = false

new Vue({
  render: h => h(App),
}).$mount('#app')
