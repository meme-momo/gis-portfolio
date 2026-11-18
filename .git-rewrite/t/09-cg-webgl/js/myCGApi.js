import { createProgram } from "./util.js";
// 顶点着色器
const vsSource = `
    attribute vec2 a_position;
    void main() {
        gl_Position = vec4(a_position, 0.0, 1.0);
        gl_PointSize = 1.0;
    }
`;

// 片段着色器
const fsSource = `
    precision mediump float;
    void main() {
        gl_FragColor = vec4(1.0, 0.0, 0.0, 1.0); // 红色
    }
`;

// 获取 WebGL 上下文
const canvas = document.querySelector("#glcanvas");
const gl = canvas.getContext("webgl");
//创建流水程序并绑定
const program = createProgram(gl, vsSource, fsSource);
gl.useProgram(program);
// 创建缓冲区
const positionBuffer = gl.createBuffer();
//获取属性位置，是将数据送入流水的一种方式
const positionLocation = gl.getAttribLocation(program, 'a_position');
// const positionBuffer = gl.createBuffer();
function commonDraw(points,drawType){
    // 使用完全不透明的黑色清除所有图像
    gl.clearColor(0.0, 0.0, 0.0, 1.0);
    // 用上面指定的颜色清除缓冲区
    gl.clear(gl.COLOR_BUFFER_BIT);
    
    gl.bindBuffer(gl.ARRAY_BUFFER, positionBuffer);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(points), gl.STATIC_DRAW);
    // 获取属性位置    
    gl.enableVertexAttribArray(positionLocation);
    gl.vertexAttribPointer(positionLocation, 2, gl.FLOAT, false, 0, 0);

    gl.drawArrays(drawType, 0, points.length / 2);
}
export function testAngle(){
    const points=[-0.5,0,0,0.5,0.5,0]
     commonDraw(points,gl.TRIANGLES)
}
// 归一化坐标到[-1,1]
function normalize(x, y, w, h) {
    return [2 * x / w - 1, 2 * y / h-1];
}
// DDA算法生成像素坐标
export function dda(x1, y1, x2, y2) {
    const points = [];
    const dx = x2 - x1;
    const dy = y2 - y1;
    const steps = Math.max(Math.abs(dx), Math.abs(dy));
    const xInc = dx / steps;
    const yInc = dy / steps;
    let x = x1;
    let y = y1;
    for (let i = 0; i <= steps; i++) {
        points.push(normalize(x, y, canvas.width, canvas.height));
        x += xInc;
        y += yInc;
    }
    commonDraw(points.flat(),gl.POINTS)
}

//中点画线0<k<1
export function midpointLine(x1, y1, x2, y2) {
    const points = [];
    //保证x1<x2
    if(x1>x2){
        [x1,y1,x2,y2]=[x2,y2,x1,y1]
    }
    const dx = x2 - x1,dy = y2 - y1;
    const upd=2*dx-2*dy,downd=-2*dy
    let d=dx-2*dy;
    let x=x1,y=y1;
    while(x<=x2){
        points.push(normalize(x,y,canvas.width,canvas.height));
        if(d<0){
            x+=1;
            y+=1;
            d+=upd;
        }else{
            x+=1;
            d+=downd;
        }
    }
    commonDraw(points.flat(),gl.POINTS)
}
// Bresenham算法（支持四个象限）
export function bresenhamLine(x0, y0, x1, y1) {
    const points = [];
    
    // 处理水平线特殊情况                                                                                                                                   
    if (y0 === y1) {
        const step = (x0 < x1) ? 1 : -1;
        for (let x = x0; x !== x1 + step; x += step) {
            points.push(normalize(x, y0, canvas.width, canvas.height));
        }
        commonDraw(points.flat(), gl.POINTS);
        return;
    }
    
    // 处理垂直线特殊情况
    if (x0 === x1) {
        const step = (y0 < y1) ? 1 : -1;
        for (let y = y0; y !== y1 + step; y += step) {
            points.push(normalize(x0, y, canvas.width, canvas.height));
        }
        commonDraw(points.flat(), gl.POINTS);
        return;
    }
    
    const dx = Math.abs(x1 - x0);
    const dy = Math.abs(y1 - y0);
    const sx = (x0 < x1) ? 1 : -1;
    const sy = (y0 < y1) ? 1 : -1;
    
    let x = x0;
    let y = y0;
    let err = dx - dy;
    
    while (true) {
        points.push(normalize(x, y, canvas.width, canvas.height));
        
        if (x === x1 && y === y1) break;
        
        const e2 = err << 1;
        
        if (e2 > -dy) {
            err -= dy;
            x += sx;
        }
        
        if (e2 < dx) {
            err += dx;
            y += sy;
        }
    }
    
    commonDraw(points.flat(), gl.POINTS);
}
