<template src='./ResultView.html'></template>

<script src='./ResultView.js'></script>

<style scoped>
    .card {
        margin-bottom: 10px;
        /* height: 400px; */
        /* border-radius: 5px; */
        border: none;
    }

    .card-block {
        padding: 0px;
        position: relative;
    }

    text {
        font-weight: 300;
        font-family: "Helvetica Neue", Helvetica, Arial, sans-serf;
        font-size: 14px;
    }

    .descriptions {
        font-size: 14px;
        color: gray;
    }

    #resultContainer {
        height: 670px;
        padding: 5px;
        overflow-y: scroll;
    }

    .vis-container {
        display: inline-flex;
    }

    #vegaLiteContainer {
        height: 480px;
        padding: 5px;
        margin-top:5px;
        overflow: scroll;
        border: 1px solid gray;
        overflow: scroll;
    }

    .explanation-container >>> span.column-id {
        background: gold;
    }

    .explanation-container >>> span.entity-id {
        background: #aaa;
    }

    .recommend {
        height: 95px;
        overflow: scroll;
        padding:5px;
        font-size: 12px;
        border: 1px solid lightgray;
    }

    .rowitem {
        font-size: 13px;
        padding: 2px;
        display: flex;
        align-items: center;
    }

    .select-token, .cond-unit-token {
        font-size: 13px;
        border: 1px solid lightgray;
        height: 25px;
        border-radius: 2px;
        align-items: center;
        display: flex;
    }
    .select-token:hover, 
    .cond-unit-token:hover {
        border: 1px solid gray;
    }

    .col-token {
        align-items: center;
        margin: 5px 2px;
        padding-left: 2px;
        height: 20px;
    }

    .col-text, .agg-text {
        margin: 2px;
    }

    .agg-text {
        text-decoration: underline;
    }

    .result-text {
        font-size: 40px;
    }

</style>