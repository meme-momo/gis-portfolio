# 05 · AsiaGIS 桌面 GIS 软件

> 一个用 C# WinForms 从零写的桌面 GIS 小工具
> 代码量：约 2484 行（`GISForm.cs` 1849 行 + 设计器 530 行 + 图层类 84 行 + 入口 21 行）
> 技术栈：C# / .NET Framework 4.8 / WinForms / GDI+

## 特别之处

整个项目**没有引用任何第三方 GIS 库**（无 SharpMap、无 DotSpatial、无 ArcObjects），`csproj` 里只有 `System.*` 系列。地图的绘制、坐标变换、缩放漫游、要素查询全部基于 `System.Drawing` 自己实现。

这意味着里面能读到的东西很原始：屏幕坐标与地图坐标怎么互转、重绘时怎么裁掉视野外的要素、鼠标滚轮怎么以光标为中心缩放。

## 功能

| 菜单 | 功能 |
|---|---|
| 文件 → 打开 | 打开矢量图层 |
| 操作 → 放大 / 缩小 / 漫游 / 全图 | 视图控制（`mainpanel_MouseWheel`、`MouseDown`/`MouseUp`/`MouseMove` 组合实现） |
| 查询 → 点查询 / 线查询 / 面查询 | 交互式空间查询 |
| 编辑 | 要素编辑 |

## 代码结构

```
05-asiagis-desktop/
├── AsiaGIS.sln
├── AsiaGIS.csproj           .NET Framework 4.8，WinExe
├── Program.cs               程序入口
├── GISForm.cs               主窗体：渲染引擎 + 交互逻辑（1849 行）
├── GISForm.Designer.cs      界面布局（工具条、菜单、绘图面板）
├── GISForm.resx
├── ZBALayer.cs              图层封装类
├── app.config
├── Properties/              程序集信息
├── Resources/               界面资源
└── 图标/                    工具条图标（ico / png）
```

`ZBALayer.cs` 是理解整个程序的钥匙——每个图层一个对象，持有几何数据与样式，`GISForm` 负责把图层按顺序画到面板上。

## 编译运行

1. Visual Studio 2019 或更高版本（需安装 **.NET Framework 4.8 开发工具**）
2. 打开 `AsiaGIS.sln`，直接 F5
3. 需要 Windows 环境

> 仓库只保留了源码与资源，`bin/`、`obj/`、`.vs/` 已被 `.gitignore` 排除。

## 为什么值得看

课程里的 GIS 开发作业通常是「拖控件 + 调接口」，而这个项目把**渲染循环**和**坐标变换**自己写了一遍。做过这一步之后，用 ArcGIS 时对「为什么缩放后要素变模糊」「为什么大图层会卡」这类问题会有完全不同的理解。

## 备注

程序当时是课程作业，界面用 WinForms 拖的，没有做异常处理的完善（打开非矢量文件可能直接抛错）。功能可用，但请不要当生产工具用。
