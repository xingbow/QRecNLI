import Vue from 'vue'

var pipeService = new Vue({
    data: {
        TESTEVENT: 'test_event',
        GETSQL: "GET_SQL",
    },
    methods: {
        emitTestEvent: function(msg) {
            this.$emit(this.TESTEVENT, msg)
        },
        onTestEvent: function(callback) {
            this.$on(this.TESTEVENT, function(msg) {
                callback(msg)
            })
        },
        emitSQL: function(msg) {
            this.$emit(this.GETSQL, msg)
        },
        onSQL: function(callback) {
            this.$on(this.GETSQL, function(msg) {
                callback(msg)
            })
        },
        emit: function(token, msg) {
            this.$emit(this[token], msg)
        },
        on: function(token, callback) {
            this.$on(this[token], function(msg) {
                callback(msg)
            })
        },
    }
})
export default pipeService