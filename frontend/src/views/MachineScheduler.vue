<template>
    <div>
    <v-container text-align="center">
        <v-btn 
            align="center"
            color="error"
            v-on:click='planUpdate'
            >
            Plan generieren
        </v-btn>
        <v-btn 
            align="end"
            color="success"
            v-on:click='planSaved'
            >
            Plan speichern
        </v-btn>
    </v-container>
        <v-container>
        <FullCalendar :options="calendarOptions">
         </FullCalendar>
        </v-container>
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


export default defineComponent({
     
    //props: [FullCalendar],
    components: {FullCalendar},
    data()  {
        return {
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
            locale: "ger",
            initialView: 'resourceTimelineDay',
            schedulerLicenseKey: 'CC-Attribution-NonCommercial-NoDerivatives',
            headerToolbar: {
                left: 'prev, next today myCustomButton',
                center: 'title',
                right: 'resourceTimelineMonth, resourceTimelineWeek, resourceTimelineDay',
                    },
            customButtons: {
                myCustomButton: {
                text: 'speichern',
                click: function() {
                    alert('Der Plan wurde gespeichert!');
                    var current_events: { resourceId : string; title: string; start: Date; end: Date; }[]
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
            weekends: false,
            editable: true,
            resourceAreaHeaderContent: 'Machines',
            
            resources: [
                {
                    id: "SL 2",
                    title: "Maschine 1"
                },
                {
                    id: "SL 4",
                    title: "Maschine 2"
                },
                {
                    id: "SL 5",
                    title: "Maschine 3"
                },
                {
                    id: "SL 6",
                    title: "Maschine 4"
                },
                {
                    id: "SL 7",
                    title: "Maschine 5"
                },
                {
                    id: "SL 8",
                    title: "Maschine 6"
                },
                {
                    id: "SL 9",
                    title: "Maschine 7"
                },
                {
                    id: "SL 10",
                    title: "Maschine 8"
                },
                {
                    id: "SL 11",
                    title: "Maschine 9"
                }
            ],
            events: [] as { resourceId : string; title: string; AKNR:number; start: Date; end: Date; }[]
            
            
            },
        }
    },
    methods:
    
    { 
        async planUpdate() {
            console.log("updated events")
            var response = await fetch('http://localhost:8000/api/algorithm/naive_sorting')
            var output : { resourceId: string; title: string; AKNR:number; start: Date, end: Date }[] = [];
            var newevents = this.calendarOptions.events
            output = await response.json()
            this.calendarOptions["events"] = output

            console.log(output)
            
            console.log("new events")
            console.log(newevents)
        
        },

        async planSaved() {
            var data = this.calendarOptions.events
            
            fetch('http://localhost:8000/api/updatedb/update', {
                method: 'POST',
                headers: {
                            'Accept': 'application/json',
                            'Content-Type': 'application/json'
                        },
                            body: JSON.stringify(data)
                        })
                        .then(response => response.json())
                        .then(response => console.log(JSON.stringify(response)))
        }
},



   async created(){
            var response = await fetch('http://localhost:8000/api/machines/')
            var output : { resourceId: string; title: string; AKNR: number; start: Date, end: Date,}[] = [];
            console.log("original")
            output = await response.json()
            console.log(output)
            /*output = [{
               "resourceId": "SL 2",
                "title": "12403",
                "start": new Date("2016-02-26T11:54:52Z"),
                "end": new Date("2022-09-13T14:10:06Z")
                    }]*/
            var machinecount = output.length
            console.log(machinecount)
            
            
            this.calendarOptions["events"] = output
            //console.log(this.calendarOptions["events"])
        }

})

</script>

<style>


</style>