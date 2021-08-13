import dataService from '../../service/dataService.js'
import pipeService from '../../service/pipeService.js'

export default {
    name: "QueryPanel",
    props: {
        dbselected: "",
    },
    data() {
        return {
            userText: "",
            form: {
                name: '',
                region: '',
                date1: '',
                date2: '',
                delivery: false,
                type: [],
                resource: '',
                desc: ''
              }
        }
    },
    methods: {
        search: function() {
            if (this.userText.length > 0) {
                let userText = this.userText;
                dataService.text2SQL([this.userText, this.dbselected], (data) => {
                    let sqlResult = {
                            "sql": data["data"]["sql"].trim(),
                            "data": data["data"]["data"],
                            "nl": userText.trim()
                        }
                        // send "sql" to settings and record sql history
                    if (sqlResult["sql"].length > 0) {
                        dataService.SQL2text(sqlResult["sql"], this.dbselected, (data) => {
                            sqlResult.explanation = data["data"];
                            dataService.SQL2VL(sqlResult["sql"], this.dbselected, (data) => {
                                sqlResult.vlSpecs = data["data"];
                                pipeService.emitSQL(sqlResult);
                            });
                        });
                    }
                });
            } else {
                alert("input text is empty");
            }
        }
    }
}