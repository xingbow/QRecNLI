import dataService from '../../service/dataService.js'
import pipeService from '../../service/pipeService.js'

export default {
    name: "QueryPanel",
    props: {
        dbselected: "",
        tables: {},
    },
    data() {
        return {
            userText: "",
            popoverVisible: false,
            textOptions: [],
            rowStyle: {
                padding: 2
            }
        }
    },
    mounted() {
        pipeService.onSetQuery(nl => {
            // console.log("nl in querypanel: ", nl)
            this.userText = nl;
        })
    },
    methods: {
        search: function() {
            if (this.userText.length > 0) {
                const userText = this.userText;
                let dbName = this.dbselected;
                dataService.text2SQL([this.userText, dbName], (data) => {
                    const sqlResult = {
                        "sql": data["sql"].trim(),
                        "data": data["data"],
                        "nl": userText.trim()
                    }
                    pipeService.emitSQL(sqlResult);
                    // send "sql" to settings and record sql history
                    if (sqlResult["sql"].length > 0) {
                        dataService.SQL2text(sqlResult["sql"], dbName, (data) => {
                            pipeService.emitSQLTrans(data);
                        });
                        dataService.SQL2VL(sqlResult["sql"], dbName, (data) => {
                            pipeService.emitVLSpecs([data]);
                        });
                        // query suggestions
                        dataService.SQLSugg(dbName, (data) => {
                            console.log("query suggestion after submitting nl query: ", data);
                            pipeService.emitQuerySugg(data);
                        })
                    }
                });
            } else {
                alert("input text is empty");
            }
        },
        onInput: function(input) {
            // console.log(this.textOptions);
            let textOptions = [];
            for (let tableName in this.tables) {
                const columnOptions = this.tables[tableName].map(col => ({
                    type: col[1],
                    colName: col[0],
                    tableName: tableName
                }));
                textOptions = [...textOptions, ...columnOptions];
            }

            const validInput = input.split(',').pop();
            const validOptions = [];
            let tokens = validInput.split(' ');

            // TODO: only consider at most the last three words
            if (tokens.length > 3) {
                tokens = tokens.slice(tokens.length - 3, tokens.length);
            }

            while (tokens.length > 0) {
                const subString = tokens.join(' ');
                for (let optionId in textOptions) {
                    const option = textOptions[optionId];
                    const colName = option.colName;
                    if (colName.match(`^${subString}`)) {
                        option.numToken = tokens.length;
                        validOptions.push(option);
                    }
                }
                tokens = tokens.slice(1, tokens.length);
            }

            this.textOptions = validOptions;
            if (this.textOptions.length > 0) {
                this.popoverVisible = true;
            } else {
                this.popoverVisible = false;
            }
        },

        onBlur: function() {
            this.popoverVisible = false;
        },

        rowClick: function(row, column, event) {
            let tokens = this.userText.split(' ');
            for (let i = 0; i < row.numToken; i++) {
                tokens.pop();
            }
            tokens.push(row.colName);
            this.userText = tokens.join(' ');
        }
    }
}