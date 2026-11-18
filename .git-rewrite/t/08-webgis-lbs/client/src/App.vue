<template>
  <div class="app-container">
    <CesiumView />
    <GeoFence />
  </div>
</template>

<script setup>
import CesiumView from './components/CesiumView.vue'
import GeoFence from './components/GeoFence.vue'
</script>

<style scoped>
.app-container {
  width: 100%;
  height: 100%;
  position: relative;
}
</style>
