# 09 · WebGL 图形学实验框架

> 课程：计算机图形学
> 内容：从零搭一个 WebGL 二维绘图框架，并在上面实现基本图形算法

## 做了什么

不是直接调 three.js 画个三角形，而是把 WebGL 那条流水线手动走了一遍：

```
JavaScript 顶点数据
      ↓ bufferData
GPU 缓冲区
      ↓ vertexAttribPointer
顶点着色器（GLSL）
      ↓ 图元装配
片元着色器（GLSL）
      ↓
Canvas 上的像素
```

框架拆成三层：

| 文件 | 职责 |
|---|---|
| `index.html` | 承载 `<canvas id="glcanvas">`，触发不同算法 |
| `js/util.js` | 通用工具：编译着色器、链接程序、检查编译错误 |
| `js/myCGApi.js` | 算法实现层（GLSL 着色器源码 + 绘制函数 + 具体算法） |
| `js/index.js` | 入口：初始化上下文并演示绘制 |

## 已实现的算法

**1. 三角形绘制（框架验证）**

用三个顶点跑通整条流水线，确认着色器与缓冲区都正常：

```javascript
export function testAngle() {
    const points = [-0.5, 0, 0, 0.5, 0.5, 0]   // 三个顶点
    commonDraw(points, gl.TRIANGLES)
}
```

**2. Bresenham 直线算法**

经典光栅化算法，只用整数加减和误差项判断，不做浮点除法，逐像素生成直线：

```javascript
export function bresenhamLine(x0, y0, x1, y1) {
    let dx = Math.abs(x1 - x0), dy = Math.abs(y1 - y0)
    const sx = x0 < x1 ? 1 : -1, sy = y0 < y1 ? 1 : -1
    let err = dx - dy
    while (true) {
        // 屏幕坐标 → 标准化设备坐标（NDC，-1 ~ 1）
        points.push((x0 / canvas.width) * 2 - 1, (y0 / canvas.height) * 2 - 1)
        if (x0 === x1 && y0 === y1) break
        const e2 = 2 * err
        if (e2 > -dy) { err -= dy; x0 += sx }
        if (e2 < dx)  { err += dx; y0 += sy }
    }
}
```

这里有个容易忽略的细节：**屏幕坐标以像素为单位，WebGL 用的是 -1~1 的标准化设备坐标（NDC）**，每个点都要转换，否则点会堆在画布一角。

## 运行

浏览器不能直接打开 `index.html`（ES Module 有跨域限制），需要一个本地服务器：

```bash
# 方式一：VS Code 装 Live Server 插件，右键 index.html → Open with Live Server
# 方式二：命令行
python -m http.server 8000
# 访问 http://localhost:8000
```

需要浏览器支持 WebGL（现代浏览器默认支持）。

## 为什么值得留档

图形学算法书上都有，但**把算法变成屏幕上的像素**这一步，只有自己接过着色器和缓冲区才会真正理解。做完这个再回头看「为什么要坐标转换」「为什么点太小看不见」，就不是背概念了。

顶点着色器里的 `gl_PointSize = 1.0` 也是个坑：不设的话点的大小依赖实现，部分显卡上会完全看不到。

## 说明

课程提供的教程文档未包含在仓库中，这里只保留自己写的代码。
