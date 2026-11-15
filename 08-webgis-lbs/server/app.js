const express = require('express');
const cors = require('cors');
const http = require('http');
const WebSocket = require('ws');
const turf = require('@turf/turf');

const app = express();
app.use(cors());
app.use(express.json());
const server = http.createServer(app);
const PORT = 3001;

// 在线客户端连接池
const wss = new WebSocket.Server({ server });
let clientList = new Set();

// 地理围栏数据
const fenceList = [
  {
    id: 1,
    name: "园区核心管制区",
    type: "polygon",
    coordinates: [
      [113.645, 34.752],
      [113.655, 34.752],
      [113.655, 34.742],
      [113.645, 34.742],
      [113.645, 34.752]
    ]
  },
  {
    id: 2,
    name: "圆形禁入区",
    type: "circle",
    center: [113.65, 34.747],
    radius: 500
  }
];

// HTTP接口:获取围栏列表
app.get('/api/fence/list', (req, res) => {
  res.json({ code: 200, data: fenceList });
});

// WebSocket连接管理
wss.on('connection', (ws) => {
  console.log("客户端已接入实时围栏监控");
  clientList.add(ws);

  // 监听前端上报的实时GPS位置
  ws.on('message', (data) => {
    try {
      const { lng, lat, userId } = JSON.parse(data);
      const userPoint = turf.point([lng, lat]);
      let isOutOfFence = false;
      let warnFence = null;

      // 遍历所有围栏做空间判断
      for (const fence of fenceList) {
        if (fence.type === 'polygon') {
          const poly = turf.polygon([fence.coordinates]);
          if (!turf.booleanPointInPolygon(userPoint, poly)) {
            isOutOfFence = true;
            warnFence = fence;
          } else {
            isOutOfFence = false;
            warnFence = null;
            break;
          }
        } else if (fence.type === 'circle') {
          const circleGeom = turf.circle(fence.center, fence.radius, { 
            units: 'meters' 
          });
          if (!turf.booleanPointInPolygon(userPoint, circleGeom)) {
            isOutOfFence = true;
            warnFence = fence;
          } else {
            isOutOfFence = false;
            warnFence = null;
            break;
          }
        }
      }

      // 实时推送位置+越界告警给当前客户端
      const sendData = {
        type: 'position_update',
        userId,
        lng,
        lat,
        isOutOfFence,
        fence: warnFence
      };
      
      ws.send(JSON.stringify(sendData));

      // 全局广播(可选:多客户端实时同步人员位置)
      clientList.forEach(client => {
        if (client.readyState === WebSocket.OPEN && client !== ws) {
          client.send(JSON.stringify(sendData));
        }
      });

    } catch (err) {
      console.error("位置解析异常", err);
    }
  });

  ws.on('close', () => {
    clientList.delete(ws);
    console.log("客户端断开连接");
  });
});

server.listen(PORT, () => {
  console.log(`========================================`);
  console.log(`实时LBS地理围栏服务启动成功!`);
  console.log(`HTTP服务地址: http://localhost:${PORT}`);
  console.log(`WebSocket地址: ws://localhost:${PORT}`);
  console.log(`围栏API: http://localhost:${PORT}/api/fence/list`);
  console.log(`========================================`);
});
