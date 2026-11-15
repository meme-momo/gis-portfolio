# -*- coding: utf-8 -*-
"""
MGWR + 地理探测器 + 精度提升框架
--------------------------------
输出内容：
1. MGWR 模型精度、带宽、预测值、残差、局部系数数据表
2. 地理探测器 q 值、交互探测矩阵与交互类型数据表
3. 非地图型论文图表：q 值图、交互热力图、精度对比图、拟合图、残差图等
4. 自动比较多种预测模型，给出当前数据下精度最高的模型
"""

import os
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

import geopandas as gpd
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from esda.moran import Moran, Moran_Local
from libpysal.weights import Queen
from libpysal.weights.spatial_lag import lag_spatial
from matplotlib.colors import ListedColormap, TwoSlopeNorm
from matplotlib.patches import Patch
from mgwr.gwr import MGWR
from mgwr.sel_bw import Sel_BW
from sklearn.ensemble import ExtraTreesRegressor, GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import Lasso, LinearRegression, Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import LeaveOneOut, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR


# =========================================================
# 1. 参数设置（根据实际数据修改此部分）
# =========================================================

EXCEL_PATH = r"data.csv"            # 属性数据路径
SHP_PATH = r"shp\city.shp"            # 矢量面数据路径
OUT_DIR = r"./output"              # 输出文件夹

CITY_FIELD = "name"                # 城市名称字段（若不存在，会按经纬度匹配）
LON_COL = "lon"
LAT_COL = "lat"
TARGET_COL = "XHM"                # 目标变量

# 特征变量中英文映射（可按需增删）
FEATURE_CN_MAP = {
    "Feat1": "人均GDP",
    "Feat2": "专利/万人",
    "Feat3": "对外开放度",
    "Feat4": "产业高级化",
    "Feat5": "科技支出占比",
    "Feat6": "交通可达性",
    "Feat7": "普惠金融指数",
}

TARGET_CN_NAME = "目标变量"
FEATURE_COLS = list(FEATURE_CN_MAP.keys())
FEATURE_NAMES = [FEATURE_CN_MAP[col] for col in FEATURE_COLS]

os.makedirs(OUT_DIR, exist_ok=True)

# 图形全局设置：兼顾 SCI 英文字体与中文标题显示
mpl.rcParams.update(
    {
        "font.family": ["Times New Roman", "SimHei", "Microsoft YaHei", "Arial Unicode MS"],
        "font.size": 12,
        "axes.labelsize": 13,
        "axes.titlesize": 15,
        "legend.fontsize": 10,
        "figure.dpi": 300,
        "savefig.dpi": 600,
        "axes.linewidth": 1.2,
        "xtick.direction": "in",
        "ytick.direction": "in",
        "axes.unicode_minus": False,
    }
)
sns.set_theme(style="ticks", font="SimHei")

TITLE_FONT = {"family": "SimHei", "size": 15}

INVALID_FILENAME_CHARS = str.maketrans({char: "_" for char in r'\/:*?"<>|'})


def safe_filename(name):
    return name.translate(INVALID_FILENAME_CHARS)


def save_fig(filename):
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, safe_filename(filename)), bbox_inches="tight", facecolor="white")
    plt.close()


def apply_clean_axis(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="x", linestyle="--", linewidth=0.7, alpha=0.25)


def diverging_norm(series):
    clean = pd.Series(series).dropna()
    if clean.empty:
        return None

    vmin = clean.min()
    vmax = clean.max()
    if vmin < 0 < vmax:
        return TwoSlopeNorm(vmin=vmin, vcenter=0, vmax=vmax)
    return None


def rmse(y_true, y_pred):
    return mean_squared_error(y_true, y_pred) ** 0.5


def adjusted_r2(y_true, y_pred, p):
    n = len(y_true)
    r2 = r2_score(y_true, y_pred)
    return 1 - (1 - r2) * (n - 1) / (n - p - 1)


def load_data(path):
    file_ext = os.path.splitext(path)[1].lower()
    if file_ext == ".csv":
        try:
            data = pd.read_csv(path, encoding="utf-8")
        except UnicodeDecodeError:
            data = pd.read_csv(path, encoding="gbk")
    elif file_ext == ".xlsx":
        data = pd.read_excel(path, engine="openpyxl")
    elif file_ext == ".xls":
        data = pd.read_excel(path, engine="xlrd")
    else:
        raise ValueError(f"不支持的数据文件格式：{file_ext}")

    data = data.drop(columns=[col for col in data.columns if str(col).startswith("Unnamed")], errors="ignore")
    return data


