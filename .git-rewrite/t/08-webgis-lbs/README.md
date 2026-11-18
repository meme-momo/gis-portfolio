# 实时地理围栏LBS监控系统

基于 Node.js + Vue3 + CesiumJS 实现的实时地理围栏 LBS 服务项目

## 项目架构

- **后端**: Node.js + Express + WebSocket(ws) + Turf.js (空间计算)
- **前端**: Vue3 + Vite + CesiumJS + Pinia + Element Plus
- **实时通信**: WebSocket 长连接
- **GIS引擎**: CesiumJS 三维地图

## 核心功能

✅ 多边形围栏和圆形围栏两种地理围栏类型  
✅ 基于 Turf.js 的 GIS 空间几何算法（点面包含判断）  
✅ WebSocket 毫秒级实时位置上报和越界告警推送  
✅ CesiumJS 三维地图可视化展示  
✅ 围栏状态实时变色（绿色=正常，红色=越界）  
✅ 越界弹窗告警通知  
✅ 模拟人员位置移动演示  
✅ 自动断线重连机制

## 快速开始

### 1. 启动后端服务

```bash
cd server
npm install
npm start
```

后端服务启动后访问:
- HTTP服务: http://localhost:3001
- WebSocket: ws://localhost:3001
- 围栏API: http://localhost:3001/api/fence/list

### 2. 启动前端服务

```bash
cd client
npm install
npm run dev
```

前端访问: http://localhost:5173

## 项目目录

```
lbs-geofence-project/
├── server/                 # 后端服务
│   ├── package.json
│   └── app.js             # 主服务文件
├── client/                 # 前端Vue项目
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   └── src/
│       ├── main.js
│       ├── App.vue
│       ├── style.css
│       ├── stores/
│       │   └── viewer.js  # Cesium viewer状态管理
│       └── components/
│           ├── CesiumView.vue    # Cesium地图组件
│           └── GeoFence.vue      # 地理围栏核心组件
└── README.md
```

## 围栏数据说明

默认配置了郑州区域的两个围栏：

1. **园区核心管制区** - 多边形围栏 (113.645-113.655, 34.742-34.752)
2. **圆形禁入区** - 半径500米的圆形围栏 (中心点: 113.65, 34.747)

## 运行效果

1. 打开前端页面后会自动连接 WebSocket
2. Cesium 地图加载并定位到郑州区域
3. 显示绿色的地理围栏区域
4. 蓝色点表示实时人员位置，每2秒自动移动
5. 当人员越界时：
   - 围栏区域变为红色
   - 右下角弹出越界告警通知
   - 状态面板显示"已越界"

## 技术亮点

1. **Turf.js 空间计算**: 专业的GIS点面包含算法，判断精准
2. **WebSocket 实时通信**: 无轮询延迟，真正毫秒级响应
3. **CesiumJS 三维可视化**: 专业级GIS引擎，支持地形、3D视角
4. **Pinia 状态管理**: 全局共享 Cesium viewer 实例
5. **Element Plus UI**: 美观的告警通知和状态展示

## 代码说明

- `node_modules/` 未入库（`.gitignore` 已排除），克隆后需在两个目录各自 `npm install`
- `package-lock.json` 保留，保证依赖版本可复现
- 依赖 `CesiumJS`，首次运行需在 `client` 目录执行 `npm install` 时会下载较大的 Cesium 资源包（数百 MB），这是 Cesium 本身的体积，不是项目代码
- 围栏数据目前写在后端默认配置里（郑州两个示例围栏），改 `server/app.js` 即可替换

## 技术要点（值得借鉴的部分）

1. **点面包含判断不自己做**：直接调 `@turf/boolean-point-in-polygon`，圆形围栏用 `@turf/circle` 先生成多边形再判断——空间几何边界情况太多，用成熟库比自己写可靠
2. **WebSocket 而非轮询**：位置上报频率高（2 秒一次），轮询会产生大量无效请求；长连接天然适合这种场景
3. **前端不重算空间关系**：越界判断放在后端，前端只负责渲染状态，避免"客户端判定和后端不一致"这类经典问题
4. **Cesium viewer 实例用 Pinia 全局共享**：Cesium 实例开销大，多个组件各自 new 一个会直接卡死浏览器

## 运行验证状态

- JavaScript 语法：通过 `node --check` 检查（`server/app.js`、`client/src/**/*.js`、`vite.config.js`）
- 完整运行：需 `npm install` 后启动前后端，本地未在此环境执行（依赖体积较大）
- 前端 `.vue` 文件需 Vite 编译，未做静态语法检查
