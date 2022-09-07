<template>
  <div class="app">
    <MachineScheduler />
  </div>
</template>


<script lang="ts">
import { defineComponent } from 'vue';
import MachineScheduler from './components/MachineScheduler.vue';

export default defineComponent({
  name: 'App',
  components: {
    MachineScheduler
  }
});
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
