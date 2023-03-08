<template src="./QueryPanel.html"></template>

<script src="./QueryPanel.js"></script>

<style scoped>
.input-group {
  font-size: 14px;
}

.input-body {
  width: calc(100% - 100px);
}

.speaker:hover {
  /* color: #fff !important; */
  text-decoration: none;
}

.table-name-cell {
  border: 1px solid lightgray;
  border-radius: 5px;
  align-items: center;
  justify-content: center;
}

.next-query-trigger {
  position: absolute;
  top: 55px;
  font-size: 14px;
  font-weight: bold;
  color: rgb(148, 145, 145);
}

.next-query-trigger:hover {
  position: absolute;
  color: rgb(131, 127, 127);
}

.recommend-container {
  width: calc(100% - 100px);
}

.recommend {
  /* height: 95px; */
  overflow: scroll;
  /* padding:5px; */
  margin-top: 10px;
  /* border: 1px solid lightgray; */
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
}

.rowitem,
.recommend-item {
  font-size: 16px;
  padding: 2px;
  display: flex;
  align-items: center;
}

.recommend-item {
  border: 1px solid white;
  border-radius: 5px;
  text-decoration: underline;
}

.recommend-item:hover {
  border: 1px solid #409eff;
  border-radius: 5px;
}
</style>