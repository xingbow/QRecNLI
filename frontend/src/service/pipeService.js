import Vue from 'vue'

var pipeService = new Vue({
    data: {
        TESTEVENT: 'test_event',
    },
    methods: {
        emitTestEvent: function (msg) {
            this.$emit(this.TESTEVENT, msg)
        },
        onTestEvent: function (callback) {
            this.$on(this.TESTEVENT, function (msg) {
                callback(msg)
            })
        }, 
    }
})
export default pipeService
