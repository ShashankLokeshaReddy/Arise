<template>
  <v-container class="my-container">
    <v-row align="center">
      <v-col align="center">
        <v-btn-toggle mandatory tile color="primary" class="d-flex flex-row my-btn-toggle">
          <v-btn color=#FFA500 to="/">Maschinenansicht</v-btn>
          <v-btn color=#FFA500 to="/production">Produktions-Jobansicht</v-btn>
          <v-btn color=#FFA500 to="/background">Hintergrund-Jobansicht</v-btn>
          <v-btn color=#FFA500 to="/table">Tabelle</v-btn>
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
    font-family: 'Roboto', sans-serif;
    margin: 0;
  }
  .v-btn:hover {
    color:rgb(255, 255, 255) !important;
    background-color: white !important;
  }
</style>