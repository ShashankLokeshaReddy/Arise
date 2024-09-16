<template>
  <v-container>
    <v-row align="center" class="mb-4">
      <v-col align="center">
      <div class="date-input-container">
          <button class="custom-button" @click="runSJF">SJF</button>
          <button class="custom-button" @click="runDeadlineFirst">Early Deadline</button>
        </div>
        <div class="date-input-container">
          <button class="custom-button" @click="runPLOptimizer_IEM">PL mit Randbedingungen</button>
          <button class="custom-button" @click="runPLOptimizer_Bielefeld">PL ohne Randbedingungen</button>
        </div>
      </v-col>
      <v-col align="center">
        <div class="date-input-container">
          <label for="startDate" class="date-label">LTermin Zwischen</label>
        </div>
        <div class="date-input-container">
          <input v-model="startDate" type="date" id="startDate" class="date-input">
          <input v-model="endDate" type="date" id="endDate" class="date-input">
        </div>
        <button class="custom-button" @click="getUnSchedJobs(startDate, endDate)">Jobs abrufen</button>
        <button class="custom-button" @click="saveJobs">Jobs speichern</button>
      </v-col>
      <v-col align="center">
        <input type="file" ref="fileInput" @change="handleFileUpload" class="date-input">
        <button class="custom-button" @click="upload">Arbeitsaufträge hochladen</button>
        <button class="custom-button" @click="deleteJobs">Arbeitsaufträge löschen</button>
      </v-col>
    </v-row>
  </v-container>

  <v-container v-if="isLoading" fluid justify="center" align="center">
    <v-progress-circular
      :size="70"
      :width="7"
      color="blue"
      indeterminate
    ></v-progress-circular>
  </v-container>

  <v-container v-else fluid justify="center" align="center">
    <ag-grid-vue
      style="width: 1200px; height: 30rem;"
      class="ag-theme-alpine"
      :columnDefs="columnDefs"
      :rowData="rowData"
      display="flex"
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
    getUnSchedJobs(startDate, endDate) {
      const confirmed = window.confirm("Möchten Sie alle neuen Jobs aus der Datenbank abrufen?");
      if (!confirmed) {
        return;
      }
      this.isLoading = true; // show loading icon
        const info_json = {
          info_start: startDate,
          info_end: endDate
        };
        const formData = new FormData();
        for (let key in info_json) {
            formData.append(key, info_json[key]);
        }
      axios
        .post('http://' + window.location.hostname + ':8001/api/jobs/getSchulteDataUnscheduled/', formData)
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
    saveJobs() {
      const confirmed = window.confirm("Möchten Sie alle Jobs in einer CSV-Datei speichern?");
      if (!confirmed) {
        return;
      }
      this.isLoading = true; // show loading icon
      axios
        .post('http://' + window.location.hostname + ':8001/api/jobs/savejobstoCSV/')
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
    fillTable() {
      // Define saveButtonRenderer
      const saveButtonRenderer = params => {
        const button = document.createElement('button')
        button.innerText = 'Save'
        button.addEventListener('click', () => {
          const rowData = params.node.data
          const jobs_data = {
            Fefco_Teil: rowData.Fefco_Teil,
            ArtNr_Teil: rowData.ArtNr_Teil,
            ID_Druck: rowData.ID_Druck,
            Druckflaeche: rowData.Druckflaeche,
            Bogen_Laenge_Brutto: rowData.Bogen_Laenge_Brutto,
            Bogen_Breite_Brutto: rowData.Bogen_Breite_Brutto,
            Maschine: rowData.Maschine,
            Ruestzeit_Ist: rowData.Ruestzeit_Ist,
            Ruestzeit_Soll: rowData.Ruestzeit_Soll,
            Laufzeit_Ist: rowData.Laufzeit_Ist,
            Laufzeit_Soll: rowData.Laufzeit_Soll,
            Zeit_Ist: rowData.Zeit_Ist,
            Zeit_Soll: rowData.Zeit_Soll,
            Werkzeug_Nutzen: rowData.Werkzeug_Nutzen,
            Bestell_Nutzen: rowData.Bestell_Nutzen,
            Menge_Soll: rowData.Menge_Soll,
            Menge_Ist: rowData.Menge_Ist,
            Bemerkung: rowData.Bemerkung,
            LTermin: rowData.LTermin,
            KndNr: rowData.KndNr,
            Laufzeit_Soll: rowData.Laufzeit_Soll,
            Suchname: rowData.Suchname,
            TeilNr: rowData.TeilNr,
            SchrittNr: rowData.SchrittNr,
            Start: rowData.Start,
            Ende: rowData.Ende,
            Summe_Minuten: rowData.Summe_Minuten,
            ID_Maschstatus: rowData.ID_Maschstatus,
            Maschstatus: rowData.Maschstatus,
            Lieferdatum_Rohmaterial: rowData.Lieferdatum_Rohmaterial,
            BE_Erledigt: rowData.BE_Erledigt     
          };

          const formData = new FormData();
          for (let key in jobs_data) {
          formData.append(key, jobs_data[key]);
          }
          
          axios.post('http://' + window.location.hostname + ':8001/api/jobs/setInd_Table/', formData)
          .then(response => {
              console.log(response.data);
          })
          .catch(error => {
              console.log(error);
          });

        })
        return button
      }

      this.columnDefs = [
        { headerName: "AKNR", field: "AKNR", type: 'rightAligned', filter:true },
        { headerName: "Fefco_Teil", field: "Fefco_Teil", type: 'rightAligned', filter:true },
        { headerName: "ArtNr_Teil", field: "ArtNr_Teil", type: 'rightAligned', filter:true },
        { headerName: "ID_Druck", field: "ID_Druck", type: 'rightAligned', filter:true },
        { headerName: "Druckflaeche", field: "Druckflaeche", type: 'rightAligned', filter:true },
        { headerName: "Bogen_Laenge_Brutto", field: "Bogen_Laenge_Brutto", type: 'rightAligned', filter:true },
        { headerName: "Bogen_Breite_Brutto", field: "Bogen_Breite_Brutto", type: 'rightAligned', filter:true },
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

      fetch('http://' + window.location.hostname + ':8001/api/jobs/getSchedule')
        .then((res) => res.json())
        .then((rowData) => (this.rowData = rowData["Table"]))
        .catch((error) => console.log(error));
    },
    runGeneticOptimizer() {
      const confirmed = window.confirm("Möchten Sie den genetischen Optimierer ausführen?");
      if (!confirmed) {
        return;
      }
      this.isLoading = true; // show loading icon
      axios
        .post('http://' + window.location.hostname + ':8001/api/jobs/run_preference_learning_optimizer/')
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
        .post('http://' + window.location.hostname + ':8001/api/jobs/run_sjf/')
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
    runDeadlineFirst() {
      const confirmed = window.confirm("Möchten Sie den Early Deadline-Algorithmus ausführen?");
      if (!confirmed) {
        return;
      }
      this.isLoading = true; // show loading icon
      axios
        .post('http://' + window.location.hostname + ':8001/api/jobs/run_deadline_first/')
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
    runPLOptimizer_IEM() {
      const confirmed = window.confirm("Möchten Sie den PL-Algorithmus ausführen?");
      if (!confirmed) {
        return;
      }
      this.isLoading = true; // show loading icon
      axios
        .post('http://' + window.location.hostname + ':8001/api/jobs/run_preference_learning_optimizer_IEM/')
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
    runPLOptimizer_Bielefeld() {
      const confirmed = window.confirm("Möchten Sie den PL-Algorithmus ausführen?");
      if (!confirmed) {
        return;
      }
      this.isLoading = true; // show loading icon
      axios
        .post('http://' + window.location.hostname + ':8001/api/jobs/run_preference_learning_optimizer_Bielefeld/')
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
    deleteJobs() {
      const confirmed = window.confirm("Möchten Sie alle Jobs löschen?");
      if (!confirmed) {
        return;
      }
      this.isLoading = true; // show loading icon
      axios
        .post('http://' + window.location.hostname + ':8001/api/jobs/deleteJobs/')
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
        .post('http://' + window.location.hostname + ':8001/api/jobs/stop_PL_optimizer/')
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
      axios.post('http://' + window.location.hostname + ':8001/api/jobs/uploadCSV/', formData)
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
.custom-button {
  border: 1px solid #ccc;
  font-family: 'Roboto', sans-serif;
  border-radius: 4px;
  padding: 6px 12px;
  font-size: 12px;
  font-weight: 500;
  text-transform: uppercase;
  color: #000000;
  background-color: #f1f1f1;
  margin-right: 8px;
  margin-bottom: 8px;
}

.custom-button:hover {
  border-color: #999;
  color: blue;
  background-color: #f1f1f1;
}

.custom-button:active,
.custom-button:focus {
  outline: none;
  box-shadow: none;
}

.date-input {
  margin-right: 0.5rem;
  padding: 0.25rem;
  margin-bottom: 8px;
}

.date-label {
  font-size: 12px;
  font-weight: 500;
  text-transform: uppercase;
  color: #333;
  background-color: transparent;
  font-family: 'Roboto', sans-serif;
  margin-right: 4px;
  margin-bottom: 8px;
}
</style>