def load_shp(path):
    if os.path.exists(path):
        return gpd.read_file(path)

    shp_files = list(Path("shp").glob("*.shp"))
    if not shp_files:
        raise FileNotFoundError("shp 文件夹中未找到 .shp 文件，无法计算 Moran's I。")
    return gpd.read_file(shp_files[0])


def fill_city_name_by_coords(data, gdf):
    if CITY_FIELD in data.columns:
        return data

    if {"x", "y"}.issubset(gdf.columns):
        shp_coords = gdf[["x", "y"]].to_numpy()
    else:
        shp_centroids = gdf.geometry.centroid
        shp_coords = np.column_stack([shp_centroids.x, shp_centroids.y])

    data_coords = data[[LON_COL, LAT_COL]].to_numpy()
    distances = np.sqrt(((data_coords[:, None, :] - shp_coords[None, :, :]) ** 2).sum(axis=2))
    nearest_idx = distances.argmin(axis=1)

    if len(set(nearest_idx)) != len(data):
        raise ValueError("经纬度匹配 shp 城市时出现重复匹配，请检查数据坐标。")

    data[CITY_FIELD] = gdf.iloc[nearest_idx][CITY_FIELD].to_numpy()
    print(f"CSV 缺少 {CITY_FIELD} 字段，已按经纬度匹配 shp 城市。")
    return data


def geodetector_q(y, x):
    temp = pd.DataFrame({"y": y, "x": x}).dropna()
    total_n = len(temp)
    total_var = np.var(temp["y"], ddof=1)
    if total_var == 0 or total_n == 0:
        return np.nan

    q = 1
    for group in temp["x"].unique():
        sub = temp[temp["x"] == group]
        if len(sub) <= 1:
            group_var = 0
        else:
            group_var = np.var(sub["y"], ddof=1)
        q -= (len(sub) * group_var) / (total_n * total_var)
    return q


def discretize(series, bins=5):
    return pd.qcut(series, q=bins, duplicates="drop")


def classify_interaction(q1, q2, q12):
    min_q = min(q1, q2)
    max_q = max(q1, q2)
    sum_q = q1 + q2

    if q12 < min_q:
        return "非线性减弱"
    if min_q <= q12 < max_q:
        return "单因子非线性减弱"
    if np.isclose(q12, sum_q):
        return "独立"
    if max_q < q12 < sum_q:
        return "双因子增强"
    if q12 > sum_q:
        return "非线性增强"
    return "增强"


def run_mgwr(data):
    x = data[FEATURE_COLS].values
    y = data[TARGET_COL].values.reshape((-1, 1))
    coords = list(zip(data[LON_COL], data[LAT_COL]))

    scaler = StandardScaler()
    x_scaled = scaler.fit_transform(x)

    n_obs = len(data)
    n_features_with_const = x_scaled.shape[1] + 1
    min_bw = max(n_features_with_const + 2, 10)
    max_bw = n_obs - 1

    if max_bw < min_bw:
        raise ValueError(
            f"样本量过小，无法进行 MGWR 带宽搜索：样本量={n_obs}，"
            f"变量数含截距={n_features_with_const}。"
        )

    print(f"\nMGWR 带宽搜索中：样本量={n_obs}，搜索范围={min_bw}-{max_bw}")

    selector = Sel_BW(coords, y, x_scaled, multi=True, n_jobs=1)
    bw = selector.search(
        init_multi=max_bw,
        bw_min=min_bw,
        bw_max=max_bw,
        multi_bw_min=[min_bw],
        multi_bw_max=[max_bw],
    )

    print("最优带宽：", bw)

    model = MGWR(coords, y, x_scaled, selector)
    results = model.fit()
    pred = results.predy.flatten()
    y_flat = y.flatten()

    result_data = data.copy()
    result_data["MGWR_pred"] = pred
    result_data["MGWR_resid"] = y_flat - pred
    result_data["MGWR_abs_resid"] = np.abs(result_data["MGWR_resid"])

    params = results.params
    result_data["Intercept_coef"] = params[:, 0]
    for idx, col in enumerate(FEATURE_COLS):
        result_data[f"{col}_coef"] = params[:, idx + 1]
        result_data[f"{FEATURE_CN_MAP[col]}_局部系数"] = params[:, idx + 1]

    try:
        local_r2 = np.asarray(results.localR2).flatten()
    except (AttributeError, NotImplementedError):
        local_r2 = None
    if local_r2 is not None:
        result_data["Local_R2"] = local_r2

    try:
        tvalues = np.asarray(results.tvalues)
    except (AttributeError, NotImplementedError):
        tvalues = None
    if tvalues is not None and tvalues.shape[1] >= len(FEATURE_COLS) + 1:
        for idx, col in enumerate(FEATURE_COLS):
            result_data[f"{col}_t"] = tvalues[:, idx + 1]
            result_data[f"{FEATURE_CN_MAP[col]}_t值"] = tvalues[:, idx + 1]
            result_data[f"{FEATURE_CN_MAP[col]}_显著"] = np.abs(tvalues[:, idx + 1]) >= 1.96

    metrics = pd.DataFrame(
        [
            {
                "模型": "MGWR",
                "训练R2": r2_score(y_flat, pred),
                "调整R2": adjusted_r2(y_flat, pred, len(FEATURE_COLS)),
                "RMSE": rmse(y_flat, pred),
                "MAE": mean_absolute_error(y_flat, pred),
                "AIC": getattr(results, "aic", np.nan),
                "AICc": getattr(results, "aicc", np.nan),
                "BIC": getattr(results, "bic", np.nan),
            }
        ]
    )

    bw_table = pd.DataFrame(
        {
            "变量": ["截距"] + FEATURE_NAMES,
            "带宽": np.asarray(bw).astype(float),
        }
    )

    coef_summary = result_data[
        ["Intercept_coef"] + [f"{col}_coef" for col in FEATURE_COLS]
    ].describe().T.reset_index()
    coef_summary["变量"] = ["截距"] + FEATURE_NAMES
    coef_summary = coef_summary[["变量", "mean", "std", "min", "25%", "50%", "75%", "max"]]

    return result_data, metrics, bw_table, coef_summary


