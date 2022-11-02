<template>
  <div class="app">
    <MachineScheduler />
    <OrderTable />
  </div>
  
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import MachineScheduler from './components/MachineScheduler.vue'
import OrderTable from './components/OrderTable.vue'


export default defineComponent({
  name: 'App',

  components: {
    MachineScheduler,
    OrderTable
},

  data () {
    return {
      //
    }
  },
})
</script>
