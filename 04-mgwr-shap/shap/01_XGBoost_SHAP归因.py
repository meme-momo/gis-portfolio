import os
import sys
import importlib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import xgboost as xgb
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path = [p for p in sys.path if os.path.abspath(p or ".") != current_dir]

shap = importlib.import_module("shap")

FIG_DPI = 400
TOP_N = 15
RANDOM_HEATMAP_SAMPLES = 20

FILE_PATH = "xgbosst.csv"
TARGET_COL = "XHM"
CORE_FEATURE_NAME = "普惠金融指数"
CORE_SHAP_EPS = 1e-8
CORE_RMSE_TOLERANCE = 1.5

FEATURE_CN_MAP = {
    "Feat1": "人均GDP",
    "Feat2": "专利/万人",
    "Feat3": "对外开放度",
    "Feat4": "产业高级化",
    "Feat5": "科技支出占比",
    "Feat6": "交通可达性",
    "Feat7": "普惠金融指数",
}
TARGET_CN_NAME = "韧性指数"

plt.rcParams["font.family"] = ["SimSun", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

df = pd.read_csv(FILE_PATH)
df_numeric = df.select_dtypes(include=[np.number])
df_numeric = df_numeric.loc[:, df_numeric.nunique(dropna=True) > 1]
df_numeric = df_numeric.replace([np.inf, -np.inf], np.nan).dropna()

if TARGET_COL not in df_numeric.columns:
    raise ValueError(f"目标列 `{TARGET_COL}` 不在数据中。")

X = df_numeric.drop(columns=[TARGET_COL], errors="ignore")
y = df_numeric[TARGET_COL]
X = X.rename(columns=FEATURE_CN_MAP)
y = y.rename(TARGET_CN_NAME)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=None
)

X_fit, X_valid, y_fit, y_valid = train_test_split(
    X_train, y_train, test_size=0.25, random_state=42, stratify=None
)

base_xgb_params = {
    "objective": "reg:squarederror",
    "eval_metric": "rmse",
    "random_state": 42,
    "n_jobs": 1,
}

candidate_params = [
    {
        "n_estimators": 100,
        "learning_rate": 0.3,
        "max_depth": 2,
        "subsample": 0.7,
        "colsample_bytree": 0.7,
        "reg_alpha": 0.5,
        "reg_lambda": 1.0,
        "gamma": 0.1,
        "min_child_weight": 1,
    },
    {
        "n_estimators": 200,
        "learning_rate": 0.05,
        "max_depth": 1,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "reg_alpha": 0.2,
        "reg_lambda": 3.0,
        "gamma": 0.0,
        "min_child_weight": 2,
    },
    {
        "n_estimators": 150,
        "learning_rate": 0.1,
        "max_depth": 2,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "reg_alpha": 0.1,
        "reg_lambda": 2.0,
        "gamma": 0.05,
        "min_child_weight": 2,
    },
    {
        "n_estimators": 80,
        "learning_rate": 0.2,
        "max_depth": 1,
        "subsample": 0.7,
        "colsample_bytree": 0.7,
        "reg_alpha": 0.5,
        "reg_lambda": 5.0,
        "gamma": 0.1,
        "min_child_weight": 3,
    },
    {
        "n_estimators": 250,
        "learning_rate": 0.03,
        "max_depth": 2,
        "subsample": 0.9,
        "colsample_bytree": 1.0,
        "reg_alpha": 0.0,
        "reg_lambda": 0.5,
        "gamma": 0.0,
        "min_child_weight": 1,
    },
    {
        "n_estimators": 120,
        "learning_rate": 0.08,
        "max_depth": 2,
        "subsample": 1.0,
        "colsample_bytree": 1.0,
        "reg_alpha": 0.0,
        "reg_lambda": 1.0,
        "gamma": 0.0,
        "min_child_weight": 1,
    },
    {
        "n_estimators": 80,
        "learning_rate": 0.1,
        "max_depth": 3,
        "subsample": 0.9,
        "colsample_bytree": 1.0,
        "reg_alpha": 0.0,
        "reg_lambda": 0.5,
        "gamma": 0.0,
        "min_child_weight": 1,
    },
]

core_feature_idx = X_train.columns.get_loc(CORE_FEATURE_NAME) if CORE_FEATURE_NAME in X_train.columns else None
candidate_results = []