def compare_prediction_models(data):
    x = data[FEATURE_COLS].values
    y = data[TARGET_COL].values
    loo = LeaveOneOut()

    models = {
        "线性回归": Pipeline([("scaler", StandardScaler()), ("model", LinearRegression())]),
        "Ridge": Pipeline([("scaler", StandardScaler()), ("model", Ridge(alpha=1.0))]),
        "Lasso": Pipeline([("scaler", StandardScaler()), ("model", Lasso(alpha=0.001, max_iter=10000))]),
        "SVR-RBF": Pipeline([("scaler", StandardScaler()), ("model", SVR(C=10, gamma="scale", epsilon=0.01))]),
        "随机森林": RandomForestRegressor(n_estimators=300, random_state=42, min_samples_leaf=1),
        "极端随机树": ExtraTreesRegressor(n_estimators=300, random_state=42, min_samples_leaf=1),
        "梯度提升树": GradientBoostingRegressor(n_estimators=200, learning_rate=0.03, max_depth=2, random_state=42),
    }

    rows = []
    predictions = {}
    fitted_models = {}

    print("\n比较预测模型精度（Leave-One-Out 交叉验证）...")
    for name, model in models.items():
        cv_pred = cross_val_predict(model, x, y, cv=loo)
        model.fit(x, y)
        train_pred = model.predict(x)

        rows.append(
            {
                "模型": name,
                "训练R2": r2_score(y, train_pred),
                "LOOCV_R2": r2_score(y, cv_pred),
                "LOOCV_RMSE": rmse(y, cv_pred),
                "LOOCV_MAE": mean_absolute_error(y, cv_pred),
            }
        )

        predictions[name] = {"train": train_pred, "cv": cv_pred}
        fitted_models[name] = model

    accuracy = pd.DataFrame(rows).sort_values("LOOCV_R2", ascending=False)
    best_name = accuracy.iloc[0]["模型"]
    best_model = fitted_models[best_name]

    best_pred_table = data[[CITY_FIELD, TARGET_COL]].copy()
    best_pred_table["最优模型"] = best_name
    best_pred_table["预测值"] = predictions[best_name]["train"]
    best_pred_table["LOOCV预测值"] = predictions[best_name]["cv"]
    best_pred_table["训练残差"] = best_pred_table[TARGET_COL] - best_pred_table["预测值"]
    best_pred_table["LOOCV残差"] = best_pred_table[TARGET_COL] - best_pred_table["LOOCV预测值"]

    feature_importance = None
    if hasattr(best_model, "feature_importances_"):
        feature_importance = pd.DataFrame(
            {
                "变量": FEATURE_NAMES,
                "重要性": best_model.feature_importances_,
            }
        ).sort_values("重要性", ascending=False)

    return accuracy, best_pred_table, feature_importance


