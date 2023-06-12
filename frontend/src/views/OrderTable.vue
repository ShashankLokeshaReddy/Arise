<template>
  <v-container>
    <v-row align="center">
      <v-col align="center" class="mb-4">
        <v-btn class="bordered flex-grow-1 mr-2" @click="runSJF">SJF</v-btn>
        <v-btn class="bordered flex-grow-1 mr-2" @click="runDeadlineFirst">Early Deadline</v-btn>
      </v-col>
      <v-col align="center" class="mb-4">
        <v-btn class="bordered flex-grow-1 mr-2" @click="runPLOptimizer">Preference Optimizer</v-btn>
        <v-btn class="bordered flex-grow-1 mr-2" color="error" @click="stopProcess">Stop Process</v-btn>
      </v-col>
      <v-col align="center" class="mb-4">
        <input type="file" ref="fileInput" @change="handleFileUpload"/>
        <v-btn class="bordered" @click="upload">Upload Job Orders</v-btn>
        <v-btn class="bordered" color="error" @click="deleteJobs">Delete Job Orders</v-btn>
      </v-col>
    </v-row>
  </v-container>

  <v-container v-if="isLoading" fluid justify="center" align="center">
    <v-progress-circular
      :size="70"
      :width="7"
      color="primary"
      indeterminate
    ></v-progress-circular>
  </v-container>

  <v-container v-else fluid justify="center" align="center">
    <ag-grid-vue
      style="width: 1200px; height: 30rem;"
      class="ag-theme-alpine"
      :columnDefs="columnDefs"
      :rowData="rowData"
      display = "flex"
      rowSelection="multiple"
      alignItems="start"
    ></ag-grid-vue>
  </v-container>
</template>

<script lang="ts">
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";
import { AgGridVue } from "ag-grid-vue3";
import { reactive } from "@vue/reactivity";
import axios from "axios";

