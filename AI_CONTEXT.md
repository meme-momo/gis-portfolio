# AI_CONTEXT.md · 项目交接说明

> 如果你是被邀请来接手这个仓库的 AI 助手，**先读完这一页**再动手。这里写了项目全貌、运行方式、以及必须遵守的约定。

## 这个仓库是什么

地理信息科学方向的项目代码集，9 个独立项目，覆盖：生态修复成效评估、国土空间适宜性评价、空间统计建模（MGWR/SHAP）、桌面 GIS 开发、WebGIS、计算机图形学。

代码来自真实项目和竞赛作品，**保留原始写法**（中文注释、单文件集中逻辑），没有为了好看而做工程化重构——这是刻意的，便于对照当时的分析思路。

## 项目索引

| 目录 | 主题 | 核心技术 | 有无成果图 |
|---|---|---|---|
| `01-nantaihang-restoration` | 南太行生态修复成效评估（竞赛作品） | ArcPy 渔网统计、指标权重、InVEST 三类服务（PM2.5/土壤保持/生境质量） | 6 张 |
| `02-linfen-mine-restoration` | 废弃矿山修复工程数据支撑 | ArcPy 图斑归并、字段归一、分县统计 | — |
| `03-land-suitability` | 全国油茶种植适宜性评价 | 隶属度函数（抛物线型/反S型）、Rasterio 栅格对齐叠加、重点县提取 | 待补 |
| `04-mgwr-shap` | 城市群发展空间异质性 | MGWR、地理探测器、7 模型 LOOCV 对比、XGBoost+SHAP | 8 张 |
| `05-asiagis-desktop` | 桌面 GIS 软件 | C# WinForms + GDI+，无第三方 GIS 库，自实现渲染/缩放/查询 | 待补截图 |
| `06-arcgis-coursework` | 课程实验报告 | ArcGIS Pro 空间分析 | — |
| `07-python-toolbox` | 实用脚本集 | requests/BeautifulSoup 爬虫、Pillow 批处理、arcpy 字段翻译 | — |
| `08-webgis-lbs` | 实时地理围栏 LBS | Node+Express+WebSocket+Turf.js / Vue3+Vite+CesiumJS | — |
| `09-cg-webgl` | WebGL 图形学实验 | 手写 GLSL 着色器、Bresenham 直线算法 | — |

## 文件命名规则（改动时请遵守）

- 项目目录：`01-` ~ `09-` = 建议浏览顺序
- 项目内脚本：`01_`、`02_`… = 阅读/执行顺序；无前缀的是配置或说明
- 成果图：`fig1_`、`fig2_`… = 论文中出现的顺序

**改名后必须同步更新对应 README 里的脚本清单表格**，否则文档与代码对不上。

## 运行环境（三套，别混用）

```bash
# 1) ArcPy 脚本（01、02、07 的字段翻译）——只能在 ArcGIS Pro 自带 Python 里跑
#    需要 Spatial Analyst 许可；arcpy 无法 pip 安装

# 2) 开源栈（03、04、07 其余脚本）
pip install -r requirements.txt
# 含 rasterio / geopandas / scikit-learn / xgboost / shap / mgwr / libpysal / esda

# 3) Web 项目（08、09）
cd 08-webgis-lbs/server && npm install && npm start   # 后端 :3001
cd 08-webgis-lbs/client && npm install && npm run dev # 前端 :5173
cd 09-cg-webgl && python -m http.server 8000          # 09 不能直接双击 html，ES Module 需要本地服务
```

## 数据说明（重要）

**仓库里没有数据。** 遥感影像、矢量、项目原始资料体积从几百 MB 到数 GB，且部分受项目方保密要求限制，一律未入库。

每个项目 README 里写了数据来源、目录结构和字段要求。运行前需自备数据并放到项目对应目录，或修改脚本顶部的 `base_dir` / `*_PATH` 变量。

**脚本里的路径已统一改为相对路径**（如 `r"dasai\南太行数据"`），不是笔误，请勿擅自改回绝对路径。

## 已做的质量处理

| 项 | 说明 |
|---|---|
| 语法检查 | 全部 `.py` 通过 `py_compile` + `pyflakes`；`.ipynb` 逐单元格 `compile`；`.js` 通过 `node --check` |
| 隐私脱敏 | 无真实姓名、学校、学号、手机号、邮箱、个人目录、登录凭证 |
| 体积控制 | 成果图压缩（地图 JPEG q85、图表 PNG 无损），全仓库约 9.5 MB |
| 代码修复 | 有 1 个脚本原为两段代码交叉粘贴导致无法运行，已按功能拆分为两个独立脚本 |

## 给接手 AI 的约定（请遵守）

1. **不要**往仓库写入：个人绝对路径、账号信息、Cookie、API 密钥、密码
2. **不要**提交数据文件、遥感影像、模型权重、`node_modules/`（`.gitignore` 已覆盖，别用 `-f` 强推）
3. 保持**中文注释**和原有代码风格；不要为了"规范"做大范围重构
4. 新增依赖要写进 `requirements.txt`，并注明属于哪套环境
5. 改完代码跑一遍检查：`.py` → `py_compile` + `pyflakes`；`.ipynb` → 逐单元格 compile；`.js` → `node --check`
6. 发现代码里有疑似敏感信息（Cookie、key、真实姓名），**先提醒用户再动手**
7. 回答用中文；给命令要能直接复制执行

## 建议的阅读顺序

想快速判断这个仓库的水平，按这个顺序看：

1. `README.md` 顶部的成果预览图（2 张）
2. `04-mgwr-shap/README.md` —— 方法链路最完整，含真实指标与过拟合分析
3. `01-nantaihang-restoration/README.md` —— 工程量最大，15 个脚本按阶段编号
4. `05-asiagis-desktop/ZBALayer.cs` —— 理解 C# 自绘渲染的入口
5. `08-webgis-lbs/README.md` —— 唯一的全栈项目
