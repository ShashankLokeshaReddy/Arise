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
        <FullCalendar :options="calendarOptions" defaultView="dayGridMonth" ref="calendar" datesRender="planSaved"/>
        </v-container>
    </div>
</template>

<script lang="ts">



import { defineComponent } from 'vue'

import '@fullcalendar/core/vdom'
import FullCalendar, { Calendar } from '@fullcalendar/vue3'
import DayGridPlugin from '@fullcalendar/daygrid'
import TimegridPlugin from '@fullcalendar/timegrid'
import InteractionPlugin from '@fullcalendar/interaction'
import ListPlugin from '@fullcalendar/list'
import ResourceTimelinePlugin from '@fullcalendar/resource-timeline'

var oldCalendar: { id: number; resourceId: string; title: string; AKNR:number; start: Date, end: Date }[] = [];


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
            //datesRender: alert("test"),
            customButtons: {
                myCustomButton: {
                text: 'speichern',
                click: function() {
                    alert('Der Plan wurde gespeichert!');
                    var current_events: { resourceId : string; title: string; start: Date; end: Date; }[]
                    //var current_events = this.getEvents(); //genau hier ist das Problem, dass es scheinbar keine Events bekommt.
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
            events: function () {
                alert("test");
                //let calendarApi = (this.$refs.calendar as InstanceType<typeof FullCalendar>).getApi();
                //alert(calendarApi.getDate());
            }
            
            
            },
        }
    },
    methods:
    
    { 
        async planUpdate() {
            console.log("updated events")
            var response = await fetch('http://localhost:8000/api/algorithm/naive_sorting')
            var output : { id: number; resourceId: string; title: string; AKNR: number; start: Date, end: Date, SchrittNr: number}[];
            var newevents = this.calendarOptions.events
            output = await response.json()
            this.calendarOptions["events"] = output

            console.log(output)
            
            console.log("new events")
            console.log(newevents)
        
        },

        async planSaved() {
            let calendarApi = (this.$refs.calendar as InstanceType<typeof FullCalendar>).getApi();
            var diffCalendar: { id: number; resourceId: string; title: string; AKNR:number; start: Date, end: Date }[] = [];
            var newCalendar: { id: number; resourceId: string; title: string; AKNR:number; start: Date, end: Date }[] = [];
            for (var i = 0; i < oldCalendar.length; i++){
                var obj = oldCalendar[i].id;
                var start = calendarApi.getEventById(obj)._instance.range.start;
                var end = calendarApi.getEventById(obj)._instance.range.end;
                start = new Date(start.getTime() + start.getTimezoneOffset() * 60000);
                end = new Date(end.getTime() + end.getTimezoneOffset() * 60000);

                var event = {
                    id: obj,
                    resourceId: calendarApi.getEventById(obj)._def.resourceIds[0],
                    title: calendarApi.getEventById(obj)._def.title,
                    start: start.toISOString(),
                    end: end.toISOString(),
                    AKNR: calendarApi.getEventById(obj)._def.extendedProps.AKNR,
                    SchrittNr: calendarApi.getEventById(obj)._def.extendedProps.SchrittNr,
                };
                console.log(start.toISOString());
                var oldStart = Date.parse(oldCalendar[i].start);
                var oldEnd = Date.parse(oldCalendar[i].end);
                newCalendar.push(event);
                if (oldCalendar[i].resourceId != event.resourceId || oldStart != Date.parse(start) || oldEnd != Date.parse(end)) {
                    diffCalendar.push(event);
                }

            }
            //only submits POST if events changed, therefore diffCalendar not empty
            if (!(Object.keys(diffCalendar).length === 0)) {
                fetch('http://localhost:8000/api/updatedb/post/', {
                    method: 'POST',
                    headers: {
                                'Accept': 'application/json',
                                'Content-Type': 'application/json'
                            },
                                body: JSON.stringify(diffCalendar)
                            })
                            .then(response => response.json())
                            .then(response => console.log(JSON.stringify(response)))
                oldCalendar = newCalendar;
                console.log("event got changed")
            }

        },
        async handleMonthChange() {
            console.log("rendering changed");
            let calendarApi = (this.$refs.calendar as InstanceType<typeof FullCalendar>).getApi();
            //alert(calendarApi.getDate());
    }
},



   async created(){
            var response = await fetch('http://localhost:8000/api/machines/')
            var output : { id: number; resourceId: string; title: string; AKNR: number; start: Date, end: Date, SchrittNr: number}[] = [];
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
            oldCalendar = output
            let self = this;
            //console.log(this.calendarOptions["events"])
        },


});


</script>

<style>


</style>