def run_geodetector(data):
    q_rows = []
    bins_map = {}

    for col in FEATURE_COLS:
        bins = discretize(data[col], bins=5)
        bins_map[col] = bins
        q_rows.append(
            {
                "变量": FEATURE_CN_MAP[col],
                "字段": col,
                "q值": geodetector_q(data[TARGET_COL], bins),
            }
        )

    q_df = pd.DataFrame(q_rows).sort_values("q值", ascending=False)

    interaction_matrix = pd.DataFrame(index=FEATURE_NAMES, columns=FEATURE_NAMES, dtype=float)
    interaction_rows = []

    q_lookup = dict(zip(q_df["字段"], q_df["q值"]))
    for col1 in FEATURE_COLS:
        for col2 in FEATURE_COLS:
            interaction = bins_map[col1].astype(str) + "_" + bins_map[col2].astype(str)
            q_inter = geodetector_q(data[TARGET_COL], interaction)
            interaction_matrix.loc[FEATURE_CN_MAP[col1], FEATURE_CN_MAP[col2]] = q_inter

            if FEATURE_COLS.index(col1) < FEATURE_COLS.index(col2):
                q1 = q_lookup[col1]
                q2 = q_lookup[col2]
                interaction_rows.append(
                    {
                        "变量1": FEATURE_CN_MAP[col1],
                        "变量2": FEATURE_CN_MAP[col2],
                        "q1": q1,
                        "q2": q2,
                        "q交互": q_inter,
                        "交互增量": q_inter - max(q1, q2),
                        "交互类型": classify_interaction(q1, q2, q_inter),
                    }
                )

    interaction_long = pd.DataFrame(interaction_rows).sort_values("q交互", ascending=False)
    return q_df, interaction_matrix, interaction_long


def compute_spatial_diagnostics(data, gdf):
    spatial_data = gdf.merge(data[[CITY_FIELD, TARGET_COL]], on=CITY_FIELD)
    w = Queen.from_dataframe(spatial_data)
    w.transform = "r"
    moran = Moran(spatial_data[TARGET_COL], w)
    lisa = Moran_Local(spatial_data[TARGET_COL], w)

    spatial_data["LISA_q"] = lisa.q
    spatial_data["LISA_p"] = lisa.p_sim
    spatial_data["LISA类型"] = np.select(
        [
            (lisa.q == 1) & (lisa.p_sim < 0.05),
            (lisa.q == 2) & (lisa.p_sim < 0.05),
            (lisa.q == 3) & (lisa.p_sim < 0.05),
            (lisa.q == 4) & (lisa.p_sim < 0.05),
        ],
        ["HH 热点", "LH 异常低值", "LL 冷点", "HL 异常高值"],
        default="不显著",
    )

    moran_df = pd.DataFrame(
        [
            {
                "指标": TARGET_CN_NAME,
                "Moran_I": moran.I,
                "P_value": moran.p_sim,
                "Z_score": moran.z_sim,
                "LISA显著单元数": int((lisa.p_sim < 0.05).sum()),
            }
        ]
    )
    return moran_df, spatial_data, w, moran


