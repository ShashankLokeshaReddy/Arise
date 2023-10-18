<template>
  <div>
    <!-- FullCalendar component with loading overlay -->
    <div class="calendar-container">
      <div v-if="isLoading" class="loading-overlay">
        <v-progress-circular
          :size="70"
          :width="7"
          color="blue"
          indeterminate
        ></v-progress-circular>
      </div>

      <FullCalendar ref="machinecalendar" :options="calendarOptions"></FullCalendar>
    </div>

    <!-- Event details popup -->
    <v-dialog v-model="showEventPopup" max-width="700px">
      <v-card class="event-popup">
        <v-card-title>
          <span class="headline">Jobdetails</span>
        </v-card-title>
        <v-card-text>
          <p>Fefco_Teil: {{ selectedEvent.extendedProps.Fefco_Teil }}</p>
          <p>ArtNr_Teil: {{ selectedEvent.extendedProps.ArtNr_Teil }}</p>
          <p>AKNR: {{ selectedEvent.extendedProps.AKNR }}</p>
          <p>TeilNr: {{ selectedEvent.extendedProps.TeilNr }}</p>
          <p>SchrittNr: {{ selectedEvent.extendedProps.SchrittNr }}</p>
          <p>Ruestzeit Soll: {{ selectedEvent.extendedProps.Ruestzeit_Soll }}</p>
          <p>Bemerkung: {{ selectedEvent.extendedProps.Bemerkung }}</p>
          <p>Suchname: {{ selectedEvent.extendedProps.Suchname }}</p>
          <p>Maschine: {{ selectedEvent.extendedProps.machines }}</p>
          <p>Start: {{ selectedEvent.extendedProps.Start }}</p>
          <p>Ende: {{ selectedEvent.extendedProps.Ende }}</p>
          <p>Lieferdatum_Rohmaterial: {{ selectedEvent.extendedProps.Lieferdatum_Rohmaterial }}</p>
          <p>LTermin: {{ selectedEvent.extendedProps.LTermin }}</p>
        </v-card-text>
        <v-card-actions>
          <v-btn color="blue darken-1" text @click="closeEventPopup" class="close-button">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script lang="ts">

import { defineComponent } from 'vue'
import '@fullcalendar/core/vdom'
import FullCalendar from '@fullcalendar/vue3'
import DayGridPlugin from '@fullcalendar/daygrid'
import TimegridPlugin from '@fullcalendar/timegrid'
import InteractionPlugin from '@fullcalendar/interaction'
import ListPlugin from '@fullcalendar/list'
import ResourceTimelinePlugin from '@fullcalendar/resource-timeline'
import axios from 'axios'
import moment from 'moment';