export default {
  data() {
    return {
      columnDefs: null,
      rowData: null,
      isLoading: false, // new data property for loading state
    };
  },
  components: {
    AgGridVue,
  },

  beforeMount() {
    this.fillTable();
  },

  methods: {
    fillTable() {
      this.columnDefs = [
        { headerName: "FEFCO_Teil", field: "FEFCO_Teil", type: 'rightAligned', filter:true },
        { headerName: "ArtNr_Teil", field: "ArtNr_Teil", type: 'rightAligned', filter:true },
        { headerName: "ID_DRUCK", field: "ID_DRUCK", type: 'rightAligned', filter:true },
        { headerName: "Druckflaeche", field: "Druckflaeche", type: 'rightAligned', filter:true },
        { headerName: "BOGEN_LAENGE_BRUTTO", field: "BOGEN_LAENGE_BRUTTO", type: 'rightAligned', filter:true },
        { headerName: "BOGEN_BREITE_BRUTTO", field: "BOGEN_BREITE_BRUTTO", type: 'rightAligned', filter:true },
        { headerName: "Maschine", field: "Maschine", type: 'rightAligned', filter:true },
        { headerName: "Ruestzeit_Ist", field: "Ruestzeit_Ist", type: 'rightAligned', filter:true },
        { headerName: "Ruestzeit_Soll", field: "Ruestzeit_Soll", type: 'rightAligned', filter:true },
        { headerName: "Laufzeit_Ist", field: "Laufzeit_Ist", type: 'rightAligned', filter:true },
        { headerName: "Laufzeit_Soll", field: "Laufzeit_Soll", type: 'rightAligned', filter:true },
        { headerName: "Zeit_Ist", field: "Zeit_Ist", type: 'rightAligned', filter:true },
        { headerName: "Zeit_Soll", field: "Zeit_Soll", type: 'rightAligned', filter:true },
        { headerName: "Werkzeug_Nutzen", field: "Werkzeug_Nutzen", type: 'rightAligned', filter:true },
        { headerName: "Bestell_Nutzen", field: "Bestell_Nutzen", type: 'rightAligned', filter:true },
        { headerName: "Menge_Soll", field: "Menge_Soll", type: 'rightAligned', filter:true },
        { headerName: "Menge_Ist", field: "Menge_Ist", type: 'rightAligned', filter:true },
        { headerName: "Bemerkung", field: "Bemerkung", type: 'rightAligned', filter:true },
        { headerName: "LTermin", field: "LTermin", type: 'rightAligned', filter:true },
        { headerName: "KndNr", field: "KndNr", type: 'rightAligned', filter:true },
        { headerName: "Suchname", field: "Suchname", type: 'rightAligned', filter:true },
        { headerName: "AKNR", field: "AKNR", type: 'rightAligned', filter:true },
        { headerName: "TeilNr", field: "TeilNr", type: 'rightAligned', filter:true },
        { headerName: "SchrittNr", field: "SchrittNr", type: 'rightAligned', filter:true },
        { headerName: "Start", field: "Start", type: 'rightAligned', filter:true },
        { headerName: "Ende", field: "Ende", type: 'rightAligned', filter:true },
        { headerName: "Summe_Minuten", field: "Summe_Minuten", type: 'rightAligned', filter:true },
        { headerName: "ID_Maschstatus", field: "ID_Maschstatus", type: 'rightAligned', filter:true },
        { headerName: "Maschstatus", field: "Maschstatus", type: 'rightAligned', filter:true },
        { headerName: "Lieferdatum_Rohmaterial", field: "Lieferdatum_Rohmaterial", type: 'rightAligned', filter:true },
        { headerName: "BE_Erledigt", field: "BE_Erledigt", type: 'rightAligned', filter:true }, 
      ];

      fetch("http://localhost:8001/api/jobs/getSchedule")
        .then((res) => res.json())
        .then((rowData) => (this.rowData = rowData["Table"]))
        .catch((error) => console.log(error));
    }
    runPLOptimizer() {
      const confirmed = window.confirm("Möchten Sie den genetischen Optimierer ausführen?");
      if (!confirmed) {
        return;
      }
      this.isLoading = true; // show loading icon
      axios
        .post("http://localhost:8001/api/jobs/run_preference_learning_optimizer/")
        .then((response) => {
          console.log(response.data);
          this.isLoading = false;
          this.fillTable();
        })
        .catch((error) => {
          console.log(error);
        });
    },
    runSJF() {
      const confirmed = window.confirm("Möchten Sie den SJF-Algorithmus ausführen?");
      if (!confirmed) {
        return;
      }
      this.isLoading = true; // show loading icon
      axios
        .post("http://localhost:8001/api/jobs/run_sjf/")
        .then((response) => {
          console.log(response.data);
          this.isLoading = false;
          this.fillTable();
        })
        .catch((error) => {
          console.log(error);
        });
    },
    runDeadlineFirst() {
      const confirmed = window.confirm("Möchten Sie den Early Deadline-Algorithmus ausführen?");
      if (!confirmed) {
        return;
      }
      this.isLoading = true; // show loading icon
      axios
        .post("http://localhost:8001/api/jobs/run_deadline_first/")
        .then((response) => {
          console.log(response.data);
          this.isLoading = false;
          this.fillTable();
        })
        .catch((error) => {
          console.log(error);
        });
    },
    deleteJobs() {
      const confirmed = window.confirm("Would you like to delete all jobs?");
      if (!confirmed) {
        return;
      }
      this.isLoading = true; // show loading icon
      axios
        .post("http://localhost:8001/api/jobs/deleteJobs/")
        .then((response) => {
          console.log(response.data);
          this.isLoading = false;
          window.alert(response.data.message);
          this.fillTable();
        })
        .catch((error) => {
          console.log(error);
        });
    },
    stopProcess() {
      axios
        .post("http://localhost:8001/api/jobs/stop_genetic_optimizer/")
        .then((response) => {
          console.log(response.data);
          this.fillTable();
        })
        .catch((error) => {
          console.log(error);
        });
    },
    handleFileUpload(event) {
      this.file = event.target.files[0];
    },
    upload() {
      const formData = new FormData();
      formData.append('file', this.file);
      this.isLoading = true;
      axios.post('http://localhost:8001/api/jobs/uploadCSV/', formData)
        .then(response => {
          console.log(response.data);
          this.isLoading = false;
          window.alert(response.data.message);
          this.fillTable();
        })
        .catch(error => {
          console.log(error);
        });
      },
    },
  },

};
</script>

<style>
  button.v-btn {
    border: 1px solid #ccc;
    border-radius: 4px;
    padding: 6px 12px; /* smaller padding */
    font-size: 12px; /* smaller font size */
    font-weight: 500;
    text-transform: uppercase;
    color: #333;
    background-color: #fff;
  }

  button.v-btn:hover {
    border-color: #999;
    color: #666;
    background-color: #f5f5f5;
  }

  button.v-btn:active,
  button.v-btn:focus {
    outline: none;
    box-shadow: none;
  }

  label.v-btn {
    border: 1px solid #ccc;
    border-radius: 4px;
    padding: 6px 12px; /* smaller padding */
    font-size: 12px; /* smaller font size */
    font-weight: 500;
    text-transform: uppercase;
    color: #333;
    background-color: #fff;
  }

  label.v-btn:hover {
    border-color: #999;
    color: #666;
    background-color: #f5f5f5;
  }

  label.v-btn:active,
  label.v-btn:focus {
    outline: none;
    box-shadow: none;
  }
</style>
