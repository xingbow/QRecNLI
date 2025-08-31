<template>
  <div class="explanation-container">
    <div class="rowitem">
      <div class="ex-table-item">SQL</div>
      <span class="ex-table-content">{{ sqlQuery }}</span>
    </div>
    <div class="rowitem">
      <div class="ex-table-item">Trans.</div>
      <span class="explanation-seq" v-html="nlExplanation"></span>
    </div>
  </div>
</template>

<script>
export default {
  name: "SQLExplanation",
  props: {
    sqlQuery: String,
    nlExplanation: String,
    tables: {
      type: Object,
      default: () => {},
    },
  },
};
</script>

<style scoped>
.explanation-container {
    margin: 10px;
}

.explanation-seq >>> span.column-id {
  background: gold;
}

.explanation-seq >>> span.entity-id {
  background: #aaa;
}

.ex-table-item {
  width: 80px;
  font-weight: bold;
}

.ex-table-content {
  max-width: 420px;
}

.rowitem {
  font-size: 13px;
  padding: 2px;
  display: flex;
  align-items: center;
  min-height: 35px;
}
</style>