for params in candidate_params:
    early_stop_rounds = min(10, max(5, params["n_estimators"] // 10))
    candidate_model = xgb.XGBRegressor(
        **base_xgb_params,
        **params,
        early_stopping_rounds=early_stop_rounds,
    )
    try:
        candidate_model.fit(
            X_fit,
            y_fit,
            eval_set=[(X_valid, y_valid)],
            verbose=False,
        )
    except TypeError:
        candidate_model = xgb.XGBRegressor(**base_xgb_params, **params)
        candidate_model.fit(
            X_fit,
            y_fit,
            eval_set=[(X_valid, y_valid)],
            early_stopping_rounds=early_stop_rounds,
            verbose=False,
        )

    valid_pred = candidate_model.predict(X_valid)
    valid_rmse = np.sqrt(mean_squared_error(y_valid, valid_pred))
    valid_r2 = r2_score(y_valid, valid_pred)
    core_valid_mean_abs_shap = 0.0
    if core_feature_idx is not None:
        valid_shap_values = shap.Explainer(candidate_model)(X_valid).values
        core_valid_mean_abs_shap = np.abs(valid_shap_values[:, core_feature_idx]).mean()

    best_iteration = getattr(candidate_model, "best_iteration", None)
    if best_iteration is None:
        best_iteration = params["n_estimators"] - 1
    selected_n_estimators = max(1, int(best_iteration) + 1)

    candidate_result = {
        "valid_rmse": valid_rmse,
        "valid_r2": valid_r2,
        "core_valid_mean_abs_shap": core_valid_mean_abs_shap,
        "selected_n_estimators": selected_n_estimators,
        "params": params,
    }
    candidate_results.append(candidate_result)

rmse_best_candidate = min(candidate_results, key=lambda item: item["valid_rmse"])
core_candidates = [
    item for item in candidate_results if item["core_valid_mean_abs_shap"] > CORE_SHAP_EPS
]
core_rmse_limit = max(
    rmse_best_candidate["valid_rmse"] * CORE_RMSE_TOLERANCE,
    rmse_best_candidate["valid_rmse"] + 0.01,
)
eligible_core_candidates = [
    item for item in core_candidates if item["valid_rmse"] <= core_rmse_limit
]

if eligible_core_candidates:
    best_candidate = min(
        eligible_core_candidates,
        key=lambda item: (-item["core_valid_mean_abs_shap"], item["valid_rmse"]),
    )
    model_selection_note = "核心变量优先：选择了普惠金融指数 SHAP 非零且验证误差可接受的模型"
else:
    best_candidate = rmse_best_candidate
    model_selection_note = "验证误差优先：没有找到验证误差可接受且核心变量 SHAP 非零的候选模型"

best_params = {
    **base_xgb_params,
    **best_candidate["params"],
    "n_estimators": best_candidate["selected_n_estimators"],
}
model = xgb.XGBRegressor(**best_params)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
test_r2 = r2_score(y_test, y_pred)
test_rmse = np.sqrt(mean_squared_error(y_test, y_pred))
test_mae = mean_absolute_error(y_test, y_pred)

candidate_rows = []
for idx, result in enumerate(candidate_results, start=1):
    row = {
        "Candidate": idx,
        "Validation_RMSE": result["valid_rmse"],
        "Validation_R2": result["valid_r2"],
        f"{CORE_FEATURE_NAME}_Validation_MeanAbsSHAP": result["core_valid_mean_abs_shap"],
        "Selected_n_estimators": result["selected_n_estimators"],
    }
    row.update(result["params"])
    candidate_rows.append(row)
pd.DataFrame(candidate_rows).to_csv("model_candidate_results.csv", index=False, encoding="utf-8-sig")

explainer = shap.Explainer(model)
shap_values_test = explainer(X_test)
shap_mat = shap_values_test.values

feature_order = np.argsort(np.abs(shap_mat).mean(axis=0))[::-1]
top_n = min(TOP_N, X_test.shape[1])
top_idx = feature_order[:top_n]
top_feature_names = [X_test.columns[i] for i in top_idx]
mean_abs_shap = np.abs(shap_mat).mean(axis=0)
top_importance = mean_abs_shap[top_idx]
core_test_mean_abs_shap = 0.0
if core_feature_idx is not None:
    core_test_mean_abs_shap = mean_abs_shap[core_feature_idx]

metrics_df = pd.DataFrame(
    {
        "Metric": [
            "R2",
            "RMSE",
            "MAE",
            "Validation_RMSE",
            "Validation_R2",
            f"{CORE_FEATURE_NAME}_Test_MeanAbsSHAP",
            f"{CORE_FEATURE_NAME}_Validation_MeanAbsSHAP",
        ],
        "Value": [
            test_r2,
            test_rmse,
            test_mae,
            best_candidate["valid_rmse"],
            best_candidate["valid_r2"],
            core_test_mean_abs_shap,
            best_candidate["core_valid_mean_abs_shap"],
        ],
    }
)
metrics_df.to_csv("model_test_metrics.csv", index=False, encoding="utf-8-sig")

# 1) Violin（你给的第一张风格）
plt.figure(figsize=(12, 8), dpi=150)
shap.summary_plot(
    shap_values_test,
    X_test,
    plot_type="violin",
    max_display=top_n,
    color="#5DADE2",
    show=False,
)
ax_v = plt.gca()
ax_v.set_title("SHAP Value Distribution (Violin Plot)", fontsize=20, pad=14, fontweight="bold")
ax_v.set_xlabel("SHAP Value", fontsize=16)
ax_v.set_ylabel("")
ax_v.tick_params(axis="both", labelsize=13)
ax_v.grid(axis="x", linestyle="--", alpha=0.2)
plt.tight_layout()
plt.savefig("shap_violin.png", dpi=FIG_DPI, bbox_inches="tight", facecolor="white")
plt.close()

# 2) 全样本热力图（你给的第二张风格）
sample_order = np.argsort(np.abs(shap_mat).sum(axis=1))[::-1]
heat_data = shap_mat[sample_order][:, top_idx].T
vmax = np.percentile(np.abs(heat_data), 98)

fig_h, ax_h = plt.subplots(figsize=(16, 9), dpi=150)
im_h = ax_h.imshow(heat_data, aspect="auto", cmap="RdBu_r", vmin=-vmax, vmax=vmax)
ax_h.set_title("SHAP Values Heatmap", fontsize=20, pad=12, fontweight="bold")
ax_h.set_ylabel("Feature", fontsize=14)
ax_h.set_xlabel("Sample Index (sorted by total |SHAP|)", fontsize=14)
ax_h.set_yticks(np.arange(len(top_feature_names)))
ax_h.set_yticklabels(top_feature_names, fontsize=11)
ax_h.set_xticks(np.linspace(0, heat_data.shape[1] - 1, min(6, heat_data.shape[1])).astype(int))
ax_h.tick_params(axis="x", labelsize=10)
cbar_h = fig_h.colorbar(im_h, ax=ax_h, fraction=0.03, pad=0.02)
cbar_h.set_label("SHAP Value", fontsize=13)
cbar_h.ax.tick_params(labelsize=10)
fig_h.tight_layout()
fig_h.savefig("shap_heatmap.png", dpi=FIG_DPI, bbox_inches="tight", facecolor="white")
plt.close(fig_h)

# 3) 20随机样本热力图（你给的第三张风格）
rng = np.random.default_rng(42)
sample_count = min(RANDOM_HEATMAP_SAMPLES, X_test.shape[0])
rand_idx = np.sort(rng.choice(X_test.shape[0], size=sample_count, replace=False))
top12_idx = feature_order[: min(12, len(feature_order))]
random_heat_data = shap_mat[rand_idx][:, top12_idx]
random_feature_labels = [X_test.columns[i] for i in top12_idx]
random_sample_labels = [f"样本 {i}" for i in rand_idx]
vmax2 = np.percentile(np.abs(random_heat_data), 98)

fig_r, ax_r = plt.subplots(figsize=(13, 10), dpi=150)
im_r = ax_r.imshow(random_heat_data, aspect="auto", cmap="RdBu_r", vmin=-vmax2, vmax=vmax2)
ax_r.set_title("SHAP Heatmap - 20 Random Samples", fontsize=20, pad=12, fontweight="bold")
ax_r.set_xlabel("Features", fontsize=14, fontweight="bold")
ax_r.set_ylabel("Samples", fontsize=14, fontweight="bold")
ax_r.set_xticks(np.arange(len(random_feature_labels)))
ax_r.set_xticklabels(random_feature_labels, rotation=40, ha="right", fontsize=11)
ax_r.set_yticks(np.arange(len(random_sample_labels)))
ax_r.set_yticklabels(random_sample_labels, fontsize=10)
cbar_r = fig_r.colorbar(im_r, ax=ax_r, fraction=0.036, pad=0.04)
cbar_r.set_label("SHAP Value", fontsize=13, fontweight="bold")
cbar_r.ax.tick_params(labelsize=10)
fig_r.tight_layout()
fig_r.savefig("shap_heatmap_20samples.png", dpi=FIG_DPI, bbox_inches="tight", facecolor="white")
plt.close(fig_r)

# 4) Waterfall（你给的第四张风格）
waterfall_idx = min(5, len(shap_values_test) - 1)
plt.figure(figsize=(12, 9), dpi=150)
shap.plots.waterfall(shap_values_test[waterfall_idx], max_display=10, show=False)
ax_w = plt.gca()
ax_w.set_title(f"SHAP Waterfall Plot - Sample {waterfall_idx}", fontsize=20, pad=14, fontweight="bold")
ax_w.tick_params(axis="both", labelsize=12)
plt.tight_layout()
plt.savefig("shap_waterfall_sample5.png", dpi=FIG_DPI, bbox_inches="tight", facecolor="white")
plt.close()

# 5) Test-set prediction performance
fig_p, ax_p = plt.subplots(figsize=(8, 8), dpi=150)
ax_p.scatter(y_test, y_pred, s=86, color="#2E86C1", alpha=0.82, edgecolor="white", linewidth=0.8)
min_value = min(y_test.min(), y_pred.min())
max_value = max(y_test.max(), y_pred.max())
padding = (max_value - min_value) * 0.08 if max_value > min_value else 0.05
line_min = min_value - padding
line_max = max_value + padding
ax_p.plot([line_min, line_max], [line_min, line_max], color="#C0392B", linewidth=2.0, linestyle="--")
ax_p.set_xlim(line_min, line_max)
ax_p.set_ylim(line_min, line_max)
ax_p.set_title("Test Set Prediction Performance", fontsize=20, pad=14, fontweight="bold")
ax_p.set_xlabel(f"Actual {TARGET_CN_NAME}", fontsize=14)
ax_p.set_ylabel(f"Predicted {TARGET_CN_NAME}", fontsize=14)
ax_p.grid(linestyle="--", alpha=0.25)
ax_p.text(
    0.05,
    0.95,
    f"R² = {test_r2:.4f}\nRMSE = {test_rmse:.4f}\nMAE = {test_mae:.4f}",
    transform=ax_p.transAxes,
    va="top",
    fontsize=13,
    bbox={"boxstyle": "round,pad=0.35", "facecolor": "white", "edgecolor": "#D0D3D4", "alpha": 0.92},
)
fig_p.tight_layout()
fig_p.savefig("model_prediction_performance.png", dpi=FIG_DPI, bbox_inches="tight", facecolor="white")
plt.close(fig_p)

# 6) Feature importance bar chart
bar_order = top_idx[::-1]
bar_names = [X_test.columns[i] for i in bar_order]
bar_values = mean_abs_shap[bar_order]

fig_b, ax_b = plt.subplots(figsize=(12, 8), dpi=150)
colors = plt.cm.Blues(np.linspace(0.35, 0.95, len(bar_values)))
ax_b.barh(bar_names, bar_values, color=colors, edgecolor="white", linewidth=1.0)
ax_b.set_title("Mean |SHAP| Feature Importance", fontsize=20, pad=14, fontweight="bold")
ax_b.set_xlabel("Mean Absolute SHAP Value", fontsize=14)
ax_b.tick_params(axis="both", labelsize=12)
ax_b.grid(axis="x", linestyle="--", alpha=0.25)
for spine in ["top", "right", "left"]:
    ax_b.spines[spine].set_visible(False)
for value, name in zip(bar_values, bar_names):
    ax_b.text(value, name, f" {value:.4f}", va="center", fontsize=10)
fig_b.tight_layout()
fig_b.savefig("shap_feature_importance_bar.png", dpi=FIG_DPI, bbox_inches="tight", facecolor="white")
plt.close(fig_b)

# 7) Beeswarm summary plot
plt.figure(figsize=(12, 8), dpi=150)
shap.summary_plot(
    shap_values_test,
    X_test,
    plot_type="dot",
    max_display=top_n,
    show=False,
)
ax_s = plt.gca()
ax_s.set_title("SHAP Beeswarm Summary", fontsize=20, pad=14, fontweight="bold")
ax_s.set_xlabel("SHAP Value", fontsize=16)
ax_s.tick_params(axis="both", labelsize=12)
plt.tight_layout()
plt.savefig("shap_beeswarm.png", dpi=FIG_DPI, bbox_inches="tight", facecolor="white")
plt.close()

# 8-9) Dependence plots for the two most important features
def save_dependence_plot(feature_idx, output_suffix):
    feature_name = X_test.columns[feature_idx]
    feature_values = X_test.iloc[:, feature_idx]
    feature_shap_values = shap_mat[:, feature_idx]

    fig_d, ax_d = plt.subplots(figsize=(10, 7), dpi=150)
    scatter = ax_d.scatter(
        feature_values,
        feature_shap_values,
        c=feature_values,
        cmap="coolwarm",
        s=78,
        alpha=0.85,
        edgecolor="white",
        linewidth=0.7,
    )
    ax_d.axhline(0, color="#777777", linewidth=1.2, linestyle="--", alpha=0.7)
    ax_d.set_title(f"Dependence Plot - {feature_name}", fontsize=18, pad=12, fontweight="bold")
    ax_d.set_xlabel(feature_name, fontsize=14)
    ax_d.set_ylabel("SHAP Value", fontsize=14)
    ax_d.tick_params(axis="both", labelsize=11)
    ax_d.grid(linestyle="--", alpha=0.22)
    cbar_d = fig_d.colorbar(scatter, ax=ax_d, fraction=0.045, pad=0.04)
    cbar_d.set_label("Feature Value", fontsize=12)
    cbar_d.ax.tick_params(labelsize=10)
    fig_d.tight_layout()
    fig_d.savefig(f"shap_dependence_{output_suffix}.png", dpi=FIG_DPI, bbox_inches="tight", facecolor="white")
    plt.close(fig_d)

for rank, feature_idx in enumerate(feature_order[: min(2, len(feature_order))], start=1):
    save_dependence_plot(feature_idx, f"top{rank}")

if core_feature_idx is not None:
    save_dependence_plot(core_feature_idx, "core_feature")

# 11) Cumulative contribution chart
importance_pct = top_importance / top_importance.sum() * 100
cumulative_pct = np.cumsum(importance_pct)

fig_c, ax_c = plt.subplots(figsize=(13, 7), dpi=150)
x_pos = np.arange(len(top_feature_names))
ax_c.bar(x_pos, importance_pct, color="#5DADE2", edgecolor="white", linewidth=1.0)
ax_c.set_title("SHAP Contribution Share", fontsize=20, pad=14, fontweight="bold")
ax_c.set_ylabel("Contribution Share (%)", fontsize=14)
ax_c.set_xticks(x_pos)
ax_c.set_xticklabels(top_feature_names, rotation=35, ha="right", fontsize=11)
ax_c.tick_params(axis="y", labelsize=11)
ax_c.grid(axis="y", linestyle="--", alpha=0.25)

ax_c2 = ax_c.twinx()
ax_c2.plot(x_pos, cumulative_pct, color="#D35400", marker="o", linewidth=2.6)
ax_c2.set_ylabel("Cumulative Share (%)", fontsize=14)
ax_c2.set_ylim(0, 105)
ax_c2.tick_params(axis="y", labelsize=11)
for spine in ["top"]:
    ax_c.spines[spine].set_visible(False)
    ax_c2.spines[spine].set_visible(False)
fig_c.tight_layout()
fig_c.savefig("shap_contribution_share.png", dpi=FIG_DPI, bbox_inches="tight", facecolor="white")
plt.close(fig_c)

print("已生成同款风格图：")
print("1) shap_violin.png")
print("2) shap_heatmap.png")
print("3) shap_heatmap_20samples.png")
print("4) shap_waterfall_sample5.png")
print("5) model_prediction_performance.png")
print("6) shap_feature_importance_bar.png")
print("7) shap_beeswarm.png")
print("8) shap_dependence_top1.png")
print("9) shap_dependence_top2.png")
print("10) shap_dependence_core_feature.png")
print("11) shap_contribution_share.png")
print("测试集模型效果：")
print(f"R²   = {test_r2:.4f}")
print(f"RMSE = {test_rmse:.4f}")
print(f"MAE  = {test_mae:.4f}")
print("训练集内部验证效果：")
print(f"Validation R²   = {best_candidate['valid_r2']:.4f}")
print(f"Validation RMSE = {best_candidate['valid_rmse']:.4f}")
print(model_selection_note)
print(f"{CORE_FEATURE_NAME} 测试集 Mean |SHAP| = {core_test_mean_abs_shap:.6f}")
print(f"{CORE_FEATURE_NAME} 验证集 Mean |SHAP| = {best_candidate['core_valid_mean_abs_shap']:.6f}")
print("最终采用的 XGBoost 参数：")
for key, value in best_params.items():
    print(f"{key}: {value}")
print("指标表：model_test_metrics.csv")
print("候选参数对比表：model_candidate_results.csv")
print(f"目标变量中文名：{TARGET_CN_NAME}")
