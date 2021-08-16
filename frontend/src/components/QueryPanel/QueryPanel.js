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
    mounted() {
        pipeService.onSetQuery(nl=>{
            console.log("nl in querypanel: ", nl)
            this.userText = nl;
        })
    },
    methods: {
        search: function() {
            if (this.userText.length > 0) {
                const userText = this.userText;
                dataService.text2SQL([this.userText, this.dbselected], (data) => {
                    const sqlResult = {
                        "sql": data["sql"].trim(),
                        "data": data["data"],
                        "nl": userText.trim()
                    }
                    pipeService.emitSQL(sqlResult);
                    // send "sql" to settings and record sql history
                    if (sqlResult["sql"].length > 0) {
                        dataService.SQL2text(sqlResult["sql"], this.dbselected, (data) => {
                            pipeService.emitSQLTrans(data);
                        });
                        dataService.SQL2VL(sqlResult["sql"], this.dbselected, (data) => {
                            pipeService.emitVLSpecs(data);
                        });
                    }
                });
            } else {
                alert("input text is empty");
            }
        }
    }
}