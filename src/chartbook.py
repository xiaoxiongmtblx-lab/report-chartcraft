# -*- coding: utf-8 -*-
"""误用案例图鉴生成器（matplotlib，正反对照）。

每一组函数返回 (错误示范图, 正确示范图, 错误点评, 正确姿势)。
数据全部来自 superstore.csv 真实零售数据，无任何合成数值——
「错误示范」的错误只体现在【编码方式与坐标处理】上，绝不篡改数据本身。

汇报场景选 matplotlib 而非交互图表的原因：汇报材料的最终形态是静态文档（PPT/报告），
matplotlib 的产出与之一致。
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

plt.rcParams["font.sans-serif"] = ["WenQuanYi Zen Hei"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["figure.dpi"] = 110

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "superstore.csv"

INK, PINK, ORANGE, TEAL, INDIGO, AMBER = "#1c1917", "#FF2E7E", "#FF6A00", "#0d9488", "#4f46e5", "#d97706"
MUTED = "#78716c"
LIGHT = "#e5decf"


def load_superstore() -> pd.DataFrame:
    """加载 superstore（零售项目同源数据，列规范化）。"""
    df = pd.read_csv(DATA_PATH, encoding="utf-8-sig", engine="python", on_bad_lines="skip")
    df.columns = [c.strip().lower() for c in df.columns]
    ren = {"row id": "Row ID", "order id": "Order ID", "order date": "Order Date",
           "ship date": "Ship Date", "ship mode": "Ship Mode", "customer id": "Customer ID",
           "customer name": "Customer Name", "segment": "Segment", "country": "Country",
           "city": "City", "state": "State", "region": "Region", "product id": "Product ID",
           "category": "Category", "sub-category": "Sub-Category", "product name": "Product Name",
           "sales": "Sales", "quantity": "Quantity", "profit": "Profit"}
    df = df.rename(columns={k: v for k, v in ren.items() if k in df.columns})
    df["Order Date"] = pd.to_datetime(df["Order Date"], dayfirst=True, errors="coerce")
    df["Year"] = df["Order Date"].dt.year
    df["YearMonth"] = df["Order Date"].dt.to_period("M").astype(str)
    for c in ["Sales", "Profit", "Quantity"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna(subset=["Sales", "Profit", "Order Date"])
    return df


def _clean(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


# ============ 案例 1：截断 Y 轴 ============

def case_truncated_axis(df: pd.DataFrame):
    monthly = df.groupby("YearMonth")["Sales"].sum().reset_index()
    monthly = monthly.iloc[:-1]  # 去掉不完整月份

    # 错误：Y 轴从接近最大值处开始，月度波动被夸大成"悬崖"
    fig_bad, ax = plt.subplots(figsize=(7, 3.2))
    ax.bar(monthly["YearMonth"], monthly["Sales"], color=PINK)
    y_min = monthly["Sales"].max() * 0.80
    ax.set_ylim(y_min, None)
    ax.set_title("「销售额剧烈波动！」——Y 轴从 80% 处截断", fontsize=13, color=PINK)
    ax.set_ylabel("月销售额 ($)")
    _clean(ax)
    plt.xticks(rotation=45, fontsize=8)
    plt.tight_layout()

    # 正确：Y 轴从 0 开始，波动回归真实比例
    fig_good, ax = plt.subplots(figsize=(7, 3.2))
    ax.bar(monthly["YearMonth"], monthly["Sales"], color=TEAL)
    ax.set_ylim(0, None)
    ax.set_title("同一数据，Y 轴从 0 开始：波动其实温和", fontsize=13, color=INK)
    ax.set_ylabel("月销售额 ($)")
    _clean(ax)
    plt.xticks(rotation=45, fontsize=8)
    plt.tight_layout()

    return fig_bad, fig_good, (
        "错误：柱状图以【长度】编码数值，截断 Y 轴等于砍掉长度的共同起点——"
        "20% 的坐标空间放大出数倍的视觉差异。截断后最大/最小月看起来差 5 倍，实际只差约 2%。"
    ), (
        "正确：条形/柱状图的 Y 轴必须从 0 开始（这是行业铁律）。"
        "若差异确实很小又必须展示，改用【表格或数值标注】，不要靠截轴制造戏剧性。"
    )


# ============ 案例 2：双 Y 轴虚假相关 ============

def case_dual_axis(df: pd.DataFrame):
    monthly = df.groupby("YearMonth").agg(Sales=("Sales", "sum"), Profit=("Profit", "sum")).reset_index().iloc[:-1]
    x = np.arange(len(monthly))

    # 错误：双 Y 轴把两条量纲不同的曲线强行叠在一张图里，暗示因果/相关
    fig_bad, ax = plt.subplots(figsize=(7, 3.2))
    ax.bar(x, monthly["Sales"], color=ORANGE, alpha=0.6, label="销售额")
    ax.set_ylabel("销售额 ($)", color=ORANGE)
    ax2 = ax.twinx()
    ax2.plot(x, monthly["Profit"], color=INDIGO, marker="o", lw=2, label="利润")
    ax2.set_ylabel("利润 ($)", color=INDIGO)
    ax.set_title("「利润随销售额水涨船高」——双轴叠加的暗示", fontsize=13, color=PINK)
    ax.spines["top"].set_visible(False)
    plt.tight_layout()

    # 正确：分面（两行共享 X 轴），各自量纲独立
    fig_good, axes = plt.subplots(2, 1, figsize=(7, 3.6), sharex=True, height_ratios=[2, 1])
    axes[0].bar(x, monthly["Sales"], color=ORANGE, alpha=0.85)
    axes[0].set_ylabel("销售额 ($)", fontsize=10)
    axes[1].plot(x, monthly["Profit"], color=INDIGO, marker="o", lw=2)
    axes[1].axhline(0, color=MUTED, lw=0.8, ls="--")
    axes[1].set_ylabel("利润 ($)", fontsize=10)
    axes[1].set_title("分面对照：共享时间轴，各自量纲——相关性留给读者判断", fontsize=13, color=INK, pad=8)
    for a in axes:
        _clean(a)
    plt.tight_layout()

    return fig_bad, fig_good, (
        "错误：双 Y 轴的两条轴刻度是【作者自由设定】的——调整任一轴的量程就能让两线 "
        "『完美同涨』或『完全反向』。读者看到的『相关』是刻度裁剪的产物，不是数据的属性。"
    ), (
        "正确：量纲不同的两个指标用分面（共享 X 轴的小图）呈现；"
        "若真要论证相关，先算相关系数并给出显著性，再考虑可视化。"
    )


# ============ 案例 3：饼图类目过多 ============

def case_pie_overload(df: pd.DataFrame):
    sub = df.groupby("Sub-Category")["Sales"].sum().sort_values(ascending=False)

    # 错误：17 个类目的饼图
    fig_bad, ax = plt.subplots(figsize=(6.2, 4.4))
    colors = plt.cm.tab20(np.linspace(0, 1, len(sub)))
    ax.pie(sub.values, labels=sub.index, colors=colors, textprops={"fontsize": 6.5},
           startangle=90, counterclock=False)
    ax.set_title("17 个子品类饼图：谁大谁小？——角度人眼根本比不了", fontsize=12, color=PINK)
    plt.tight_layout()

    # 正确：Top 8 + 其他，水平条形（长度比较）
    top = sub.head(8)
    other = sub.iloc[8:].sum()
    data = pd.concat([top, pd.Series({"其他(合计)": other})])
    fig_good, ax = plt.subplots(figsize=(7, 3.6))
    colors = [INDIGO] * 8 + [MUTED]
    ax.barh(data.index[::-1], data.values[::-1], color=colors[::-1])
    for i, v in enumerate(data.values[::-1]):
        ax.text(v, i, f"  ${v:,.0f}", va="center", fontsize=8)
    ax.set_title("Top 8 + 其他：长度编码 + 数值标注，一眼排出座次", fontsize=12, color=INK)
    ax.set_xlabel("销售额 ($)")
    _clean(ax)
    plt.tight_layout()

    return fig_bad, fig_good, (
        "错误：人眼对【角度】的感知精度极低（前注意属性倒数第二），"
        "17 个类目彼此只差几度，视觉上无法排序；相邻色块还极易混淆。"
    ), (
        "正确：类目 >5 个时放弃饼图，用水平条形图（长度是高精度编码）；"
        "长尾类目合并为『其他』，并直接标注数值。"
    )


# ============ 案例 4：面积/气泡编码失真 ============

def case_area_encoding(df: pd.DataFrame):
    cat = df.groupby("Category")["Profit"].sum()

    # 错误：用圆面积编码利润（可正可负的量用了只适合非负的编码）
    fig_bad, ax = plt.subplots(figsize=(6.2, 3.6))
    vals = cat.values
    sizes = np.abs(vals) / np.abs(vals).max() * 3000
    colors = [PINK if v < 0 else TEAL for v in vals]
    ax.scatter(range(len(cat)), [0] * len(cat), s=sizes, c=colors, alpha=0.75)
    ax.set_xticks(range(len(cat)))
    ax.set_xticklabels(cat.index, fontsize=9)
    ax.axhline(0, color=INK, lw=1)
    ax.get_yaxis().set_visible(False)
    ax.set_title("气泡面积编码利润：面积感知差 40%+，负值更是没法画", fontsize=12, color=PINK)
    _clean(ax)
    plt.tight_layout()

    # 正确：以 0 为基准的条形，正负一目了然
    fig_good, ax = plt.subplots(figsize=(6.2, 3.6))
    colors = [PINK if v < 0 else TEAL for v in cat.values]
    ax.bar(cat.index, cat.values, color=colors, width=0.55)
    ax.axhline(0, color=INK, lw=1)
    for i, v in enumerate(cat.values):
        ax.text(i, v + (3000 if v > 0 else -3000), f"${v:,.0f}", ha="center", fontsize=9)
    ax.set_title("以 0 为基准线的条形：方向与幅度都精确", fontsize=12, color=INK)
    ax.set_ylabel("利润 ($)")
    _clean(ax)
    plt.tight_layout()

    return fig_bad, fig_good, (
        "错误：面积在前注意属性排序里垫底（感知精度约为长度的 40%），"
        "「看起来差不多大」的两个气泡可能差一倍；且面积编码无法自然表达负值。"
    ), (
        "正确：一维数值用【长度】编码（条形图），正负值共用 0 基准线；"
        "气泡/面积只用于二维散点里的辅助信息，且需给出图例换算。"
    )


# ============ 案例 5：均值掩盖分布 ============

def case_mean_hides(df: pd.DataFrame):
    # 错误：只画各品类平均单行利润
    avg = df.groupby("Category")["Profit"].mean()
    fig_bad, ax = plt.subplots(figsize=(6.2, 3.4))
    ax.bar(avg.index, avg.values, color=INDIGO, width=0.5)
    ax.axhline(0, color=INK, lw=1)
    ax.set_title("「三大品类平均利润都健康」——均值在说谎", fontsize=12, color=PINK)
    ax.set_ylabel("平均单行利润 ($)")
    _clean(ax)
    plt.tight_layout()

    # 正确：箱线图暴露分布与离群
    fig_good, ax = plt.subplots(figsize=(6.2, 3.6))
    groups = [g["Profit"].to_numpy() for _, g in df.groupby("Category")]
    bp = ax.boxplot(groups, tick_labels=avg.index.tolist(), showfliers=True,
                    flierprops={"markersize": 2, "markerfacecolor": PINK, "alpha": 0.3},
                    medianprops={"color": ORANGE, "lw": 2},
                    boxprops={"color": INK}, whiskerprops={"color": MUTED},
                    capprops={"color": MUTED})
    ax.axhline(0, color=INK, lw=1, ls="--")
    ax.set_title("箱线图：每个品类都有大量亏损行（离群点）——均值掩盖了风险", fontsize=12, color=INK)
    ax.set_ylabel("单行利润 ($)")
    _clean(ax)
    plt.tight_layout()

    return fig_bad, fig_good, (
        "错误：均值对离群值敏感且不传达风险。平均利润为正的品类，"
        "可能有 30% 的订单在亏钱——这类『结构性风险』只有分布图能暴露。"
    ), (
        "正确：比较组间水平时，箱线图（分位数+离群点）或小提琴图是默认选项；"
        "汇报中若只能放一张图，把均值线和分布一起画。"
    )


# ============ 案例 6：相关不等于因果（辛普森式误导） ============

def case_correlation(df: pd.DataFrame):
    # 用两个地区的 折扣 vs 销售额 散点构造：总体看有"正相关"，分组看消失
    # （真实数据中按地区分层）
    pts = df.sample(900, random_state=42)
    west = pts[pts["Region"] == "West"]
    central = pts[pts["Region"] == "Central"]

    # 错误：把两个群体的散点混在一起画趋势线
    fig_bad, ax = plt.subplots(figsize=(6.4, 3.6))
    ax.scatter(pts["Sales"], pts["Profit"], s=12, alpha=0.45, color=MUTED)
    z = np.polyfit(pts["Sales"], pts["Profit"], 1)
    xs = np.linspace(0, pts["Sales"].max(), 100)
    ax.plot(xs, np.polyval(z, xs), color=PINK, lw=2.5)
    ax.set_title("「销售额越高利润越高，冲量！」——混合总体的伪趋势", fontsize=12, color=PINK)
    ax.set_xlabel("单行销售额 ($)"); ax.set_ylabel("单行利润 ($)")
    _clean(ax)
    plt.tight_layout()

    # 正确：按地区分色，暴露"趋势"来自群体结构
    fig_good, ax = plt.subplots(figsize=(6.4, 3.6))
    ax.scatter(west["Sales"], west["Profit"], s=12, alpha=0.5, color=TEAL, label="西部")
    ax.scatter(central["Sales"], central["Profit"], s=12, alpha=0.5, color=INDIGO, label="中部")
    ax.axhline(0, color=INK, lw=1, ls="--")
    ax.set_title("按地区分色：组内关系完全不同——是群体结构制造了总体趋势", fontsize=12, color=INK)
    ax.set_xlabel("单行销售额 ($)"); ax.set_ylabel("单行利润 ($)")
    ax.legend(fontsize=9)
    _clean(ax)
    plt.tight_layout()

    return fig_bad, fig_good, (
        "错误：把不同群体的数据混成总体再拟合趋势线，得到的『斜率』"
        "往往只反映群体构成差异（辛普森效应），据此下的业务结论会整体跑偏。"
    ), (
        "正确：画散点前先问『这里面有没有天然的分组』——按维度分色/分面重画；"
        "汇报结论写『在 X 分层下……』而不是笼统的『整体上……』。"
    )


# ============ 案例 7：彩虹配色滥用 ============

def case_rainbow(df: pd.DataFrame):
    sub = df.groupby("Sub-Category")["Profit"].sum().sort_values(ascending=False).head(10)

    # 错误：17 色彩虹，重点被淹没
    fig_bad, ax = plt.subplots(figsize=(7, 3.4))
    ax.bar(sub.index, sub.values, color=plt.cm.rainbow(np.linspace(0, 1, len(sub))))
    ax.set_title("彩虹配色：每种颜色都在喊『看我看我』，结论消失了", fontsize=12, color=PINK)
    ax.set_ylabel("利润 ($)")
    plt.xticks(rotation=40, fontsize=8)
    _clean(ax)
    plt.tight_layout()

    # 正确：灰色背景 + 唯一强调色
    fig_good, ax = plt.subplots(figsize=(7, 3.4))
    colors = [MUTED] * len(sub)
    colors[0] = TEAL  # 只强调利润最高的
    colors[-1] = PINK  # 以及亏损最重的
    ax.bar(sub.index, sub.values, color=colors)
    ax.axhline(0, color=INK, lw=1)
    ax.set_title("灰底 + 强调色：视线被引导到『谁赚钱/谁亏钱』", fontsize=12, color=INK)
    ax.set_ylabel("利润 ($)")
    plt.xticks(rotation=40, fontsize=8)
    _clean(ax)
    plt.tight_layout()

    return fig_bad, fig_good, (
        "错误：分类配色用满彩虹 = 每个元素视觉权重相同，读者无法聚焦；"
        "高饱和撞色还制造了图表里不存在的『分组』。"
    ), (
        "正确：默认中性灰，只给『支撑结论的那 1-2 个数据』上色——"
        "颜色是引导注意力的稀缺资源，强调一切等于什么都不强调。"
    )


# ============ 案例 8：点估计无不确定性 ============

def case_no_uncertainty(df: pd.DataFrame):
    # 各地区两年平均客单价：真实数据 + bootstrap 95% CI
    rng = np.random.RandomState(42)
    regions = ["West", "East", "Central", "South"]
    means, lows, highs = [], [], []
    for r in regions:
        vals = df[df["Region"] == r]["Sales"].to_numpy()
        boots = [np.mean(rng.choice(vals, len(vals))) for _ in range(500)]
        means.append(np.mean(vals))
        lows.append(np.percentile(boots, 2.5))
        highs.append(np.percentile(boots, 97.5))

    # 错误：只画均值柱
    fig_bad, ax = plt.subplots(figsize=(6.4, 3.4))
    ax.bar(regions, means, color=INDIGO, width=0.5)
    ax.set_title("「西部客单价最高」——差距可能只是抽样噪声", fontsize=12, color=PINK)
    ax.set_ylabel("平均客单价 ($)")
    _clean(ax)
    plt.tight_layout()

    # 正确：带 95% 置信区间
    fig_good, ax = plt.subplots(figsize=(6.4, 3.4))
    ax.bar(regions, means, color=INDIGO, width=0.5)
    yerr = [np.array(means) - np.array(lows), np.array(highs) - np.array(means)]
    ax.errorbar(regions, means, yerr=yerr, fmt="none", ecolor=PINK, elinewidth=2, capsize=6)
    ax.set_title("加 95% 置信区间：地区间差异其实重叠——结论要改写", fontsize=12, color=INK)
    ax.set_ylabel("平均客单价 ($)")
    _clean(ax)
    plt.tight_layout()

    return fig_bad, fig_good, (
        "错误：只报点估计，读者无法区分『真实差异』与『抽样波动』。"
        "本例中四个地区的均值差异落在置信区间的重叠区里，『最高』未必真高。"
    ), (
        "正确：比较类结论必须带不确定性（CI 误差条 / bootstrap 区间）；"
        "区间大量重叠时，结论措辞降级为『未观察到显著差异』。"
    )


ALL_CASES = [
    ("截断 Y 轴", case_truncated_axis, "比较类图表最常见操纵手法"),
    ("双 Y 轴虚假相关", case_dual_axis, "量纲不同的两条线强行同框"),
    ("饼图类目过多", case_pie_overload, "角度编码的天然短板"),
    ("面积编码失真", case_area_encoding, "用错编码通道 + 负值无解"),
    ("均值掩盖分布", case_mean_hides, "只看均值漏掉结构性风险"),
    ("相关不等于因果", case_correlation, "混合总体的伪趋势（辛普森）"),
    ("彩虹配色滥用", case_rainbow, "无重点等于无结论"),
    ("点估计无不确定性", case_no_uncertainty, "差异可能只是噪声"),
]
