// /* global d3 $ */
import vSelect from 'vue-select'
import 'vue-select/dist/vue-select.css';
import dataService from '../../service/dataService';
import Tabulator from 'tabulator-tables';

export default {
    name: 'Settings',
    components: {
        vSelect,
    },
    props: {
        tableLists: Array,
    },
    data() {
        return {
            containerId: "settingsContainer",
            tabselected: "",
            tableCols: [],
        }
    },
    watch: {
        tabselected: function(tabselected){
            if(tabselected.length>0){
                console.log("select table:", tabselected);
                dataService.getTableCols(tabselected, data=>{
                    console.log("columns: ", data["data"]);
                    let tableCols = data["data"];
                    dataService.loadTablesContent(tabselected, (data)=> {
                        this.tableCols = tableCols
                        this.dataTable.setData(data["data"].slice(0,(data["data"].length >= 5) ? 5 : data["data"].length));
                    })
                })
            }
        } 
    },
    mounted: function () {
        console.log("this is settings view");
        //initialize table
        this.dataTable = new Tabulator("#data-table", {
            // data:tabledata, //assign data to table
            autoColumns:true, //create columns from data field names
            // pagination:"local",       //paginate the data
            // paginationSize:5,
        });
    }
}