def make_charts(result_data, q_df, interaction_matrix, interaction_long, accuracy, best_pred_table, feature_importance):
    print("\n绘制非地图统计图表...")

    palette = sns.color_palette("Blues_r", n_colors=len(q_df))

    plt.figure(figsize=(10, 6))
    ax = sns.barplot(data=q_df, x="q值", y="变量", palette=palette)
    for container in ax.containers:
        ax.bar_label(container, fmt="%.3f", padding=4, fontsize=10)
    ax.set_title("地理探测器 q 值排序", fontsize=18, pad=14)
    ax.set_xlabel("q 值")
    ax.set_ylabel("")
    apply_clean_axis(ax)
    save_fig("01_地理探测器_q值排序.png")

    plt.figure(figsize=(10, 6))
    sorted_q = q_df.sort_values("q值")
    plt.hlines(y=sorted_q["变量"], xmin=0, xmax=sorted_q["q值"], color="#b7c9d6", linewidth=3)
    plt.scatter(sorted_q["q值"], sorted_q["变量"], s=180, c=sorted_q["q值"], cmap="viridis", edgecolor="white", linewidth=1.5)
    for _, row in sorted_q.iterrows():
        plt.text(row["q值"] + 0.008, row["变量"], f"{row['q值']:.3f}", va="center", fontsize=10)
    plt.title("影响因子解释力棒棒糖图", fontsize=18, pad=14)
    plt.xlabel("q 值")
    plt.ylabel("")
    apply_clean_axis(plt.gca())
    save_fig("02_q值棒棒糖图.png")

    plt.figure(figsize=(9.5, 8))
    mask = np.tril(np.ones_like(interaction_matrix, dtype=bool), k=-1)
    sns.heatmap(
        interaction_matrix,
        mask=mask,
        annot=True,
        fmt=".3f",
        cmap="RdYlBu_r",
        square=True,
        linewidths=0.8,
        linecolor="white",
        cbar_kws={"label": "q 交互值"},
    )
    plt.title("地理探测器交互探测热力图", fontsize=18, pad=14)
    plt.xticks(rotation=35, ha="right")
    plt.yticks(rotation=0)
    save_fig("03_交互探测热力图.png")

    top_interactions = interaction_long.head(12).copy()
    top_interactions["组合"] = top_interactions["变量1"] + " × " + top_interactions["变量2"]
    plt.figure(figsize=(11, 7))
    ax = sns.barplot(data=top_interactions, x="q交互", y="组合", hue="交互类型", dodge=False, palette="Set2")
    for container in ax.containers:
        ax.bar_label(container, fmt="%.3f", padding=3, fontsize=9)
    ax.set_title("Top 12 交互解释力组合", fontsize=18, pad=14)
    ax.set_xlabel("q 交互值")
    ax.set_ylabel("")
    apply_clean_axis(ax)
    ax.legend(title="交互类型", loc="lower right")
    save_fig("04_Top交互组合.png")

    acc_plot = accuracy.sort_values("LOOCV_R2", ascending=True)
    plt.figure(figsize=(10, 6))
    plt.hlines(acc_plot["模型"], 0, acc_plot["训练R2"], color="#d7e3ef", linewidth=8, label="训练R2")
    plt.scatter(acc_plot["训练R2"], acc_plot["模型"], s=100, color="#377eb8", label="训练R2")
    plt.scatter(acc_plot["LOOCV_R2"], acc_plot["模型"], s=120, color="#e41a1c", label="LOOCV_R2")
    for _, row in acc_plot.iterrows():
        plt.text(row["LOOCV_R2"] + 0.015, row["模型"], f"{row['LOOCV_R2']:.3f}", va="center", fontsize=9)
    plt.axvline(0, color="black", linewidth=0.8)
    plt.title("模型精度对比：训练集 vs 留一交叉验证", fontsize=18, pad=14)
    plt.xlabel("R2")
    plt.ylabel("")
    plt.legend()
    apply_clean_axis(plt.gca())
    save_fig("05_模型精度对比.png")

    plt.figure(figsize=(7.5, 7))
    sns.regplot(data=best_pred_table, x=TARGET_COL, y="预测值", scatter_kws={"s": 70, "alpha": 0.85}, line_kws={"color": "#e41a1c"})
    min_val = min(best_pred_table[TARGET_COL].min(), best_pred_table["预测值"].min())
    max_val = max(best_pred_table[TARGET_COL].max(), best_pred_table["预测值"].max())
    plt.plot([min_val, max_val], [min_val, max_val], "--", color="gray", linewidth=1)
    best_model = best_pred_table["最优模型"].iloc[0]
    train_r2 = r2_score(best_pred_table[TARGET_COL], best_pred_table["预测值"])
    cv_r2 = r2_score(best_pred_table[TARGET_COL], best_pred_table["LOOCV预测值"])
    plt.title(f"{best_model} 拟合效果：训练R2={train_r2:.3f}，LOOCV_R2={cv_r2:.3f}", fontsize=15, pad=14)
    plt.xlabel("真实值")
    plt.ylabel("预测值")
    save_fig("06_最优模型真实值_vs_预测值.png")

    plt.figure(figsize=(9, 5.5))
    sns.histplot(best_pred_table["LOOCV残差"], kde=True, color="#4c78a8", bins=10)
    plt.axvline(0, color="#e41a1c", linestyle="--", linewidth=1.2)
    plt.title("最优模型 LOOCV 残差分布", fontsize=18, pad=14)
    plt.xlabel("LOOCV 残差")
    plt.ylabel("频数")
    save_fig("07_最优模型残差分布.png")

    if feature_importance is not None:
        plt.figure(figsize=(9, 6))
        ax = sns.barplot(data=feature_importance, x="重要性", y="变量", palette="mako")
        for container in ax.containers:
            ax.bar_label(container, fmt="%.3f", padding=3, fontsize=9)
        ax.set_title("最优预测模型变量重要性", fontsize=18, pad=14)
        ax.set_xlabel("重要性")
        ax.set_ylabel("")
        apply_clean_axis(ax)
        save_fig("08_最优模型变量重要性.png")

    mgwr_importance = pd.DataFrame(
        {
            "变量": FEATURE_NAMES,
            "重要性": [result_data[f"{col}_coef"].abs().mean() for col in FEATURE_COLS],
        }
    ).sort_values("重要性")
    plt.figure(figsize=(9, 6))
    plt.hlines(mgwr_importance["变量"], 0, mgwr_importance["重要性"], color="#c5d5e4", linewidth=3)
    plt.scatter(
        mgwr_importance["重要性"],
        mgwr_importance["变量"],
        s=170,
        c=mgwr_importance["重要性"],
        cmap="viridis",
        edgecolor="white",
        linewidth=1.4,
    )
    for _, row in mgwr_importance.iterrows():
        plt.text(row["重要性"] * 1.01, row["变量"], f"{row['重要性']:.3f}", va="center", fontsize=10)
    plt.title("MGWR 变量重要性：平均绝对局部系数", fontsize=18, pad=14)
    plt.xlabel("平均绝对局部系数")
    plt.ylabel("")
    apply_clean_axis(plt.gca())
    save_fig("09_MGWR变量重要性棒棒糖图.png")

    corr_df = result_data[FEATURE_COLS + [TARGET_COL]].rename(columns={**FEATURE_CN_MAP, TARGET_COL: TARGET_CN_NAME}).corr()
    plt.figure(figsize=(9, 8))
    sns.heatmap(corr_df, annot=True, fmt=".2f", cmap="vlag", center=0, square=True, linewidths=0.8, linecolor="white")
    plt.title("变量相关性热力图", fontsize=18, pad=14)
    plt.xticks(rotation=35, ha="right")
    plt.yticks(rotation=0)
    save_fig("10_变量相关性热力图.png")

    coef_cols = [f"{FEATURE_CN_MAP[col]}_局部系数" for col in FEATURE_COLS]
    coef_long = result_data[[CITY_FIELD] + coef_cols].melt(id_vars=CITY_FIELD, var_name="变量", value_name="局部系数")
    coef_long["变量"] = coef_long["变量"].str.replace("_局部系数", "", regex=False)
    plt.figure(figsize=(11, 6.5))
    sns.boxplot(data=coef_long, x="局部系数", y="变量", palette="coolwarm")
    plt.axvline(0, color="black", linestyle="--", linewidth=1)
    plt.title("MGWR 局部系数分布箱线图", fontsize=18, pad=14)
    plt.xlabel("局部系数")
    plt.ylabel("")
    save_fig("11_MGWR局部系数箱线图.png")

    city_coef = result_data.set_index(CITY_FIELD)[coef_cols]
    city_coef.columns = [col.replace("_局部系数", "") for col in city_coef.columns]
    plt.figure(figsize=(9, max(8, len(city_coef) * 0.22)))
    sns.heatmap(city_coef, cmap="RdBu_r", center=0, linewidths=0.25, linecolor="white", cbar_kws={"label": "局部系数"})
    plt.title("城市-变量 MGWR 局部系数热力图", fontsize=18, pad=14)
    plt.xticks(rotation=35, ha="right")
    plt.yticks(fontsize=8)
    save_fig("12_城市变量局部系数热力图.png")


