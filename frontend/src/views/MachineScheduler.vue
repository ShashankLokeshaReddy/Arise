<template>
    <div>
        <FullCalendar ref="machinecalendar" :options="calendarOptions">
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
import moment from 'moment';

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
            selectOverlap: false,
            eventOverlap: false,
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
                            .post('http://' + location.hostname + ':8001/api/jobs/savejobstoCSV/')
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
            editable: true,
            
            resourceAreaColumns: [
                {
                field: 'title',
                headerContent: 'Maschinen'
                }
            ],

            resources: [],
            events: [] as { resourceId : string; title: string; start: Date; end: Date; eventTextColor : string;}[],
            eventDidMount: (info) => {
                info.el.style.background = `blue`;
                info.el.style.color = "white";
            },
            eventResize: (info) => {
                // Get the selected machine
                var resources = info.event.getResources();
                var selectedMachine = resources[0]["title"];
                var machines = info.event.extendedProps.machines;
                var allowedMachines = machines.split(',');
                
                // Check whether the selected machine is allowed
                if (allowedMachines.includes(selectedMachine)) {
                    const start_s = new Date(info.event.start);
                    const startISOString = start_s.toISOString().substring(0, 19) + "Z";
                    const end_s = new Date(info.event.end);
                    const endISOString = end_s.toISOString().substring(0, 19) + "Z";

                    const jobs_data = {
                        AKNR: info.event.title,
                        TeilNr: info.event.extendedProps.TeilNr,
                        SchrittNr: info.event.extendedProps.SchrittNr,
                        Start: startISOString,
                        Ende: endISOString,
                        Maschine: selectedMachine
                    };

                    const formData = new FormData();
                    for (let key in jobs_data) {
                        formData.append(key, jobs_data[key]);
                    }
                    axios.post('http://' + location.hostname + ':8001/api/jobs/setInd/', formData)
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
            },
            eventDrop: (info) => {
            // Get the selected machine
            var resources = info.event.getResources();
            var selectedMachine = resources[0]["title"];
            var machines = info.event.extendedProps.machines;
            var allowedMachines = machines.split(',');
            // Check whether the selected machine is allowed
            if (allowedMachines.includes(selectedMachine)) {
                const start_s = new Date(info.event.start);
                const startISOString = start_s.toISOString().substring(0, 19) + "Z";
                const end_s = new Date(info.event.end);
                const endISOString = end_s.toISOString().substring(0, 19) + "Z";
                const jobs_data = {
                    AKNR: info.event.title,
                    TeilNr: info.event.extendedProps.TeilNr,
                    SchrittNr: info.event.extendedProps.SchrittNr,
                    Start: startISOString,
                    Ende: endISOString,
                    Maschine: selectedMachine
                };

                const formData = new FormData();
                for (let key in jobs_data) {
                    formData.append(key, jobs_data[key]);
                }
                axios.post('http://' + location.hostname + ':8001/api/jobs/setInd/', formData)
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
            },
            mounted() {
                this.$nextTick(() => {
                    let calendar = this.$refs.machinecalendar.getApi();
                    let currentView = calendar.view;
                    console.log(currentView.type);
                })
            }
            },
        }
    },
    async created(){
        var response = await fetch('http://' + location.hostname + ':8001/api/jobs/getSchedule')
        var output_resp = await response.json()
        var status = output_resp["Status"]
        var output : { Maschine: string; machines: string; AKNR: string; TeilNr: string; SchrittNr: string; item: string; Start: Date, Ende: Date }[] = [];
        output = output_resp["Table"]
        
        var events_var = []
        for (var i = 0; i < output.length; ++i) {
            if(output[i]["Ende"]===null){
                output[i]["Ende"] = output[i]["end"]
            }
            var temp_event = {
                "resourceId":output[i]["Maschine"],
                "title":output[i]["AKNR"],
                "start":output[i]["Start"],
                "end":output[i]["Ende"],
                "eventColor":"blue",
                "display":'auto',
                "className": "fwd",
                "extendedProps": {
                    "machines": output[i]["Maschine"],
                    "TeilNr": output[i]["TeilNr"],
                    "SchrittNr": output[i]["SchrittNr"]
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