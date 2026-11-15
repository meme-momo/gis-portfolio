# meme-momo · 地理信息科学 项目代码集

地理信息科学专业。这里收录了我参与的**生态修复评估、国土空间评价、空间统计建模**项目代码，以及一个用 C# 手写的桌面 GIS 小工具。

代码来自真实项目和竞赛作品，保留原始写法（含中文注释、绝对路径），没有为了好看而重写——这样更能看出当时的思路。

## 项目一览

| # | 项目 | 领域 | 核心方法 / 技术 | 目录 |
|---|---|---|---|---|
| 01 | 南太行生态修复成效评估 | 国土空间生态修复 | ArcPy 空间统计、InVEST 模型（PM2.5 / 土壤保持 / 生境质量） | [`01-nantaihang-restoration`](01-nantaihang-restoration/) |
| 02 | 临汾废弃矿山修复工程 | 矿山生态修复 | ArcPy 矢量处理、斑块（patch）分析、问卷数据可视化 | [`02-linfen-mine-restoration`](02-linfen-mine-restoration/) |
| 03 | 全国油茶种植适宜性评价 | 农业空间适宜性 | 多因子隶属度函数（抛物线型/反S型）、Rasterio 栅格对齐与叠加、重点县提取 | [`03-land-suitability`](03-land-suitability/) |
| 04 | 城市群发展空间异质性建模 | 空间统计 / 计量地理 | MGWR、地理探测器、7 模型 LOOCV 对比、XGBoost + SHAP | [`04-mgwr-shap`](04-mgwr-shap/) |
| 05 | AsiaGIS 桌面 GIS 软件 | GIS 二次开发 | C# WinForms + GDI+，自实现矢量渲染、缩放漫游、要素查询 | [`05-asiagis-desktop`](05-asiagis-desktop/) |
| 06 | ArcGIS Pro 课程实践报告 | 空间分析实践 | ArcGIS Pro 空间分析、专题制图 | [`06-arcgis-coursework`](06-arcgis-coursework/) |

## 一条主线

四个数据类项目其实是一个递进关系：

```
多因子评价（03 油茶适宜性：气候/土壤/地形 → 隶属度 → 综合适宜性）
        ↓ 尺度放大到流域，加入工程实施口径
生态服务核算（01 南太行：三类服务 + 渔网权重体系）
        ↓ 从「算出来」到「算得准、讲得清」
空间统计建模（04 城市群：MGWR 局部系数 + 地理探测器 + 7 模型对照）
        ↓ 工具化，把渲染和交互自己实现一遍
桌面 GIS（05 AsiaGIS：C# 自绘矢量地图）
```

## 技术栈

| 类别 | 工具 |
|---|---|
| 空间数据处理 | ArcGIS Pro / ArcPy、QGIS、Rasterio、GeoPandas、GDAL |
| 生态评估模型 | InVEST（产水、土壤保持、生境质量、碳储量）、PLUS 土地利用模拟 |
| 统计与建模 | MGWR、地理探测器、scikit-learn、XGBoost、SHAP、Statsmodels |
| 可视化 | Matplotlib（出版级图表，统一字体字号与 dpi）、ArcGIS 制图 |
| 开发 | Python 3.11、C# / .NET Framework 4.8、Git |

## 目录结构

```
.
├── 01-nantaihang-restoration/
│   ├── scripts/     ArcPy 空间统计脚本（渔网统计、权重计算、矢量分类）
│   ├── weights/     指标权重计算（Notebook）
│   ├── analysis/    InVEST 三类生态系统服务评估（Notebook）
│   └── figures/     出图脚本（批量导出、规范命名、柱状图）
├── 02-linfen-mine-restoration/scripts/
├── 03-land-suitability/scripts/
├── 04-mgwr-shap/{mgwr,shap}/
├── 05-asiagis-desktop/      C# 源码（不含 bin/obj）
└── 06-arcgis-coursework/    实验报告
```

## 运行说明

**数据不在仓库里。** 遥感影像、矢量数据、项目原始资料体积动辄几百 MB 到几 GB，且部分受项目方保密要求限制，因此各项目 README 只说明数据来源、目录结构与字段，代码运行时需自行放回 `data/` 或修改脚本顶部的路径变量。

**两套环境**：

```bash
# 1. ArcPy 脚本（01、02）——必须在 ArcGIS Pro 自带的 Python 环境里跑
#    ArcGIS Pro → 分析 → Python 命令提示符，然后 python xxx.py
#    脚本里的 arcpy.CheckOutExtension("Spatial") 需有 Spatial Analyst 许可

# 2. 开源栈（03、04）——普通 conda 环境即可
conda create -n gis python=3.11
pip install -r requirements.txt
```

**路径要改。** 原始脚本多写成 `F:\dasai\...` 这类绝对路径，运行前请改成自己的数据位置。

## 关于代码质量

- 部分脚本是为一次性分析任务写的（变量命名简短、逻辑集中在一个文件里），我保留原样，未做工程化重构
- 项目 04 是其中方法最完整的一个：包含模型选择、交叉验证、显著性检验的完整链路，可直接复用
- 项目 05 是唯一带界面的作品，2484 行 C# 代码

## 联系

- Gitee：[@sang-yehao](https://gitee.com/sang-yehao)
- 论文写作仓库：[paper](https://gitee.com/sang-yehao/paper)

## License

[MIT](LICENSE) —— 代码可自由参考，但请勿直接用于课程作业提交。
