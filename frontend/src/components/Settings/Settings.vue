<template src='./Settings.html'></template>

<script src='./Settings.js'></script>

<style scoped>
.card {
  margin-bottom: 10px;
  border-radius: 5px;
  border: none;
}

.card-header {
  font-size: 12px;
  padding: 5px 5px;
  height: 36px;
}

.card-block {
  padding: 0px;
  position: relative;
}

.nav {
  font-size: 13px;
}

#settingsContainer {
  height: 761px;
}

#databaseMeta {
  height: 690px;
  overflow: scroll;
  font-size: 14px;
}

#table-cols {
  font-size: 12px;
}

#data-table {
  font-size: 12px;
  height: 175px;
}

.ghost {
  opacity: 0.5;
  background: #c8ebfb;
}

.history-item-icon,.number-icon {
  position: relative;
  float: right;
  margin-top: 5px;
}

.number-icon {
  font-size: 16px;
  font-weight: bold;
}

.custom-tree-node-text{
  font-size: 18px;
  margin-left: 5px;
}
</style>
