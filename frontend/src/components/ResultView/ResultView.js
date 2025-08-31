/* global d3 $ */
import pipeService from '../../service/pipeService.js';
import DraggableTop from './Draggable/DraggableTop.vue'
import SQLExplanation from './SQLExplanation.vue'
import draggable from "vuedraggable";
import VueVega from 'vue-vega';
import Vue from 'vue';
import configStorageService from '../../service/configStorageService.js';

Vue.use(VueVega);

export default {
    name: 'ResultView',
    components: {
        SQLExplanation,
        draggable,
        DraggableTop,
    },
    props: {
        dbselected: "",
        tables: {},
    },
    data() {
        return {
            containerId: 'resultContainer',
            nlQuery: "",
            sqlQuery: "",

            // data for query results
            queryReturns: [],

            explanation: "",
            selectDecoded: [],
            whereDecoded: [],
            groupbyDecoded: [],

            visCounter: -1,
            isGenerating: false,
            bookmarkedCharts: new Set(), // Track bookmarked chart IDs
        }
    },
    mounted: function() {
        // Listen for search start to show loading state (only for new searches, not history clicks)
        pipeService.onSearchStart(() => {
            this.isGenerating = true;
        });
        
        pipeService.onSQL(sqlRet => {
            const { sql, nl, SQLTrans, VLSpecs, savedConfigState } = sqlRet;
            this.isGenerating = false; // Hide loading state when results arrive
            
            // Clear existing charts first, but preserve bookmarked ones
            const bookmarkedCharts = this.queryReturns.filter(chart => 
                this.bookmarkedCharts.has(chart.id)
            );
            this.queryReturns = [...bookmarkedCharts];
            this.$nextTick(() => {
                this.sqlQuery = sql;
                this.nlQuery = nl;
                this.explanation = SQLTrans.text;
                // this.selectDecoded = SQLTrans.sqlDecoded['select'][1];
                // this.whereDecoded = SQLTrans.sqlDecoded['where'].filter((d, i) => i % 2 === 0);
                // this.groupbyDecoded = SQLTrans.sqlDecoded['groupBy'];
                const newCharts = VLSpecs.map(query => {
                this.visCounter += 1;
                const chartId = `origin-${this.visCounter}`;
                
                // Use saved state from history click if available, otherwise check storage using nlQuery
                let savedState = savedConfigState;
                if (!savedState) {
                    savedState = configStorageService.getChartState(nl);
                }
                
                return {...query,
                    id: chartId,
                    title: (savedState && savedState.title) || nl, // Use saved title if available
                    sqlQuery: sql,
                    nlQuery: nl,
                    nlExplanation: SQLTrans.text,
                    savedConfig: savedState && savedState.config, // Include saved config for restoration
                    // sqlDecoded: SQLTrans.sqlDecoded,
                };
                });
                
                // Add new charts to existing bookmarked charts
                this.queryReturns = [...this.queryReturns, ...newCharts];
            });
        });
    },
    methods: {
        onDelete: function(index) {
            const deletedChart = this.queryReturns[index];
            if (deletedChart && this.bookmarkedCharts.has(deletedChart.id)) {
                this.bookmarkedCharts.delete(deletedChart.id);
            }
            this.queryReturns.splice(index, 1);
        },
        
        onBookmarkChanged: function(bookmarkData) {
            const { chartId, isBookmarked } = bookmarkData;
            if (isBookmarked) {
                this.bookmarkedCharts.add(chartId);
            } else {
                this.bookmarkedCharts.delete(chartId);
            }
        }
    }
}