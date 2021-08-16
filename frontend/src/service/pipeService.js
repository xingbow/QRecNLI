import Vue from 'vue'

var pipeService = new Vue({
    data: {
        TESTEVENT: 'test_event',
        GETSQL: "GET_SQL",
        SQLTrans: "SQL_trans",
        VLSpecs: "VL_specs",
        setQuery: "set_query",
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
        emitSQLTrans: function(msg) {
            this.$emit(this.SQLTrans, msg)
        },
        onSQLTrans: function(callback) {
            this.$on(this.SQLTrans, function(msg) {
                callback(msg)
            })
        },
        emitVLSpecs: function(msg) {
            this.$emit(this.VLSpecs, msg)
        },
        onVLSpecs: function(callback) {
            this.$on(this.VLSpecs, function(msg) {
                callback(msg)
            })
        },
        emitSetQuery: function(msg) {
            this.$emit(this.setQuery, msg)
        },
        onSetQuery: function(callback) {
            this.$on(this.setQuery, function(msg) {
                callback(msg)
            })
        },
    }
})
export default pipeService