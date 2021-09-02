<template>
  <div class="explanation-container">
    <div class="rowitem">
      <div class="ex-table-item">SQL</div>
      <span>{{ sqlQuery }}</span>
    </div>
    <div class="rowitem">
      <div class="ex-table-item">Trans.</div>
      <span class="explanation-seq" v-html="nlExplanation"></span>
    </div>
    <div class="rowitem">
      <div class="ex-table-item">Select</div>
      <div class="token-list">
        <div
          class="rowitem"
          v-for="(selectUnit, index) in selectDecoded"
          v-bind:key="index"
        >
          <SelectToken :selectUnit="selectUnit" :tables="tables" />
        </div>
      </div>
    </div>
    <div class="rowitem">
      <div class="ex-table-item">Groupby</div>
      <div class="token-list">
        <div
          class="rowitem"
          v-for="(colUnit, index) in groupbyDecoded"
          v-bind:key="index"
        >
          <ColUnitToken :colUnit="colUnit" :tables="tables" />
        </div>
      </div>
    </div>
    <div class="rowitem">
      <div class="ex-table-item">Filters</div>
      <div class="token-list">
        <div
          class="rowitem"
          v-for="(condUnit, index) in whereDecoded"
          v-bind:key="index"
        >
          <CondUnitToken :condUnit="condUnit" :tables="tables" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { CondUnitToken, SelectToken, ColUnitToken } from "./SQLToken.js";

export default {
  name: "SQLExplanation",
  components: { CondUnitToken, SelectToken, ColUnitToken },
  props: {
    sqlQuery: String,
    nlExplanation: String,
    selectDecoded: {
      type: Array,
      default: () => [],
    },
    groupbyDecoded: {
      type: Array,
      default: () => [],
    },
    whereDecoded: {
      type: Array,
      default: () => [],
    },
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

.select-token,
.cond-unit-token {
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

.col-text,
.agg-text {
  margin: 2px;
}

.agg-text {
  text-decoration: underline;
}

.ex-table-item {
  width: 80px;
  font-weight: bold;
}

.rowitem {
  font-size: 13px;
  padding: 2px;
  display: flex;
  align-items: center;
  min-height: 35px;
}

.token-list {
  /* width: 300px; */
  display: flex;
  flex-wrap: wrap;
}
</style>