def make_spatial_charts(result_data, gdf, spatial_data, w, moran):
    print("\n绘制地图与空间诊断图表...")

    map_cols = [CITY_FIELD, "MGWR_pred", "MGWR_resid", "MGWR_abs_resid"]
    map_cols += [col for col in ["Local_R2"] if col in result_data.columns]
    map_cols += [f"{col}_coef" for col in FEATURE_COLS]
    map_cols += [f"{FEATURE_CN_MAP[col]}_局部系数" for col in FEATURE_COLS]
    map_cols += [f"{FEATURE_CN_MAP[col]}_显著" for col in FEATURE_COLS if f"{FEATURE_CN_MAP[col]}_显著" in result_data.columns]
    plot_gdf = gdf.merge(result_data[[col for col in map_cols if col in result_data.columns]], on=CITY_FIELD)

    fig, ax = plt.subplots(figsize=(8, 8))
    plot_gdf.plot(
        column="MGWR_resid",
        cmap="RdBu_r",
        norm=diverging_norm(plot_gdf["MGWR_resid"]),
        edgecolor="white",
        linewidth=0.45,
        legend=True,
        ax=ax,
    )
    ax.set_title("MGWR 残差空间分布", fontdict=TITLE_FONT, pad=12)
    ax.axis("off")
    save_fig("13_MGWR残差空间分布图.png")

    if "Local_R2" in plot_gdf.columns:
        fig, ax = plt.subplots(figsize=(8, 8))
        plot_gdf.plot(
            column="Local_R2",
            cmap="viridis",
            edgecolor="white",
            linewidth=0.45,
            legend=True,
            ax=ax,
        )
        ax.set_title("MGWR Local R2 空间分布", fontdict=TITLE_FONT, pad=12)
        ax.axis("off")
        save_fig("14_MGWR_Local_R2空间分布图.png")

    for idx, col in enumerate(FEATURE_COLS, start=15):
        coef_col = f"{col}_coef"
        fig, ax = plt.subplots(figsize=(8, 8))
        plot_gdf.plot(
            column=coef_col,
            cmap="RdBu_r",
            norm=diverging_norm(plot_gdf[coef_col]),
            edgecolor="white",
            linewidth=0.45,
            legend=True,
            ax=ax,
        )
        ax.set_title(f"{FEATURE_CN_MAP[col]} MGWR 局部系数", fontdict=TITLE_FONT, pad=12)
        ax.axis("off")
        save_fig(f"{idx:02d}_MGWR_{FEATURE_CN_MAP[col]}_局部系数图.png")

        sig_col = f"{FEATURE_CN_MAP[col]}_显著"
        if sig_col in plot_gdf.columns:
            fig, ax = plt.subplots(figsize=(8, 8))
            plot_gdf.assign(_sig=plot_gdf[sig_col].map({True: "显著", False: "不显著"})).plot(
                column="_sig",
                categorical=True,
                cmap=ListedColormap(["#bdbdbd", "#2166ac"]),
                edgecolor="white",
                linewidth=0.45,
                legend=True,
                ax=ax,
            )
            ax.set_title(f"{FEATURE_CN_MAP[col]} 局部系数显著性", fontdict=TITLE_FONT, pad=12)
            ax.axis("off")
            save_fig(f"{idx + 20:02d}_MGWR_{FEATURE_CN_MAP[col]}_显著性图.png")

    lisa_order = ["HH 热点", "LH 异常低值", "LL 冷点", "HL 异常高值", "不显著"]
    lisa_colors = {
        "HH 热点": "#d7191c",
        "LH 异常低值": "#fdae61",
        "LL 冷点": "#2c7bb6",
        "HL 异常高值": "#abd9e9",
        "不显著": "#d9d9d9",
    }
    fig, ax = plt.subplots(figsize=(8, 8))
    for label in lisa_order:
        subset = spatial_data[spatial_data["LISA类型"] == label]
        if not subset.empty:
            subset.plot(color=lisa_colors[label], edgecolor="white", linewidth=0.45, ax=ax)
    ax.legend(
        handles=[Patch(facecolor=lisa_colors[label], edgecolor="white", label=label) for label in lisa_order],
        loc="lower left",
        frameon=False,
    )
    ax.set_title("LISA 局部空间聚类图", fontdict=TITLE_FONT, pad=12)
    ax.axis("off")
    save_fig("35_LISA局部空间聚类图.png")

    y = spatial_data[TARGET_COL].to_numpy()
    y_std = (y - y.mean()) / y.std(ddof=1)
    lag_y = lag_spatial(w, y)
    lag_y_std = (lag_y - lag_y.mean()) / lag_y.std(ddof=1)
    fig, ax = plt.subplots(figsize=(7.5, 7))
    ax.scatter(y_std, lag_y_std, s=70, color="#2f6f9f", edgecolor="white", linewidth=0.8, alpha=0.9)
    sns.regplot(x=y_std, y=lag_y_std, scatter=False, ax=ax, line_kws={"color": "#d7191c", "linewidth": 1.6})
    ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
    ax.axvline(0, color="black", linewidth=0.8, linestyle="--")
    ax.set_title(f"Moran 散点图：I={moran.I:.3f}, p={moran.p_sim:.3f}", fontsize=16, pad=12)
    ax.set_xlabel(f"{TARGET_CN_NAME} 标准化值")
    ax.set_ylabel("空间滞后标准化值")
    apply_clean_axis(ax)
    save_fig("36_Moran散点图.png")

    panel_items = [(f"{col}_coef", FEATURE_CN_MAP[col]) for col in FEATURE_COLS]
    if "Local_R2" in plot_gdf.columns:
        panel_items.append(("Local_R2", "Local R2"))
    rows, cols = 2, 4
    fig, axes = plt.subplots(rows, cols, figsize=(20, 10))
    axes = axes.flatten()
    for ax, (column, title) in zip(axes, panel_items[: rows * cols]):
        cmap = "viridis" if column == "Local_R2" else "RdBu_r"
        plot_gdf.plot(
            column=column,
            cmap=cmap,
            norm=None if column == "Local_R2" else diverging_norm(plot_gdf[column]),
            edgecolor="white",
            linewidth=0.25,
            legend=False,
            ax=ax,
        )
        ax.set_title(title, fontdict=TITLE_FONT, pad=8)
        ax.axis("off")
    for ax in axes[len(panel_items):]:
        ax.axis("off")
    save_fig("37_MGWR综合图墙.png")


