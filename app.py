# -*- coding: utf-8 -*-
"""数据汇报与可视化方法论（Report & ChartCraft）

基于 superstore 真实零售数据的「怎么把分析讲清楚」训练场：
图表选型决策树 → 误用案例图鉴（正反对照）→ 汇报金字塔 → 前注意属性。

运行：streamlit run app.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import src  # noqa: F401,E402

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import plotly.express as px  # noqa: E402
import plotly.graph_objects as go  # noqa: E402
import streamlit as st  # noqa: E402

from src.chartbook import ALL_CASES, load_superstore  # noqa: E402

st.set_page_config(page_title="数据汇报与可视化方法论", page_icon="📊", layout="wide")

INK, INDIGO, PINK, ORANGE, TEAL, AMBER = "#1c1917", "#4f46e5", "#FF2E7E", "#FF6A00", "#0d9488", "#d97706"
PALETTE = [INDIGO, PINK, ORANGE, TEAL, AMBER, "#7c3aed", "#0369a1", "#78716c"]

st.markdown(
    """
    <style>
    .block-container{padding-top:2rem;max-width:1280px}
    div[data-testid="stMetric"]{background:#fffef9;border:1.5px solid #1c1917;border-radius:10px;
      box-shadow:3px 3px 0 rgba(28,25,23,.85);padding:14px 18px}
    main table{border-collapse:collapse;font-size:13px;width:100%;margin:8px 0}
    main table th,main table td{border:1px solid #e5decf;padding:6px 10px;text-align:left}
    main table th{background:#f0ebdd;font-family:Georgia,'Songti SC',serif}
    main table tr:nth-child(even) td{background:#faf7ee}
    .verdict-bad{border-left:4px solid #dc2626;background:#fdf1f1;padding:10px 16px;border-radius:0 8px 8px 0;font-size:14px}
    .verdict-good{border-left:4px solid #0d9488;background:#f0f5ef;padding:10px 16px;border-radius:0 8px 8px 0;font-size:14px}
    </style>
    """,
    unsafe_allow_html=True,
)


def show_chart(fig):
    try:
        st.plotly_chart(fig, use_container_width=True)
    except TypeError:
        st.plotly_chart(fig)


def show_table(df):
    try:
        st.table(df)
    except Exception:
        st.markdown(df.to_html(index=False, border=0), unsafe_allow_html=True)


DF = load_superstore()

st.sidebar.title("📊 汇报与可视化方法论")
st.sidebar.caption("superstore 真实数据 · 正反对照教学")
page = st.sidebar.radio(
    "分析页",
    ["🗺️ 图表选型决策树", "⚠️ 误用案例图鉴", "📰 汇报金字塔", "🎨 前注意属性"],
    label_visibility="collapsed",
)


# ================= 页 1：图表选型决策树 =================
if page == "🗺️ 图表选型决策树":
    st.title("🗺️ 图表选型决策树")
    st.caption("第一问不是『画什么图』，而是『数据关系属于哪一类』——先定关系，再定图型")

    task = st.radio(
        "你的数据关系是？",
        ["构成（部分占整体）", "比较（谁大谁小）", "分布（数据长什么样）", "关系（A 变 B 怎么变）", "趋势（随时间怎么走）", "排名（座次）"],
        horizontal=True,
    )

    guides = {
        "构成（部分占整体）": dict(
            first="类目 ≤ 5 个？", ok="饼图/环形图（角度编码勉强可用）", no="类目 > 5 → 改堆叠条形 + 『其他』合并",
            demo="stack", demo_title="品类销售额构成（堆叠条形，长尾合并）",
            rule="构成图的灵魂是『占比排序』：从大到小、从上到下；最大的块必须可肉眼识别出第一"),
        "比较（谁大谁小）": dict(
            first="类目数 ≤ 10？", ok="条形图（长度编码，感知最准）", no="类目 > 10 → 只比 Top N + 『其他』",
            demo="bar", demo_title="各地区销售额对比（条形 + 数值标注）",
            rule="Y/长度轴必须从 0 开始；条形按值排序，别按字母序"),
        "分布（数据长什么样）": dict(
            first="样本量够吗？", ok="直方图 / 箱线 / 小提琴", no="样本 < 30 → 直接给数据表，分布图无意义",
            demo="box", demo_title="各品类单行利润分布（箱线 + 离群点）",
            rule="比较分布时统一 Y 轴量程；离群点单独说明来源，别悄悄删掉"),
        "关系（A 变 B 怎么变）": dict(
            first="有无天然分组？", ok="散点（先分色/分面再下结论）", no="有混杂结构 → 警惕辛普森效应",
            demo="scatter", demo_title="销售额 vs 利润（按品类分色）",
            rule="画趋势线之前先看分色散点；相关系数写进脚注而不是标题"),
        "趋势（随时间怎么走）": dict(
            first="时间粒度对吗？", ok="折线（多序列 ≤ 5 条）", no="序列 > 5 → 拆分面或只画 Top 序列",
            demo="line", demo_title="品类月度销售额趋势（分面）",
            rule="周期性数据至少覆盖 2 个完整周期再谈『趋势』；虚线连接缺失期"),
        "排名（座次）": dict(
            first="Top 几有意义？", ok="水平条形 Top N + 数值", no="全量排名 → 表格而不是图",
            demo="rank", demo_title="子品类利润排行 Top 8（正负双色）",
            rule="排名图必须标注分母（『在 17 个子品类中』）；0 基准线让正负立现"),
    }
    g = guides[task]
    with st.container(border=True):
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"**第一问**：{g['first']}")
            st.markdown(f"✅ **满足时**：{g['ok']}")
        with c2:
            st.markdown(f"**不满足时**：{g['no']}")
        st.caption(f"口诀：{g['rule']}")

    st.subheader(g["demo_title"])
    if g["demo"] == "stack":
        top = DF.groupby("Category")["Sales"].sum().nlargest(2).index.tolist()
        d = DF.copy()
        d["Cat2"] = d["Category"].where(d["Category"].isin(top), "其他")
        piv = d.pivot_table(index="Year", columns="Cat2", values="Sales", aggfunc="sum")
        fig = px.bar(piv.reset_index(), x="Year", y=piv.columns.tolist(),
                     color_discrete_sequence=PALETTE, labels={"value": "销售额 ($)"})
        fig.update_layout(height=380, barmode="stack", margin=dict(t=10, l=10, r=10, b=10))
        show_chart(fig)
    elif g["demo"] == "bar":
        reg = DF.groupby("Region")["Sales"].sum().sort_values()
        fig = px.bar(x=reg.values, y=reg.index, orientation="h", text=[f"${v:,.0f}" for v in reg.values],
                     color_discrete_sequence=[INDIGO], labels={"x": "销售额 ($)", "y": ""})
        fig.update_traces(textposition="outside")
        fig.update_layout(height=340, margin=dict(t=10, l=10, r=10, b=10))
        show_chart(fig)
    elif g["demo"] == "box":
        fig = px.box(DF.sample(2000, random_state=42), x="Category", y="Profit", color="Category",
                     color_discrete_sequence=[INDIGO, PINK, ORANGE])
        fig.add_hline(y=0, line=dict(color=INK, dash="dot", width=1.5))
        fig.update_layout(height=380, margin=dict(t=10, l=10, r=10, b=10), showlegend=False,
                          yaxis_title="单行利润 ($)")
        show_chart(fig)
    elif g["demo"] == "scatter":
        fig = px.scatter(DF.sample(1500, random_state=42), x="Sales", y="Profit", color="Category",
                         opacity=0.6, color_discrete_sequence=[INDIGO, PINK, ORANGE],
                         labels={"Sales": "单行销售额 ($)", "Profit": "单行利润 ($)"})
        fig.add_hline(y=0, line=dict(color=INK, dash="dot", width=1))
        fig.update_layout(height=380, margin=dict(t=10, l=10, r=10, b=10))
        show_chart(fig)
    elif g["demo"] == "line":
        m = DF.groupby(["YearMonth", "Category"])["Sales"].sum().reset_index()
        fig = px.line(m, x="YearMonth", y="Sales", color="Category", facet_col="Category",
                      color_discrete_sequence=[INDIGO, PINK, ORANGE])
        fig.update_layout(height=360, margin=dict(t=10, l=10, r=10, b=10), showlegend=False)
        fig.update_yaxes(matches=None)
        show_chart(fig)
    else:
        sub = DF.groupby("Sub-Category")["Profit"].sum().sort_values(ascending=False)
        d = sub.head(8).iloc[::-1]
        colors = [PINK if v < 0 else TEAL for v in d.values]
        fig = go.Figure(go.Bar(x=d.values, y=d.index, orientation="h", marker_color=colors,
                               text=[f"${v:,.0f}" for v in d.values], textposition="outside"))
        fig.add_vline(x=0, line=dict(color=INK, width=1))
        fig.update_layout(height=380, margin=dict(t=10, l=10, r=10, b=10), xaxis_title="利润 ($)")
        show_chart(fig)


# ================= 页 2：误用案例图鉴 =================
elif page == "⚠️ 误用案例图鉴":
    st.title("⚠️ 误用案例图鉴")
    st.caption("左边是「错误示范」，右边是同一数据的「正确画法」——错误只在编码方式，数据绝无篡改")

    case_name = st.selectbox(
        "选择案例",
        [f"{name} —— {hint}" for name, _, hint in ALL_CASES],
    )
    name = case_name.split(" —— ")[0]
    fn = next(f for n, f, _ in ALL_CASES if n == name)

    fig_bad, fig_good, c_bad, c_good = fn(DF)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**❌ 错误示范**")
        st.pyplot(fig_bad)
        st.markdown(f'<div class="verdict-bad">{c_bad}</div>', unsafe_allow_html=True)
    with c2:
        st.markdown("**✅ 正确示范**")
        st.pyplot(fig_good)
        st.markdown(f'<div class="verdict-good">{c_good}</div>', unsafe_allow_html=True)

    st.caption("图由 matplotlib 生成（与 PPT/报告的静态产出形态一致）；切换案例重新渲染。")
    plt.close("all")


# ================= 页 3：汇报金字塔 =================
elif page == "📰 汇报金字塔":
    st.title("📰 汇报金字塔")
    st.caption("图表只是证据；汇报的骨架是「结论先行」——先给答案，再给支撑")

    st.subheader("SCQA 开场结构")
    with st.container(border=True):
        st.markdown(
            """
            | 组件 | 内容模板 | 本数据实例 |
            |---|---|---|
            | **S** 情境 | 读者已知的事实 | 「本季度三大品类共贡献销售额 $2.2M」 |
            | **C** 冲突 | 打破预期的发现 | 「但利润分布两极分化：科技品类贡献 61% 利润，家具品类整体亏损」 |
            | **Q** 问题 | 自然涌出的疑问 | 「资源该向哪里倾斜？」 |
            | **A** 答案 | 你的结论（先说！） | 「砍掉亏损子品类、加码科技品类的独家款」 |
            """
        )

    st.subheader("一页纸汇报模板（真实数据填充示例）")
    with st.container(border=True):
        cat = DF.groupby("Category")["Profit"].sum()
        worst_sub = DF.groupby("Sub-Category")["Profit"].sum().idxmin()
        tech_share = cat["Technology"] / cat.sum() if "Technology" in cat.index else float("nan")
        st.markdown(
            f"""
            **【标题】** 三句话讲清品类利润分化与资源再配置建议<br/>
            **【结论】** 科技品类以 {tech_share*100:.0f}% 的利润占比成为唯一利润引擎；
            家具品类整体亏损，主因是「{worst_sub}」子品类——建议季度内完成品类资源再配置。<br/>
            **【证据 1】** 品类利润构成图（见左）——三大品类一正一负一平<br/>
            **【证据 2】** 子品类分布图——亏损集中于少数 SKU，非全面恶化<br/>
            **【建议】** ① 停售 Top3 亏损子品类的长尾 SKU；② 科技品类独家款扩充 30%；
            ③ 下季度复测利润结构<br/>
            **【风险与边界】** 数据为 2019-2020 两年样本，未含品类季节性调整；
            停售决策需供应链复核库存
            """
        )
    st.caption("模板五要素：标题（结论）→ 结论 → 证据（图）→ 建议（可执行）→ 风险与边界（诚实）")

    st.subheader("标题写法对比")
    with st.container(border=True):
        st.markdown(
            """
            | 弱标题（说了等于没说） | 强标题（结论本身） |
            |---|---|
            | 「各品类利润分析」 | 「科技品类贡献 61% 利润，家具品类是唯一亏损源」 |
            | 「用户留存情况汇报」 | 「次月留存率环比下降 3pp，流失集中于新注册用户」 |
            | 「销售数据看板」 | 「Top10% 客户贡献 47% 销售额，长尾客户获客成本回收周期超 8 个月」 |
            """
        )
        st.caption("规则：读者只看标题也能带走结论；图是证据，不是主角。")


# ================= 页 4：前注意属性 =================
elif page == "🎨 前注意属性":
    st.title("🎨 前注意属性：编码通道的感知精度排序")
    st.caption("同一组数据（六值），换一种编码通道，感知精度天差地别")

    st.subheader("精度排序（高 → 低）")
    st.markdown(
        """
        **位置**（折线的坐标）＞ **长度**（条形的高度）＞ **角度**（饼图的扇形）＞ **面积**（气泡）＞ **颜色深浅/色相**
        """
    )
    st.caption("这解释了图鉴里的每个案例：比较数值用长度（条形）而不是角度（饼）或面积（气泡）。")

    vals = DF.groupby("Region")["Sales"].sum().sort_values(ascending=False)
    labels = vals.index.tolist()
    v = vals.values
    vmax, vmin = v.max(), v.min()

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**编码：长度（高精度）**")
        fig, ax = plt.subplots(figsize=(5.6, 3.4))
        ax.bar(labels, v, color=TEAL, width=0.6)
        for i, x in enumerate(v):
            ax.text(i, x, f"${x:,.0f}", ha="center", va="bottom", fontsize=9)
        ax.set_ylim(0, vmax * 1.12)
        ax.set_ylabel("销售额 ($)")
        _ = [s.set_visible(False) for s in ax.spines.values()]
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
    with c2:
        st.markdown("**编码：面积（低精度）**")
        fig, ax = plt.subplots(figsize=(5.6, 3.4))
        sizes = (v / vmax) * 5200
        ax.scatter(range(len(labels)), [1] * len(labels), s=sizes, color=ORANGE, alpha=0.8)
        for i, lab in enumerate(labels):
            ax.text(i, 0.2, lab, ha="center", fontsize=9)
        ax.set_ylim(-0.5, 2.0)
        ax.get_yaxis().set_visible(False)
        _ = [s.set_visible(False) for s in ax.spines.values()]
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    with st.container(border=True):
        st.markdown(
            f"""
            - 长度编码下，「{(vmax/v.min()).round(1)} 倍」的最大/最小差异一眼可见且能粗略估算倍数；
              面积编码下，两组看起来「差不多」，实际差数倍——感知精度差 40%+
            - 结论：**面积/颜色只用于『辅助信息』，数值主编码永远选长度或位置**
            - 颜色深浅适合编码【有序】量（如热力图），色相适合【分类】（≤7 类）——
              用色相编码数值大小是新手高频错误
            """
        )


st.divider()
st.caption(
    "数据汇报与可视化方法论 · 数据：Tableau Sample-Superstore（公开数据集）· "
    "误用图鉴由 matplotlib 生成，同一数据仅改变编码方式 · 结论由数据计算生成"
)
