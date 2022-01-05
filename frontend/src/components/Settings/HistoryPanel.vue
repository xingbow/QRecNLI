<template>
  <div id="historyList" style="overflow-y: scroll">
    <draggable
      :list="historyData"
      class="list-group"
      ghost-class="ghost"
      :clone="handleNodeClone"
      :group="{ name: 'historyNode', pull: 'clone', put: false }"
    >
      <div
        class="list-group-item"
        v-for="(element, index) in historyData"
        :key="`${element.key}-${index}`"
        v-on:click="() => handleNodeClick(element.key)"
      >
        <span>{{ element.key }}</span>
        <i
          class="fas fa-chart-bar history-item-icon"
          v-if="element.type === `vega-lite`"
        ></i>
        <i
          class="fas fa-table history-item-icon"
          v-if="element.type === `table`"
        ></i>
        <span v-if="element.type === `data`" class="number-icon">{{
          element.VLSpecs.content
        }}</span>
      </div>
    </draggable>
  </div>
</template>

<script>
// import { defineComponent } from "@vue/composition-api";
import pipeService from "../../service/pipeService";
import draggable from "vuedraggable";

export default {
  name: "HistoryPanel",
  components: { draggable },
  props: {},
  data() {
    return {
      historyData: [],
      visCounter: -1,
    };
  },
  methods: {
    findHistoryNodeByKey(key) {
      for (let hisId in this.historyData) {
        const history = this.historyData[hisId];
        if (history.key == key) {
          return history;
        }
      }
      return undefined;
    },
    handleNodeClick(key) {
      const history = this.findHistoryNodeByKey(key);
      pipeService.emitSQL(history.SQL);
      // pipeService.emitQuerySugg(history.QuerySugg);
      this.historyData.pop();
    },
    handleNodeClone({ key }) {
      this.visCounter += 1;
      const VLSpecs = this.findHistoryNodeByKey(key).VLSpecs;
      return { ...VLSpecs, id: `history-${this.visCounter}` };
    },
  },
  mounted: function () {
    pipeService.onSQL((sqlRet) => {
      const { sql, nl, SQLTrans, VLSpecs } = sqlRet;
      const histNode = {
        SQL: sqlRet,
        key: nl,
        SQLTrans: SQLTrans,
      };

      if (VLSpecs.length > 0) {
        histNode.type = VLSpecs[0].type;
        histNode.VLSpecs = {
          ...VLSpecs[0],
          title: nl,
          sqlQuery: sql,
          nlQuery: nl,
          nlExplanation: SQLTrans.text,
          sqlDecoded: SQLTrans.sqlDecoded,
        };
      }
      this.historyData.push(histNode);
    });

    // pipeService.onSetQuery(SetQuery => {
    //     this.historyData[this.historyData.length - 1].SetQuery = SetQuery;
    // });

    // pipeService.onQuerySugg(QuerySugg => {
    //     this.historyData[this.historyData.length - 1].QuerySugg = QuerySugg;
    // });
  },
};
</script>

<style scoped>
.ghost {
  opacity: 0.5;
  background: #c8ebfb;
}

.history-item-icon,
.number-icon {
  position: relative;
  float: right;
  margin-top: 5px;
}

.number-icon {
  font-size: 16px;
  font-weight: bold;
}
</style>
