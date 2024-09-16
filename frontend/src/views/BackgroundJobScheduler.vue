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

      <FullCalendar ref="backcalendar" :options="calendarOptions"></FullCalendar>
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

export default defineComponent({
     
    //props: [FullCalendar],
    components: {FullCalendar},
    data()  {
        return {
            fetchScheduledJobs: false as boolean,
            selectedEvent: null as any,
            showEventPopup: false as boolean,
            isLoading: false as boolean,
            calendarApi: null as any,
            calendarOptions: {
                plugins: [ 
                    DayGridPlugin,
                    TimegridPlugin,
                    InteractionPlugin,
                    ListPlugin,
                    ResourceTimelinePlugin,
            ],
            eventMaxStack: 3 as number,
            slotDuration: '00:05:00' as string,
            resourceAreaWidth: "10%" as string,
            scrollTimeReset: false as boolean,
            slotLabelContent: ({ date }: { date: Date }) => {
                const hour = date.getHours();
                const minute = date.getMinutes();
                const startHour = 0;
                const endHour = 24;
            },
            slotLabelClassNames: ({ date, isLabel }: { date: Date, isLabel: boolean }) => {
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
            slotLaneClassNames: ({ date, isLabel }: { date: Date, isLabel: boolean }) => {
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
            // editable: true, # to ensure that it cannot be dragged to a different resource
            eventStartEditable: true,
            eventDurationEditable: true,
            resourceEditable: false,
            
            resourceAreaColumns: [
                {
                field: 'title',
                headerContent: 'Arbeitsauftrag'
                }
            ],

            resources: [],
            events: [] as { resourceId : string; title: string; start: Date; end: Date; eventTextColor : string;}[],
            eventClick: (info) => {
                this.selectedEvent = info.event;
                this.showEventPopup = true; // Open the popup
            },
            eventDidMount: (info) => {
                if(info.event.classNames[0] === "fwd" || info.event.classNames[0] === "bck"){
                    let calendar: any = this.$refs.backcalendar.getApi();
                    let view_start = calendar.currentData.calendarApi.currentData.dateProfile.activeRange.start;
                    let view_end = calendar.currentData.calendarApi.currentData.dateProfile.activeRange.end;
                    let offset_start = view_start.getTimezoneOffset();
                    let gmtTime_view_start = new Date(view_start.getTime() + offset_start * 60 * 1000);
                    let offset_end = view_end.getTimezoneOffset();
                    let gmtTime_view_end = new Date(view_end.getTime() + offset_end * 60 * 1000);
                    const setupTimeMinutes = info.event.extendedProps.Ruestzeit_Soll;
                    const setupTimeDuration = setupTimeMinutes * 60 * 1000;
                    const delta1 = (setupTimeDuration / (info.event.end - info.event.start)) * 100;
                    var resources = info.event.getResources();
                    var all_events = resources[0].getEvents()
                    var bck_event
                    for (let i = 0; i < all_events.length; i++) {
                        if (all_events[i].classNames[0] === "bck"){ //info.event.title
                            bck_event = all_events[i]
                        }
                    }
                    if(info.event.classNames[0] === "fwd"){
                        var override_start = info.event.start;
                        var override_end = info.event.end;
                        if(info.event.end > gmtTime_view_end){
                            override_end = gmtTime_view_end;
                        }
                        if(info.event.start < gmtTime_view_start){
                            override_start = gmtTime_view_start;
                        }
                    }
                    console.log(view_start,view_end);
                    console.log(info.event.title,info.event.start,info.event.end);
                    //console.log(bck_event.title,bck_event.start,bck_event.end);
                    if((info.event.end > bck_event.end) && (info.event.classNames[0] === "fwd")){
                        var numerator = bck_event.end - override_start;
                        var denominator = override_end - override_start;
                        var delta = numerator*100/denominator;
                        var delta2 = delta - delta1;
                        info.el.style.background = `linear-gradient(270deg, red 0% ${100-delta}%, blue ${100-delta}% ${100-delta1}%, purple 0%)`;
                        info.el.style.color = "white";
                    }
                    else if(info.event.classNames[0] === "bck"){
                        info.el.style.background = `orange`;
                    }
                    else{
                        info.el.style.background = `linear-gradient(90deg, purple ${delta1}%, blue 0%)`;
                        info.el.style.color = "white";
                    }
                }
                if(info.event.classNames[0] === "fwd_db" || info.event.classNames[0] === "bck_db"){
                    let calendar: any = this.$refs.backcalendar.getApi();
                    let view_start = calendar.currentData.calendarApi.currentData.dateProfile.activeRange.start;
                    let view_end = calendar.currentData.calendarApi.currentData.dateProfile.activeRange.end;
                    let offset_start = view_start.getTimezoneOffset();
                    let gmtTime_view_start = new Date(view_start.getTime() + offset_start * 60 * 1000);
                    let offset_end = view_end.getTimezoneOffset();
                    let gmtTime_view_end = new Date(view_end.getTime() + offset_end * 60 * 1000);
                    var resources = info.event.getResources();
                    var all_events = resources[0].getEvents()
                    var bck_db_event
                    for (let i = 0; i < all_events.length; i++) {
                        if (all_events[i].classNames[0] === "bck_db"){ //info.event.title
                            bck_db_event = all_events[i]
                        }
                    }
                    if(info.event.classNames[0] === "fwd_db"){
                        var override_start = info.event.start;
                        var override_end = info.event.end;
                        if(info.event.end > gmtTime_view_end){
                            override_end = gmtTime_view_end;
                        }
                        if(info.event.start < gmtTime_view_start){
                            override_start = gmtTime_view_start;
                        }
                    }
                    console.log(view_start,view_end);
                    console.log(info.event.title,info.event.start,info.event.end);
                    //console.log(bck_db_event.title,bck_db_event.start,bck_db_event.end);
                    if((info.event.end > bck_db_event.end) && (info.event.classNames[0] === "fwd_db")){
                        var numerator = bck_db_event.end - override_start;
                        var denominator = override_end - override_start;
                        var delta = numerator*100/denominator;
                        info.el.style.background = `linear-gradient(270deg, red 0% ${100-delta}%, green ${100-delta}% ${100-delta1}%, purple 0%)`;
                        info.el.style.color = "white";
                    }
                    else if(info.event.classNames[0] === "bck_db"){
                        info.el.style.background = `grey`;
                    }
                    else{
                        info.el.style.background = `linear-gradient(90deg, purple ${delta1}%, green 0%)`;
                        info.el.style.color = "white";
                    }
                }
            },
            eventResize: (info) => {
                if(info.event.classNames[0] !== "fwd_db" && info.event.classNames[0] !== "bck_db"){
                    let calendar: any = this.$refs.backcalendar.getApi();
                    let currentView = calendar.view;
                    calendar.changeView(currentView.type);

                    const start_s = new Date(info.event.start);
                    const startISOString = start_s.toISOString();
                    start_s.setDate(start_s.getDate() - 1);
                    const Lieferdatum_Rohmaterial = start_s.toISOString().substring(0, 19) + "Z";

                    const end_s = new Date(info.event.end);
                    const endISOString = end_s.toISOString();
                    end_s.setDate(end_s.getDate() + 2);
                    const LTermin = end_s.toISOString().substring(0, 19) + "Z";
                    info.event.setExtendedProp('Lieferdatum_Rohmaterial', startISOString)
                    info.event.setExtendedProp('LTermin', endISOString)

                    const jobs_data = {AKNR: info.event.extendedProps.AKNR, Lieferdatum_Rohmaterial: Lieferdatum_Rohmaterial, LTermin: LTermin, TeilNr: info.event.extendedProps.TeilNr, SchrittNr: info.event.extendedProps.SchrittNr, Ruestzeit_Soll: info.event.extendedProps.Ruestzeit_Soll, Fefco_Teil: info.event.extendedProps.Fefco_Teil, ArtNr_Teil: info.event.extendedProps.ArtNr_Teil};

                    const formData = new FormData();
                    for (let key in jobs_data) {
                        formData.append(key, jobs_data[key]);
                    }
                    console.log("jobs_data",jobs_data)
                    console.log("formData",formData)
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
                    alert('Durch die bereits geplanten Jobs ist diese Bewegung nicht gestattet!');
                }
            },
            eventDrop: (info) => {
                if(info.event.classNames[0] !== "fwd_db" && info.event.classNames[0] !== "bck_db"){
                    let calendar: any = this.$refs.backcalendar.getApi();
                    let currentView = calendar.view;
                    calendar.changeView(currentView.type);

                    const start_s = new Date(info.event.start);
                    const startISOString = start_s.toISOString();
                    start_s.setDate(start_s.getDate() - 1);
                    const Lieferdatum_Rohmaterial = start_s.toISOString().substring(0, 19) + "Z";

                    const end_s = new Date(info.event.end);
                    const endISOString = end_s.toISOString();
                    end_s.setDate(end_s.getDate() + 2);
                    const LTermin = end_s.toISOString().substring(0, 19) + "Z";
                    info.event.setExtendedProp('Lieferdatum_Rohmaterial', startISOString)
                    info.event.setExtendedProp('LTermin', endISOString)

                    const jobs_data = {AKNR: info.event.extendedProps.AKNR, Lieferdatum_Rohmaterial: Lieferdatum_Rohmaterial, LTermin: LTermin, TeilNr: info.event.extendedProps.TeilNr, SchrittNr: info.event.extendedProps.SchrittNr, Ruestzeit_Soll: info.event.extendedProps.Ruestzeit_Soll, Fefco_Teil: info.event.extendedProps.Fefco_Teil, ArtNr_Teil: info.event.extendedProps.ArtNr_Teil};

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
                    alert('Durch die bereits geplanten Jobs ist diese Bewegung nicht gestattet!');
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
                const calendarApi = this.$refs.backcalendar.getApi();
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

                    var events_var_db = []
                    for (var i = 0; i < output.length; ++i) {
                        if(output[i]["Ende"]===null){
                            output[i]["Ende"] = output[i]["LTermin"]
                        }
                        var bck_event = {
                            "resourceId":output[i]["AKNR"] + "-" + output[i]["TeilNr"]  + "-" +  output[i]["SchrittNr"] + "-" + output[i]["Suchname"],
                            "title":output[i]["AKNR"] + "-" + output[i]["Suchname"],
                            "start":new Date(new Date(output[i]["Lieferdatum_Rohmaterial"]).getTime() + (1 * 24 * 60 * 60 * 1000)),
                            "end": new Date(new Date(output[i]["LTermin"]).getTime() - (2 * 24 * 60 * 60 * 1000)),
                            "eventColor":"grey",
                            "className": "bck_db",
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
                        var temp_event = {
                            "resourceId":output[i]["AKNR"] + "-" + output[i]["TeilNr"]  + "-" +  output[i]["SchrittNr"] + "-" + output[i]["Suchname"],
                            "title":output[i]["Maschine"],
                            "start":output[i]["Start"],
                            "end":output[i]["Ende"],
                            "display": 'background',
                            "eventColor":"green",
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

                        events_var_db.push(bck_event);
                        events_var_db.push(temp_event);
                    }

                    var resources_var_db = [];

                    for (var i = 0; i < output.length; ++i) {
                        var temp_res = {
                        "id": output[i]["AKNR"] + "-" + output[i]["TeilNr"]  + "-" +  output[i]["SchrittNr"] + "-" + output[i]["Suchname"],
                        "title": output[i]["AKNR"] + "-" + output[i]["TeilNr"]  + "-" +  output[i]["SchrittNr"] + "-" + output[i]["Suchname"]
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
                // Remove events with the 'fwd_db' and 'bck_db' classes
                this.isLoading = true;
                this.calendarOptions.events = this.calendarOptions.events.filter(
                (event) => !(event.className.includes('fwd_db') || event.className.includes('bck_db'))
                );

                // Get the resource IDs associated with remaining 'fwd' or 'bck' events
                const remainingResourceIds = this.calendarOptions.events
                .filter((event) => event.className.includes('fwd') || event.className.includes('bck'))
                .map((event) => event.resourceId);

                // Remove resources not associated with remaining 'fwd' or 'bck' events
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
            var output : { resourceId: string; AKNR: string; TeilNr: string; SchrittNr: string; Lieferdatum_Rohmaterial: Date, LTermin: Date, Start: Date, Ende: Date }[] = [];
            output = output_resp["Table"]
            
            var events_var = []
            for (var i = 0; i < output.length; ++i) {
                var start_date_str = output[i]["Start"];
                var minutes_to_add = output[i]["Ruestzeit_Soll"];
                var start_date = new Date(start_date_str);
                var end_date = new Date(start_date.getTime() - minutes_to_add * 60000);
                var adjustedStartTime = end_date.toISOString().slice(0, 19) + "Z";

                var bck_event = {
                    "resourceId":output[i]["AKNR"] + "-" + output[i]["TeilNr"]  + "-" +  output[i]["SchrittNr"] + "-" + output[i]["Suchname"],
                    "title":output[i]["AKNR"] + "-" + output[i]["Suchname"],
                    "start":new Date(new Date(output[i]["Lieferdatum_Rohmaterial"]).getTime() + (1 * 24 * 60 * 60 * 1000)),
                    "end": new Date(new Date(output[i]["LTermin"]).getTime() - (2 * 24 * 60 * 60 * 1000)),
                    "eventColor":"orange",
                    "className": "bck",
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
                var temp_event = {
                    "resourceId":output[i]["AKNR"] + "-" + output[i]["TeilNr"]  + "-" +  output[i]["SchrittNr"] + "-" + output[i]["Suchname"],
                    "title":output[i]["Maschine"],
                    "start":adjustedStartTime,
                    "end":output[i]["Ende"],
                    "display": 'background',
                    "eventColor":"blue",
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

                events_var.push(bck_event);
                events_var.push(temp_event);
            }

            var resources_var: { id: string; title: string }[] = [];
            for (var i = 0; i < output.length; ++i) {
                var temp_res = {
                    "id":output[i]["AKNR"] + "-" + output[i]["TeilNr"]  + "-" +  output[i]["SchrittNr"] + "-" + output[i]["Suchname"],
                    "title":output[i]["AKNR"] + "-" + output[i]["TeilNr"]  + "-" +  output[i]["SchrittNr"] + "-" + output[i]["Suchname"]
                };
                resources_var.push(temp_res);
            }
            /*output = [{
               "resourceId": "SL 2",
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
.bck, .bck_db{
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