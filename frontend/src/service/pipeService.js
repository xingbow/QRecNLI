import Vue from 'vue'

var pipeService = new Vue({
    data: {
        TESTEVENT: 'test_event',

        NLQuery: "NL_Query",
        GETSQL: "GET_SQL",
        SQLTrans: "SQL_trans",
        VLSpecs: "VL_specs",
        SetQuery: "Set_query",
        QuerySugg: "Query_sugg",
        OriginalSugg: "original_sugg"
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
        emitNLQuery: function(msg) {
            this.$emit(this.NLQuery, msg);
        },
        onNLQuery: function(callback) {
            this.$on(this.NLQuery, function(msg) {
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
            this.$emit(this.SetQuery, msg)
        },
        onSetQuery: function(callback) {
            this.$on(this.SetQuery, function(msg) {
                callback(msg)
            })
        },
        emitQuerySugg: function(msg) {
            this.$emit(this.QuerySugg, msg)
        },
        onQuerySugg: function(callback) {
            this.$on(this.QuerySugg, function(msg) {
                callback(msg)
            })
        },
        emitOriginalSugg: function(msg) {
            this.$emit(this.OriginalSugg, msg)
        },
        onOriginalSugg: function(callback) {
            this.$on(this.OriginalSugg, function(msg) {
                callback(msg)
            })
        },
    }
})
export default pipeService