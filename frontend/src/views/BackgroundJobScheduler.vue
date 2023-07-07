<template>
    <div>
        <FullCalendar ref="calendar" :options="calendarOptions">
        </FullCalendar>
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
            calendarApi: null,
            calendarOptions: {
                plugins: [ 
                    DayGridPlugin,
                    TimegridPlugin,
                    InteractionPlugin,
                    ListPlugin,
                    ResourceTimelinePlugin,
            ],
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
            schedulerLicenseKey: 'CC-Attribution-NonCommercial-NoDerivatives',
            headerToolbar: {
                left: 'prev next today myCustomButton',
                center: 'title',
                right: 'resourceTimelineYear resourceTimelineMonth resourceTimelineWeek resourceTimelineDay',
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
                            this.fillTable();
                            })
                            .catch((error) => {
                                console.log(error);
                            });
                    }
                }
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
            eventDidMount: (info) => {
                let calendar: any = this.$refs.calendar.getApi();
                let view_start = calendar.currentData.calendarApi.currentData.dateProfile.activeRange.start;
                let view_end = calendar.currentData.calendarApi.currentData.dateProfile.activeRange.end;
                let offset_start = view_start.getTimezoneOffset();
                let gmtTime_view_start = new Date(view_start.getTime() + offset_start * 60 * 1000);
                let offset_end = view_end.getTimezoneOffset();
                let gmtTime_view_end = new Date(view_end.getTime() + offset_end * 60 * 1000);
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
                console.log(bck_event.title,bck_event.start,bck_event.end);
                if((info.event.end > bck_event.end) && (info.event.classNames[0] === "fwd")){
                    var numerator = bck_event.end - override_start;
                    var denominator = override_end - override_start;
                    var delta = numerator*100/denominator;
                    info.el.style.background = `linear-gradient(90deg, blue ${delta}%, red 0%)`;
                    info.el.style.color = "white";
                }
                else if(info.event.classNames[0] === "bck"){
                    info.el.style.background = `orange`;
                }
                else{
                    info.el.style.background = `blue`;
                    info.el.style.color = "white";
                }
            },
            eventResize: (info) => {
                let calendar: any = this.$refs.calendar.getApi();
                let currentView = calendar.view;
                calendar.changeView(currentView.type);

                const start_s = new Date(info.event.start);
                const startISOString = start_s.toISOString();
                start_s.setDate(start_s.getDate() - 2);
                const Lieferdatum_Rohmaterial = start_s.toISOString().substring(0, 19) + "Z";

                const end_s = new Date(info.event.end);
                const endISOString = end_s.toISOString();
                end_s.setDate(end_s.getDate() + 2);
                const LTermin = end_s.toISOString().substring(0, 19) + "Z";

                const jobs_data = {AKNR: info.event.title, Lieferdatum_Rohmaterial: Lieferdatum_Rohmaterial, LTermin: LTermin, TeilNr: info.event.extendedProps.TeilNr, SchrittNr: info.event.extendedProps.SchrittNr};

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
            },
            eventDrop: (info) => {
                let calendar: any = this.$refs.calendar.getApi();
                let currentView = calendar.view;
                calendar.changeView(currentView.type);

                const start_s = new Date(info.event.start);
                const startISOString = start_s.toISOString();
                start_s.setDate(start_s.getDate() - 2);
                const Lieferdatum_Rohmaterial = start_s.toISOString().substring(0, 19) + "Z";

                const end_s = new Date(info.event.end);
                const endISOString = end_s.toISOString();
                end_s.setDate(end_s.getDate() + 2);
                const LTermin = end_s.toISOString().substring(0, 19) + "Z";

                const jobs_data = {AKNR: info.event.title, Lieferdatum_Rohmaterial: Lieferdatum_Rohmaterial, LTermin: LTermin, TeilNr: info.event.extendedProps.TeilNr, SchrittNr: info.event.extendedProps.SchrittNr};

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
            },          
            mounted() {
                this.$nextTick(() => {
                    let calendar = this.$refs.calendar.getApi();
                    let currentView = calendar.view;
                    console.log(currentView.type);
                })
            }
            },
        }
    },

   async created(){
            var response = await fetch('http://' + window.location.hostname + ':8001/api/jobs/getSchedule')
            var output_resp = await response.json()
            var status = output_resp["Status"]
            var output : { resourceId: string; AKNR: string; TeilNr: string; SchrittNr: string; Lieferdatum_Rohmaterial: Date, LTermin: Date, Start: Date, Ende: Date }[] = [];
            output = output_resp["Table"]
            
            var events_var = []
            for (var i = 0; i < output.length; ++i) {
                if(output[i]["Ende"]===null){
                    output[i]["Ende"] = output[i]["LTermin"]
                }
                var bck_event = {
                    "resourceId":output[i]["AKNR"],
                    "title":output[i]["AKNR"],
                    "start":new Date(new Date(output[i]["Lieferdatum_Rohmaterial"]).getTime() + (2 * 24 * 60 * 60 * 1000)),
                    "end": new Date(new Date(output[i]["LTermin"]).getTime() - (2 * 24 * 60 * 60 * 1000)),
                    "eventColor":"orange",
                    "className": "bck",
                    "extendedProps": {
                        "TeilNr": output[i]["TeilNr"],
                        "SchrittNr": output[i]["SchrittNr"]
                    }
                };
                var temp_event = {
                    "resourceId":output[i]["AKNR"],
                    "title":output[i]["Maschine"],
                    "start":output[i]["Start"],
                    "end":output[i]["Ende"],
                    "display": 'background',
                    "eventColor":"blue",
                    "className": "fwd"
                };

                events_var.push(bck_event);
                events_var.push(temp_event);
            }

            var resources_var: { id: string; title: string }[] = [];
            for (var i = 0; i < output.length; ++i) {
                var temp_res = {
                    "id":output[i]["AKNR"],
                    "title":output[i]["AKNR"]
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
.bck{
    height:10px;
    vertical-align: center;
}
.fwd{
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
  color:blue;
  background-color: #FFFFFF;
}
</style>