export default defineComponent({
     
    //props: [FullCalendar],
    components: {FullCalendar},
    data()  {
        return {
            fetchScheduledJobs: false,
            selectedEvent: null,
            showEventPopup: false,
            isLoading: false,
            calendarApi: null,
            calendarOptions: {
            plugins: [ 
                DayGridPlugin,
                TimegridPlugin,
                InteractionPlugin,
                ListPlugin,
                ResourceTimelinePlugin,
            ],
            selectOverlap: true,
            eventOverlap: true,
            eventMaxStack: 3,
            slotDuration: '00:05:00',
            resourceAreaWidth: "10%",
            scrollTimeReset: false,
            slotLabelContent: ({ date }) => {
                const hour = date.getHours();
                const minute = date.getMinutes();
                const startHour = 0;
                const endHour = 24;
            },
            slotLabelClassNames: ({ date, isLabel }) => {
                const hour = date.getHours();
                const classNames = ["slot-label"];
                const formattedDate = date.toISOString().substring(0, 10);
                const formattedDate_substr = date.toISOString().substring(5, 10);
                if ((formattedDate_substr >= '12-23' && formattedDate_substr <= '12-31')) {
                    classNames.push("holiday-non-operating-hours");
                } else if ( ([0, 6].includes(date.getDay())) ) {
                    classNames.push("weekend-non-operating-hours");
                } else {
                    classNames.push("operating-hours");
                }
                
                if (isLabel) {
                    classNames.push("date-label");
                }

                return classNames.join(" ");
            },
            slotLaneClassNames: ({ date, isLabel }) => {
                const hour = date.getHours();
                const classNames = ["slot-label"];
                const formattedDate = date.toISOString().substring(0, 10);
                const formattedDate_substr = date.toISOString().substring(5, 10);
                if ((formattedDate_substr >= '12-23' && formattedDate_substr <= '12-31')) {
                    classNames.push("holiday-non-operating-hours");
                } else if ( ([0, 6].includes(date.getDay())) ) {
                    classNames.push("weekend-non-operating-hours");
                } else {
                    classNames.push("operating-hours");
                }
                
                if (isLabel) {
                    classNames.push("date-label");
                }

                return classNames.join(" ");
            },
            locale: "ger",
            initialView: 'resourceTimelineDay',
            datesSet: this.handleDatesSet,
            schedulerLicenseKey: 'CC-Attribution-NonCommercial-NoDerivatives',
            headerToolbar: {
                left: 'prev today next toggleSwitch',
                center: 'title',
                right: 'resourceTimelineYear resourceTimelineMonth resourceTimelineWeek resourceTimelineDay myCustomButton',
            },
            customButtons: {
                myCustomButton: {
                    text: 'speichern',
                    click: function() {
                        const confirmed = window.confirm("Möchten Sie alle Jobs in einer CSV-Datei speichern?");
                        if (!confirmed) {
                            return;
                        }
                        axios
                            .post('http://' + window.location.hostname + ':8001/api/jobs/savejobstoCSV/')
                            .then((response) => {
                            console.log(response.data);
                            this.isLoading = false;
                            window.alert(response.data.message);
                            //this.fillTable();
                            })
                            .catch((error) => {
                                console.log(error);
                            });
                    }
                },
                toggleSwitch: {
                    text: 'Geplante Jobs abrufen',
                    click: () => {
                        this.fetchScheduledJobs = !this.fetchScheduledJobs;
                    },
                },
            },
            weekends: true,
            editable: true,
            
            resourceAreaColumns: [
                {
                field: 'title',
                headerContent: 'Maschinen'
                }
            ],

            resources: [],
            events: [] as { resourceId : string; title: string; start: Date; end: Date; eventTextColor : string;}[],
            eventClick: (info) => {
                this.selectedEvent = info.event;
                this.showEventPopup = true; // Open the popup
            },
            eventDidMount: (info) => {
                const setupTimeMinutes = info.event.extendedProps.Ruestzeit_Soll;
                const setupTimeDuration = setupTimeMinutes * 60 * 1000;
                const delta = (setupTimeDuration / (info.event.end - info.event.start)) * 100;

                if (info.event.classNames[0] === "fwd") {
                    info.el.style.background = `linear-gradient(90deg, grey ${delta}%, blue 0%)`;
                } else if (info.event.classNames[0] === "fwd_db") {
                    info.el.style.background = `linear-gradient(90deg, grey ${delta}%, green 0%)`;
                }

                info.el.style.color = "white";
            },
            eventResize: (info) => {
                if(info.event.classNames[0] !== "fwd_db"){
                    // Get the selected machine
                    var resources = info.event.getResources();
                    var selectedMachine = resources[0]["title"];
                    var machines = info.event.extendedProps.machines;
                    var allowedMachines = machines.split(',');
                    const setupTimeMinutes = info.event.extendedProps.Ruestzeit_Soll;
                    const setupTimeDuration = setupTimeMinutes * 60 * 1000;
                    const delta = (setupTimeDuration / (info.event.end - info.event.start)) * 100;

                    if (delta > 100) {
                        info.revert();
                        alert('Eine Bewegung ist nicht zulässig, da die gesamte Produktionsdauer kürzer ist als die Rüstzeit, was unpraktisch ist');
                    }
                    else if (allowedMachines.includes(selectedMachine)) {
                        const start_s = new Date(info.event.start.getTime() + setupTimeDuration);
                        const startISOString = start_s.toISOString().substring(0, 19) + "Z";
                        const end_s = new Date(info.event.end);
                        const endISOString = end_s.toISOString().substring(0, 19) + "Z";
                        info.event.setExtendedProp('Start', startISOString)
                        info.event.setExtendedProp('Ende', endISOString)

                        const jobs_data = {
                            AKNR: info.event.extendedProps.AKNR,
                            TeilNr: info.event.extendedProps.TeilNr,
                            SchrittNr: info.event.extendedProps.SchrittNr,
                            Ruestzeit_Soll: info.event.extendedProps.Ruestzeit_Soll,
                            Fefco_Teil: info.event.extendedProps.Fefco_Teil,
                            ArtNr_Teil: info.event.extendedProps.ArtNr_Teil,
                            Start: startISOString,
                            Ende: endISOString,
                            Maschine: selectedMachine
                        };

                        if (info.event.classNames[0] === "fwd") {
                            info.el.style.background = `linear-gradient(90deg, grey ${delta}%, blue 0%)`;
                        } else if (info.event.classNames[0] === "fwd_db") {
                            info.el.style.background = `linear-gradient(90deg, grey ${delta}%, green 0%)`;
                        }

                        const formData = new FormData();
                        for (let key in jobs_data) {
                            formData.append(key, jobs_data[key]);
                        }
                        axios.post('http://' + window.location.hostname + ':8001/api/jobs/setInd/', formData)
                        .then(response => {
                            console.log(response.data);
                        })
                        .catch(error => {
                            console.log(error);
                        });
                    } 
                    else {
                        // If the selected machine is not allowed, revert the event to its original position
                        info.revert();
                        alert('Das Ereignis kann nicht gelöscht werden, da es Einschränkungen für die Ausführung auf folgenden Computern hat: ' + info.event.extendedProps.machines);
                    }
                }
                else {
                    // If the selected machine is not allowed, revert the event to its original position
                    info.revert();
                    alert('Auf den bereits geplanten Veranstaltungen ist die Bewegung nicht gestattet');
                }
            },
            eventDrop: (info) => {
                if(info.event.classNames[0] !== "fwd_db"){
                    // Get the selected machine
                    var resources = info.event.getResources();
                    var selectedMachine = resources[0]["title"];
                    var machines = info.event.extendedProps.machines;
                    var allowedMachines = machines.split(',');
                    const setupTimeMinutes = info.event.extendedProps.Ruestzeit_Soll;
                    const setupTimeDuration = setupTimeMinutes * 60 * 1000;
                    const delta = (setupTimeDuration / (info.event.end - info.event.start)) * 100;

                    // Check whether the selected machine is allowed
                    if (allowedMachines.includes(selectedMachine)) {
                        const start_s = new Date(info.event.start.getTime() + setupTimeDuration);
                        const startISOString = start_s.toISOString().substring(0, 19) + "Z";
                        const end_s = new Date(info.event.end);
                        const endISOString = end_s.toISOString().substring(0, 19) + "Z";
                        info.event.setExtendedProp('Start', startISOString)
                        info.event.setExtendedProp('Ende', endISOString)

                        const jobs_data = {
                            AKNR: info.event.extendedProps.AKNR,
                            TeilNr: info.event.extendedProps.TeilNr,
                            SchrittNr: info.event.extendedProps.SchrittNr,
                            Ruestzeit_Soll: info.event.extendedProps.Ruestzeit_Soll,
                            Fefco_Teil: info.event.extendedProps.Fefco_Teil,
                            ArtNr_Teil: info.event.extendedProps.ArtNr_Teil,
                            Start: startISOString,
                            Ende: endISOString,
                            Maschine: selectedMachine
                        };

                        const formData = new FormData();
                        for (let key in jobs_data) {
                            formData.append(key, jobs_data[key]);
                        }
                        axios.post('http://' + window.location.hostname + ':8001/api/jobs/setInd/', formData)
                        .then(response => {
                            console.log(response.data);
                        })
                        .catch(error => {
                            console.log(error);
                        });
                    } 
                    else {
                        // If the selected machine is not allowed, revert the event to its original position
                        info.revert();
                        alert('Das Ereignis kann nicht gelöscht werden, da es Einschränkungen für die Ausführung auf folgenden Computern hat: ' + info.event.extendedProps.machines);
                    }
                }
                else {
                    // If the selected machine is not allowed, revert the event to its original position
                    info.revert();
                    alert('Auf den bereits geplanten Veranstaltungen ist die Bewegung nicht gestattet');
                }
            },

            },
        }
    },
    methods: {
        closeEventPopup() {
            this.showEventPopup = false;
            // this.selectedEvent = null;
        },
        handleButtonClick() {
            if (this.fetchScheduledJobs) {
                // Method to be invoked when a button is clicked
                this.isLoading = true;
                const calendarApi = this.$refs.machinecalendar.getApi();
                const { activeStart, activeEnd} = calendarApi.view;
                console.log('Button clicked:', calendarApi.view, activeStart, activeEnd);
                const info_json = {
                    info_start: activeStart,
                    info_end: activeEnd
                };
                const formData = new FormData();
                for (let key in info_json) {
                    formData.append(key, info_json[key]);
                }
                axios.post('http://' + window.location.hostname + ':8001/api/jobs/getSchulteData/', formData)
                    .then(response => {
                    var output_resp = response.data;
                    var output = output_resp["Schulte_data"];

                    var events_var_db = [];
                    for (var i = 0; i < output.length; ++i) {
                        if (output[i]["Ende"] === null) {
                        output[i]["Ende"] = output[i]["end"];
                        }
                        var temp_event = {
                            "resourceId": output[i]["Maschine"],
                            "title": output[i]["AKNR"] + "-" + output[i]["Suchname"],
                            "start": output[i]["Start"],
                            "end": output[i]["Ende"],
                            "eventColor": "green",
                            "display": 'auto',
                            "className": "fwd_db",
                            "extendedProps": {
                                "machines": output[i]["Maschine"],
                                "AKNR": output[i]["AKNR"],
                                "TeilNr": output[i]["TeilNr"],
                                "SchrittNr": output[i]["SchrittNr"],
                                "Ruestzeit_Soll": output[i]["Ruestzeit_Soll"],
                                "Bemerkung": output[i]["Bemerkung"],
                                "Suchname": output[i]["Suchname"],
                                "Fefco_Teil": output[i]["Fefco_Teil"],
                                "ArtNr_Teil": output[i]["ArtNr_Teil"],
                                "Start": output[i]["Start"],
                                "Ende": output[i]["Ende"],
                                "Lieferdatum_Rohmaterial": output[i]["Lieferdatum_Rohmaterial"],
                                "LTermin": output[i]["LTermin"]
                            }
                        };
                        events_var_db.push(temp_event);
                    }

                    var resources_var_db = [];

                    for (var i = 0; i < output.length; ++i) {
                        var temp_res = {
                        "id": output[i]["Maschine"],
                        "title": output[i]["Maschine"]
                        };
                        resources_var_db.push(temp_res);
                    }

                    // Merge events_var_db with existing events
                    this.calendarOptions.events = this.calendarOptions.events.filter(event => {
                        return !event.className.includes("fwd_db");
                    }).concat(events_var_db);

                    // Merge resources_var_db with existing resources
                    resources_var_db.forEach(resource => {
                        const existingResource = this.calendarOptions.resources.find(r => r.id === resource.id);
                        if (!existingResource) {
                        this.calendarOptions.resources.push(resource);
                        }
                    });
                    this.isLoading = false;
                    // Log the number of events
                    console.log("No. of events", this.calendarOptions.events.length);
                    })
                    .catch(error => {
                    console.log(error);
                    this.isLoading = false;
                    });
            }
            else{
                // Remove events with the 'fwd_db' class
                this.isLoading = true;
                this.calendarOptions.events = this.calendarOptions.events.filter(
                (event) => !event.className.includes('fwd_db')
                );

                // Get the resource IDs associated with remaining events
                const remainingResourceIds = this.calendarOptions.events
                .filter((event) => event.className.includes('fwd'))
                .map((event) => event.resourceId);

                // Remove resources not associated with 'fwd' events
                this.calendarOptions.resources = this.calendarOptions.resources.filter((resource) =>
                remainingResourceIds.includes(resource.id)
                );
                this.isLoading = false;
            }
        },
    },
    mounted() {
        // Register click event listeners for the buttons
        const buttons = document.querySelectorAll('.fc-button');
        buttons.forEach((button) => {
        button.addEventListener('click', (event) => {
            const buttonName = event.target.getAttribute('data-navlink');
            this.handleButtonClick();
        });
        });
    },
    async created(){
        var response = await fetch('http://' + window.location.hostname + ':8001/api/jobs/getSchedule')
        var output_resp = await response.json()
        var status = output_resp["Status"]
        var output : { Maschine: string; machines: string; AKNR: string; TeilNr: string; SchrittNr: string; item: string; Start: Date, Ende: Date }[] = [];
        output = output_resp["Table"]
        
        var events_var = []
        for (var i = 0; i < output.length; ++i) {
            var start_date_str = output[i]["Start"];
            var minutes_to_add = output[i]["Ruestzeit_Soll"];
            var start_date = new Date(start_date_str);
            var end_date = new Date(start_date.getTime() - minutes_to_add * 60000);
            var adjustedStartTime = end_date.toISOString().slice(0, 19) + "Z";

            var temp_event = {
                "resourceId":output[i]["Maschine"],
                "title":output[i]["AKNR"] + "-" + output[i]["Suchname"],
                "start":adjustedStartTime,
                "end":output[i]["Ende"],
                "eventColor":"blue",
                "display":'auto',
                "className": "fwd",
                "extendedProps": {
                    "machines": output[i]["Maschine"],
                    "AKNR": output[i]["AKNR"],
                    "TeilNr": output[i]["TeilNr"],
                    "SchrittNr": output[i]["SchrittNr"],
                    "Ruestzeit_Soll": output[i]["Ruestzeit_Soll"],
                    "Bemerkung": output[i]["Bemerkung"],
                    "Suchname": output[i]["Suchname"],
                    "Fefco_Teil": output[i]["Fefco_Teil"],
                    "ArtNr_Teil": output[i]["ArtNr_Teil"],
                    "Start": output[i]["Start"],
                    "Ende": output[i]["Ende"],
                    "Lieferdatum_Rohmaterial": output[i]["Lieferdatum_Rohmaterial"],
                    "LTermin": output[i]["LTermin"]             
                }
            };
            events_var.push(temp_event);
        }

        var resources_var: { id: string; title: string }[] = [];
        
        for (var i = 0; i < output.length; ++i) {
            var temp_res = {
                "id":output[i]["Maschine"],
                "title":output[i]["Maschine"]
            };
            resources_var.push(temp_res);
        }
        /*output = [{
            "Maschine": "SL 2",
            "title": "12403",
            "start": new Date("2016-02-26T11:54:52Z"),
            "end": new Date("2022-09-13T14:10:06Z")
                }]*/
        var machinecount = resources_var.length
        console.log(machinecount)
        
        this.calendarOptions["events"] = events_var
        this.calendarOptions["resources"] = resources_var
        console.log(this.calendarOptions["events"])
    }

})

</script>

<style>
.bck{
    height:10px;
    vertical-align: center;
}
.fwd, .fwd_db{
    height:20px;
    vertical-align: center;
}
.slot-label.operating-hours {
  background-color: #FFFFFF;
  color:blue;
}
.slot-label.weekend-non-operating-hours, .slot-label.holiday-non-operating-hours {
  background-color: #F1F1F1;
  color: #000000;
}
.date-label {
  font-weight: bold;
  text-align: center;
}
.fc-direction-ltr .fc-toolbar > * > * {
  background-color: #F1F1F1;
  color: #000000;
}
.fc-direction-ltr .fc-toolbar > * > *:hover {
  background-color: #F1F1F1;
  color: blue;
}
.fc .fc-toolbar-title, .fc .fc-toolbar-title:hover {
  color:orange;
  background-color: #FFFFFF;
}
.calendar-container {
  position: relative;
}
.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(255, 255, 255, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
}
.event-popup {
  background-color: #ffffff;
  color: orange;
  padding: 20px;
  border: 1px solid #000000;
}
.event-popup button.close-button {
  border: 1px solid #000000;
  padding: 5px 10px;
  background-color: #ffffff;
  color: #000000;
}
.headline {
  color: black;
}
</style>