def export_tables(result_data, mgwr_metrics, bw_table, coef_summary, q_df, interaction_matrix, interaction_long, moran_df, spatial_data, accuracy, best_pred_table, feature_importance):
    print("\n导出 Excel 数据表...")
    out_xlsx = os.path.join(OUT_DIR, "MGWR_地理探测器_精度结果表.xlsx")

    with pd.ExcelWriter(out_xlsx, engine="openpyxl") as writer:
        result_data.to_excel(writer, sheet_name="城市预测残差与局部系数", index=False)
        mgwr_metrics.to_excel(writer, sheet_name="MGWR精度", index=False)
        bw_table.to_excel(writer, sheet_name="MGWR带宽", index=False)
        coef_summary.to_excel(writer, sheet_name="MGWR局部系数汇总", index=False)
        q_df.to_excel(writer, sheet_name="地理探测器q值", index=False)
        interaction_matrix.to_excel(writer, sheet_name="交互探测矩阵")
        interaction_long.to_excel(writer, sheet_name="交互探测排序", index=False)
        moran_df.to_excel(writer, sheet_name="Moran空间自相关", index=False)
        spatial_data.drop(columns="geometry", errors="ignore").to_excel(writer, sheet_name="LISA空间聚类", index=False)
        accuracy.to_excel(writer, sheet_name="模型精度对比", index=False)
        best_pred_table.to_excel(writer, sheet_name="最优模型预测表", index=False)
        if feature_importance is not None:
            feature_importance.to_excel(writer, sheet_name="最优模型变量重要性", index=False)

    q_df.to_csv(os.path.join(OUT_DIR, "地理探测器q值.csv"), index=False, encoding="utf-8-sig")
    interaction_matrix.to_csv(os.path.join(OUT_DIR, "交互探测矩阵.csv"), encoding="utf-8-sig")
    interaction_long.to_csv(os.path.join(OUT_DIR, "交互探测排序.csv"), index=False, encoding="utf-8-sig")
    spatial_data.drop(columns="geometry", errors="ignore").to_csv(os.path.join(OUT_DIR, "LISA空间聚类.csv"), index=False, encoding="utf-8-sig")
    accuracy.to_csv(os.path.join(OUT_DIR, "模型精度对比.csv"), index=False, encoding="utf-8-sig")
    result_data.to_csv(os.path.join(OUT_DIR, "城市预测残差与局部系数.csv"), index=False, encoding="utf-8-sig")

    return out_xlsx


