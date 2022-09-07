<template>
    <div>
        <FullCalendar :options="calendarOptions">
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

//var eventvar : { resourceId: string; title: string, start: any, end: any }[] = [];

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
            eventMaxStack: 1,
            slotDuration: '00:02:00',
            locale: "ger",
            initialView: 'resourceTimelineDay',
            schedulerLicenseKey: 'CC-Attribution-NonCommercial-NoDerivatives',
            headerToolbar: {
                left: 'prev, next today',
                center: 'title',
                right: 'resourceTimelineMonth, resourceTimelineWeek, resourceTimelineDay',
                    },
            weekends: false,
            editable: true,
            resourceAreaHeaderContent: 'Machines',
            resources: [{
                id: "a",
                title: "Maschine 1"
            }],
            events: [] as { resourceId: string; title: string, start: Date, end:  Date}[]
            
            
            },
        }
    },

   async created(){
            var response = await fetch('http://localhost:8000/api/machines/')
            var output : { resourceId: string; title: string, start: any, end: any }[] = [];
            
            output = await response.json()

            var machinecount = output.length
            console.log(machinecount)
            var l:number
            for (l = 0;  l < machinecount; l++){
                output[l]["start"] = new Date(output[l]["start"])
                output[l]["end"] = new Date(output[l]["end"])                
            }
            
            this.calendarOptions["events"] = output
            console.log(this.calendarOptions["events"])
        }

})

</script>

<style>


</style>