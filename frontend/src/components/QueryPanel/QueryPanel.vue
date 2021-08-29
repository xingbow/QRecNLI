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
  font-size: 10px; 
  color: rgb(131, 127, 127);
}

.next-query-trigger:hover {
  position: absolute;
  font-weight: bold; 
  color: rgb(131, 127, 127);
}
</style>