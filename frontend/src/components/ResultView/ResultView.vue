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
        margin: 5px 10px;
    }

    #vegaLiteContainer {
        height: 480px;
        padding: 5px;
        margin-top:5px;
        overflow: scroll;
    }

    .list-group-item-invisible {
        height: 500px;
        border: none;
    }
</style>