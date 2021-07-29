import Vue from 'vue'

var pipeService = new Vue({
    data: {
        TESTEVENT: 'test_event',
        GETSQL:"GET_SQL",
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
        emitSql: function (msg) {
            this.$emit(this.GETSQL, msg)
        },
        onSQL: function (callback) {
            this.$on(this.GETSQL, function (msg) {
                callback(msg)
            })
        },
    }
})
export default pipeService
