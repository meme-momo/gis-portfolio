<template>
  <div id="cesiumContainer"></div>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue'
import * as Cesium from 'cesium'
import { useViewerStore } from '../stores/viewer'

const viewerStore = useViewerStore()

onMounted(() => {
  // 设置Cesium Ion token
  Cesium.Ion.defaultAccessToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJhZWJjZDQ4Mi0yNjg2LTQwMjktYmZmNS01OTcxZDBlNjNkZWEiLCJpZCI6NDI4MzM4LCJpc3MiOiJodHRwczovL2lvbi5jZXNpdW0uY29tIiwiYXVkIjoidW5kZWZpbmVkX2RlZmF1bHQiLCJpYXQiOjE3NzgxNDI5NjN9.6vbhLywsBgTZv-lVRcI2eqYzfbToQY-lISqLmoWb2Ts'

  // 创建Cesium Viewer - 兼容模式配置
  const viewer = new Cesium.Viewer('cesiumContainer', {
    baseLayerPicker: false,
    geocoder: false,
    homeButton: false,
    sceneModePicker: false,
    navigationHelpButton: false,
    fullscreenButton: false,
    vrButton: false,
    animation: false,
    timeline: false,
    infoBox: false,
    selectionIndicator: false,
    shouldAnimate: true,
    // WebGL兼容配置
    contextOptions: {
      webgl: {
        alpha: false,
        depth: true,
        stencil: false,
        antialias: true,
        premultipliedAlpha: true,
        preserveDrawingBuffer: false,
        failIfMajorPerformanceCaveat: false
      }
    }
  })

  // 隐藏版权信息
  viewer._cesiumWidget._creditContainer.style.display = 'none'

  // 禁用太阳光照，避免渲染问题
  viewer.scene.globe.enableLighting = false
  viewer.scene.skyAtmosphere.show = false
  viewer.scene.fog.enabled = false

  // 设置初始视角到郑州区域
  viewer.camera.setView({
    destination: Cesium.Cartesian3.fromDegrees(113.65, 34.747, 5000),
    orientation: {
      heading: Cesium.Math.toRadians(0),
      pitch: Cesium.Math.toRadians(-45),
      roll: 0
    }
  })

  viewerStore.setViewer(viewer)
})

onUnmounted(() => {
  viewerStore.destroyViewer()
})
</script>

<style scoped>
#cesiumContainer {
  width: 100%;
  height: 100%;
}
</style>
