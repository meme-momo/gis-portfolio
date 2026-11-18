<template>
  <div class="status-panel">
    <h3 class="panel-title">实时地理围栏监控系统</h3>
    <div class="status-item">
      <span>WebSocket状态:</span>
      <span :class="wsStatusClass">{{ wsStatus }}</span>
    </div>
    <div class="status-item">
      <span>当前经纬度:</span>
      <span>{{ positionText }}</span>
    </div>
    <div class="status-item">
      <span>围栏状态:</span>
      <span :class="fenceStatusClass">{{ fenceStatus }}</span>
    </div>
    <div class="status-item">
      <span>用户ID:</span>
      <span>{{ userId }}</span>
    </div>
    <div class="tips">
      <small>系统正在模拟位置移动，越界时自动告警</small>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import * as Cesium from 'cesium'
import { ElNotification } from 'element-plus'
import { useViewerStore } from '../stores/viewer'

const viewerStore = useViewerStore()

// DOM容器
let ws = null
let userPointEntity = null
let fenceEntities = []
let simulateInterval = null

const userId = `user_${Date.now()}`

// 状态变量
const wsStatus = ref('未连接')
const wsStatusClass = ref('text-red-500')
const positionText = ref('--')
const fenceStatus = ref('围栏内')
const fenceStatusClass = ref('text-green-500')

// WebSocket初始化 + 断线重连
const initWebSocket = () => {
  ws = new WebSocket('ws://localhost:3001')

  ws.onopen = () => {
    wsStatus.value = '已连接,实时监控中'
    wsStatusClass.value = 'text-green-500'
  }

  ws.onclose = () => {
    wsStatus.value = '连接断开,3秒后重连'
    wsStatusClass.value = 'text-orange-500'
    setTimeout(() => initWebSocket(), 3000)
  }

  ws.onerror = () => {
    wsStatus.value = '连接异常'
    wsStatusClass.value = 'text-red-500'
  }

  // 接收后端实时推送位置&越界结果
  ws.onmessage = (event) => {
    const res = JSON.parse(event.data)
    if (res.type === 'position_update') {
      handlePositionUpdate(res)
    }
  }
}

// 加载地理围栏
const loadFence = async () => {
  try {
    const res = await fetch('http://localhost:3001/api/fence/list')
    const { data } = await res.json()
    fenceEntities = []

    data.forEach(fence => {
      let entity
      if (fence.type === 'polygon') {
        entity = viewerStore.viewer.entities.add({
          name: fence.name,
          polygon: {
            hierarchy: Cesium.Cartesian3.fromDegreesArray(fence.coordinates.flat()),
            material: Cesium.Color.GREEN.withAlpha(0.3),
            outline: true,
            outlineColor: Cesium.Color.GREEN,
            outlineWidth: 2
          }
        })
      } else if (fence.type === 'circle') {
        entity = viewerStore.viewer.entities.add({
          name: fence.name,
          position: Cesium.Cartesian3.fromDegrees(...fence.center),
          ellipse: {
            semiMajorAxis: fence.radius,
            semiMinorAxis: fence.radius,
            material: Cesium.Color.GREEN.withAlpha(0.3),
            outline: true,
            outlineColor: Cesium.Color.GREEN,
            outlineWidth: 2
          }
        })
      }
      fenceEntities.push(entity)
    })

    viewerStore.viewer.zoomTo(viewerStore.viewer.entities)
  } catch (err) {
    console.error('加载围栏失败:', err)
  }
}

