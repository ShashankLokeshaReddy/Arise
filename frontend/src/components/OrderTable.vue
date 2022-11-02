<template>
  <div style="align: center;">
  <ag-grid-vue
    style="width: 1500px; height: 200px;"
    class="ag-theme-alpine"
    :columnDefs="columnDefs"
    :rowData="rowData"
    rowSelection="multiple"
  >
  </ag-grid-vue>
</div>
</template>

<script lang="ts">
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";
import { AgGridVue } from "ag-grid-vue3";
import { reactive } from '@vue/reactivity';

export default {
  data(){
    return {
      columnDefs: null,
      rowData: null,
    };
  },
  components: {
    AgGridVue,
  },
  
  beforeMount() {
      this.columnDefs = [
        { headerName: "Maschine", field: "resourceId", filter: true },
        { headerName: "Kundennummer", field: "title" , filter:true},
        { headerName: "Startzeit", field: "start", filter:true },
        { headerName: "Endzeit", field: "end", filter:true },
        { headerName: "Auftragsnummer", field: "AKNR", filter:true },
        { headerName: "Schrittnummer", field: "SchrittNr", filter:true },
      ];
     /* this.rowData =[
        { make: "Toyota", model: "Celica", price: 35000 },
        { make: "Ford", model: "Mondeo", price: 32000 },
        { make: "Porsche", model: "Boxster", price: 72000 },
      ];*/
      fetch('http://localhost:8000/api/machines/')
        .then(res => res.json())
        .then(rowData => this.rowData = rowData)
        .catch(error => console.log(error));
    },
    
  }
</script>