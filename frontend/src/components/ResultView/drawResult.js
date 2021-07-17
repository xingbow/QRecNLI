/* global d3 $ */
// import pipeService from '../../service/pipeService'

let DrawResult= function (id) {	
	this.id = id
    this.svgWidth = $('#' + id).width()
    this.svgHeight = $('#' + id).height()
    this.margin = { top: 10, right: 10, bottom: 10, left: 10 }
}

DrawResult.prototype.layout = function (data) {
    d3.select('#' + this.id).selectAll('*').remove()
    console.log('data: ', data)  /* eslint-disable-line */
}

export default DrawResult