// 更新点位、围栏样式、告警
const handlePositionUpdate = (data) => {
  const { lng, lat, isOutOfFence, fence } = data
  positionText.value = `${lng.toFixed(5)}, ${lat.toFixed(5)}`

  // 更新用户点位
  const cartesian = Cesium.Cartesian3.fromDegrees(lng, lat)
  if (!userPointEntity) {
    userPointEntity = viewerStore.viewer.entities.add({
      position: cartesian,
      point: { 
        pixelSize: 14, 
        color: Cesium.Color.BLUE,
        outlineColor: Cesium.Color.WHITE,
        outlineWidth: 2
      },
      label: {
        text: '实时人员',
        pixelOffset: new Cesium.Cartesian2(0, -25),
        fillColor: Cesium.Color.WHITE,
        font: '14px sans-serif',
        style: Cesium.LabelStyle.FILL_AND_OUTLINE,
        outlineWidth: 2
      }
    })
  } else {
    userPointEntity.position = cartesian
  }

  if (isOutOfFence) {
    fenceStatus.value = '已越界'
    fenceStatusClass.value = 'text-red-500'
    // 围栏变红
    fenceEntities.forEach(entity => {
      if (entity.polygon) {
        entity.polygon.material = Cesium.Color.RED.withAlpha(0.3)
        entity.polygon.outlineColor = Cesium.Color.RED
      }
      if (entity.ellipse) {
        entity.ellipse.material = Cesium.Color.RED.withAlpha(0.3)
        entity.ellipse.outlineColor = Cesium.Color.RED
      }
    })
    
    ElNotification.error({
      title: '⚠️ 实时越界告警',
      message: `围栏区域: ${fence?.name || '未知'}\n经纬度: ${lng.toFixed(5)}, ${lat.toFixed(5)}`,
      position: 'bottom-right',
      duration: 3000
    })
  } else {
    fenceStatus.value = '围栏内'
    fenceStatusClass.value = 'text-green-500'
    // 围栏恢复绿色
    fenceEntities.forEach(entity => {
      if (entity.polygon) {
        entity.polygon.material = Cesium.Color.GREEN.withAlpha(0.3)
        entity.polygon.outlineColor = Cesium.Color.GREEN
      }
      if (entity.ellipse) {
        entity.ellipse.material = Cesium.Color.GREEN.withAlpha(0.3)
        entity.ellipse.outlineColor = Cesium.Color.GREEN
      }
    })
  }
}

// 模拟位置移动（在围栏区域内外随机移动）
const lblng = 113.645, rlng = 113.655
const lblat = 34.742, rlat = 34.752
let currentLng = (lblng + rlng) / 2
let currentLat = (lblat + rlat) / 2

const simulateLocationUpdate = () => {
  simulateInterval = setInterval(() => {
    // 随机移动，有时会越界
    const moveX = (Math.random() - 0.5) * 0.003
    const moveY = (Math.random() - 0.5) * 0.003
    
    currentLng += moveX
    currentLat += moveY
    
    // 边界限制
    if (currentLng < lblng - 0.002) currentLng = lblng
    if (currentLng > rlng + 0.002) currentLng = rlng
    if (currentLat < lblat - 0.002) currentLat = lblat
    if (currentLat > rlat + 0.002) currentLat = rlat

    if (ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ userId, lng: currentLng, lat: currentLat }))
    }
  }, 2000)
}

// 组件挂载
onMounted(async () => {
  // 等待viewer初始化
  const checkViewer = setInterval(() => {
    if (viewerStore.viewer) {
      clearInterval(checkViewer)
      initWebSocket()
      loadFence()
      simulateLocationUpdate()
    }
  }, 100)
})

// 组件销毁释放资源
onUnmounted(() => {
  if (ws) ws.close()
  if (simulateInterval) clearInterval(simulateInterval)
})
</script>

<style scoped>
.status-panel {
  position: absolute;
  top: 20px;
  left: 20px;
  background: rgba(0, 0, 0, 0.8);
  color: #fff;
  padding: 20px;
  border-radius: 8px;
  z-index: 999;
  min-width: 280px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(10px);
}

.panel-title {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.status-item {
  margin: 10px 0;
  font-size: 14px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status-item span:first-child {
  color: #aaa;
}

.tips {
  margin-top: 15px;
  padding-top: 10px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  color: #888;
  text-align: center;
}
</style>