def main():
    print("\n读取数据...")
    data = load_data(EXCEL_PATH)
    gdf = load_shp(SHP_PATH)
    data = fill_city_name_by_coords(data, gdf)
    print(data.head())

    result_data, mgwr_metrics, bw_table, coef_summary = run_mgwr(data)
    q_df, interaction_matrix, interaction_long = run_geodetector(data)
    moran_df, spatial_data, w, moran = compute_spatial_diagnostics(data, gdf)
    accuracy, best_pred_table, feature_importance = compare_prediction_models(data)

    make_charts(result_data, q_df, interaction_matrix, interaction_long, accuracy, best_pred_table, feature_importance)
    make_spatial_charts(result_data, gdf, spatial_data, w, moran)
    out_xlsx = export_tables(
        result_data,
        mgwr_metrics,
        bw_table,
        coef_summary,
        q_df,
        interaction_matrix,
        interaction_long,
        moran_df,
        spatial_data,
        accuracy,
        best_pred_table,
        feature_importance,
    )

    best_row = accuracy.iloc[0]
    mgwr_row = mgwr_metrics.iloc[0]

    print("\n===================================")
    print("分析完成：已输出表格、非地图统计图、MGWR空间图、LISA聚类图与Moran散点图。")
    print(f"MGWR 精度：R2={mgwr_row['训练R2']:.4f}，调整R2={mgwr_row['调整R2']:.4f}，RMSE={mgwr_row['RMSE']:.4f}，MAE={mgwr_row['MAE']:.4f}")
    print(f"当前最优预测模型：{best_row['模型']}，训练R2={best_row['训练R2']:.4f}，LOOCV_R2={best_row['LOOCV_R2']:.4f}，LOOCV_RMSE={best_row['LOOCV_RMSE']:.4f}")
    print(f"结果表：{out_xlsx}")
    print(f"输出目录：{OUT_DIR}")
    print("===================================")


if __name__ == "__main__":
    main()
