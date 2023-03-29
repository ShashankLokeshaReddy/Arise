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
            locale: "ger",
            initialView: 'resourceTimelineDay',
            schedulerLicenseKey: 'CC-Attribution-NonCommercial-NoDerivatives',
            headerToolbar: {
                left: 'prev next today myCustomButton',
                center: 'title',
                right: 'resourceTimelineMonth resourceTimelineWeek resourceTimelineDay',
                    },
            customButtons: {
                myCustomButton: {
                text: 'speichern',
                click: function() {
                    alert('Der Plan wurde gespeichert!');
                    var current_events: { MaschNr : string; title: string; start: Date; end: Date; }[]
                    //current_events = this.getEvents(); //genau hier ist das Problem, dass es scheinbar keine Events bekommt.
                    (async () => {
                        const rawResponse = await fetch('https://httpbin.org/post', {
                        method: 'POST',
                        headers: {
                            'Accept': 'application/json',
                            'Content-Type': 'application/json'
                                },
                        //body: JSON.stringify(current_events)
                                });
                        const content = await rawResponse.json();

                        console.log(content);
                        })();
                }
                }
            },
            weekends: true,
            editable: true,
            
            resourceAreaColumns: [
                {
                field: 'title',
                headerContent: 'Machines'
                }
            ],

            resources: [],
            events: [] as { resourceId : string; title: string; start: Date; end: Date; eventTextColor : string;}[],
            eventDidMount: (info) => {
                info.el.style.background = `blue`;
                info.el.style.color = "white";
            },
            eventResize: (info) => {
                var resources = info.event.getResources();
                const jobs_data = [{"Job_ID": info.event.title, "Start": info.event.start, "Ende": info.event.end, "MaschNr": resources[0]["title"]}];
                axios.post('http://localhost:8000/api/jobs/setSchedule/', {jobs_data:jobs_data})
                .then(response => {
                    // Handle successful response
                    console.log(response.data)
                })
                .catch(error => {
                    // Handle error
                    console.log(error)
                });
            },
            eventDrop: (info) => {
                // Get the selected machine
                var resources = info.event.getResources();
                var MaschNr = resources[0]["title"];
                
                var machines = info.event.extendedProps.machines;
                var allowedMachines = machines.split(',');
                
                // Check whether the selected machine is allowed
                if (allowedMachines.includes(MaschNr)) {
                    // If the selected machine is allowed, update the job schedule
                    const jobs_data = [{"Job_ID": info.event.title, "Start": info.event.start, "Ende": info.event.end, "MaschNr": MaschNr}];

                    axios.post('http://localhost:8000/api/jobs/setSchedule/', {jobs_data:jobs_data})
                    .then(response => {
                        // Handle successful response
                        console.log(response.data)
                    })
                    .catch(error => {
                        // Handle error
                        console.log(error)
                    });
                } else {
                    // If the selected machine is not allowed, revert the event to its original position
                    info.revert();
                    alert('Cannot drop event as it has constraints to run on following machines: ' + info.event.extendedProps.machines);
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
            var response = await fetch('http://localhost:8000/api/jobs/getSchedule')
            var output_resp = await response.json()
            var status = output_resp["Status"]
            var output : { MaschNr: string; Job_ID: string; Start: Date, Ende: Date }[] = [];
            output = output_resp["Table"]
            
            var events_var = []
            for (var i = 0; i < output.length; ++i) {
                if(output[i]["Ende"]===null){
                    output[i]["Ende"] = output[i]["end"]
                }
                var temp_event = {
                    "resourceId":output[i]["MaschNr"],
                    "title":output[i]["Job_ID"],
                    "start":output[i]["Start"],
                    "end":output[i]["Ende"],
                    "eventColor":"blue",
                    "display":'auto',
                    "className": "fwd",
                    "extendedProps": {
                        "machines": output[i]["MaschNr"]
                    }
                };

                events_var.push(temp_event);
            }

            var resources_var: { id: string; title: string }[] = [];
            for (var i = 0; i < output.length; ++i) {
                var temp_res = {
                    "id":output[i]["MaschNr"],
                    "title":output[i]["MaschNr"]
                };
                resources_var.push(temp_res);
            }
            /*output = [{
               "MaschNr": "SL 2",
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
</style>