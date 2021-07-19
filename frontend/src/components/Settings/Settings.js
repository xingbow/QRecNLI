// /* global d3 $ */
import vSelect from 'vue-select'
import 'vue-select/dist/vue-select.css';
import dataService from '../../service/dataService';

export default {
    name: 'Settings',
    components: {
        vSelect
    },
    props: {
        tableLists: Array,
    },
    data() {
        return {
            containerId: "settingsContainer",
            tabselected: "",
            tableCols: []
        }
    },
    watch: {
        tabselected: function(tabselected){
            if(tabselected.length>0){
                console.log("select table:", tabselected);
                dataService.getTableCols(tabselected, data=>{
                    console.log("columns: ", data["data"]);
                    this.tableCols = data["data"];
                })
            }
        } 
    },
    mounted: function () {
        console.log("this is settings view")
    }
}
