# 数据汇报与可视化方法论 Report & ChartCraft

「怎么把数据分析讲清楚」的训练场（Streamlit + matplotlib），
基于 superstore 真实零售数据，用**正反对照**的方式教学可视化方法论。

## 数据来源（公开，可自由迁移）

Tableau Sample-Superstore 公开示例数据集（5,901 行，2019-2020，
与零售洞察项目同源；来源与许可见该数据集说明），随项目打包，离线可运行。

## 运行

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 功能（4 页）

| 页 | 内容 |
|---|---|
| 🗺️ 图表选型决策树 | 六类数据关系（构成/比较/分布/关系/趋势/排名）→ 主力图型 + 铁律 + 真实数据演示 |
| ⚠️ 误用案例图鉴 | **8 组正反对照图**（matplotlib）：截断 Y 轴 / 双轴虚假相关 / 饼图超载 / 面积编码失真 / 均值掩盖分布 / 辛普森伪趋势 / 彩虹配色 / 点估计无 CI |
| 📰 汇报金字塔 | SCQA 开场结构、一页纸模板（真实数据填充示例）、标题写法对比 |
| 🎨 前注意属性 | 同一数据的长度 vs 面积编码对比，感知精度排序演示 |

配套 **`讲解.html`**（杂志特刊风，浏览器直接打开）：图表六问、前注意属性金字塔、
误用「八宗罪」实录、汇报金字塔、标题改写工坊、发布前 12 项核对清单。

## 方法论红线

- 错误示范只改**编码方式与坐标处理**，数据本身一字不篡改（每张图可复算）
- 图表全部基于真实 superstore 数据渲染；结论文案引用计算数字

## 目录结构

```
report-chartcraft/
├── app.py               # Streamlit 应用（4 页）
├── 讲解.html             # 杂志特刊风讲解（独立视觉风格）
├── requirements.txt
├── data/superstore.csv
└── src/
    └── chartbook.py     # 8 组正反对照图生成器（matplotlib，中文已配置）
```

## 推上 GitHub

```bash
git init
git add .
git commit -m "feat: 数据汇报与可视化方法论 v1.0"
git branch -M main
git remote add origin https://github.com/<你的用户名>/report-chartcraft.git
git push -u origin main
```

## License

MIT
