<template>
  <v-container class="my-container">
    <v-row align="center">
      <v-col align="center">
        <v-btn-toggle mandatory tile color="primary" class="d-flex flex-row my-btn-toggle">
          <v-btn color=#FFA500 to="/">Maschinenansicht</v-btn>
          <v-btn color=#FFA500 to="/production">Production-Jobansicht</v-btn>
          <v-btn color=#FFA500 to="/background">Background-Jobansicht</v-btn>
          <v-btn color=#FFA500 to="/table">Table</v-btn>
        </v-btn-toggle>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import axios from 'axios';

export default {

};
</script>

<style scoped>
  .my-btn-toggle .v-btn {
    border: 1px solid #ccc;
    margin: 0;
  }
</style>