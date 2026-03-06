---
name: data_analysis
description: 使用 pandas 对 data/ 目录下的 Excel / CSV 文件进行对话式数据分析
---

## 触发条件

当用户提到以下任意关键词时启用本技能：
- 数据分析、分析数据、分析一下
- 销售数据、销售额、销售量、销售报表
- Excel、表格、CSV
- 最高、最低、排名、汇总、趋势、对比、同比、环比

---

## 分析流程

### 第一步：了解数据结构

先调用 `list_data_files` 工具，获取 `data/` 目录下所有文件的信息：
- 文件名与大小
- Sheet 列表（Excel）
- 每个 Sheet 的列名和行数

根据返回结果判断使用哪个文件、哪个 Sheet。

### 第二步：编写并执行分析代码

使用 `python_repl_ast` 工具执行 pandas 代码。

**读取 Excel 文件**：
```python
import pandas as pd
df = pd.read_excel("data/sales_2025.xlsx", sheet_name="Sheet1")
df.head()
```

**读取 CSV 文件**：
```python
import pandas as pd
df = pd.read_csv("data/sales.csv", encoding="utf-8-sig")
df.head()
```

**常用分析模式**：

```python
# 分组聚合（如：各产品销售额总计）
df.groupby("产品")["销售额"].sum().sort_values(ascending=False)

# 时间筛选（如：上个月的数据）
df["日期"] = pd.to_datetime(df["日期"])
last_month = df[df["日期"].dt.month == (pd.Timestamp.now().month - 1)]

# 排名（如：销售额 Top 5）
df.nlargest(5, "销售额")[["产品", "销售额"]]

# 同比 / 环比（需要有时间列）
df_monthly = df.groupby(df["日期"].dt.to_period("M"))["销售额"].sum()
df_monthly.pct_change()  # 环比增长率

# 描述性统计
df["销售额"].describe()

# 多条件筛选
df[(df["区域"] == "华东") & (df["销售额"] > 10000)]
```

### 第三步：以清晰中文回复用户

将分析结果整理为易读的中文回答，包括：
- 直接回答用户问题
- 关键数字（最高值、总计、占比等）
- 如有必要，列出 Top N 明细

---

## 注意事项

- 文件路径统一使用相对路径 `data/文件名`（代码在 backend/ 目录下执行）
- 中文列名正常使用，无需额外处理
- 数据量较大（> 10 万行）时，先用 `.head(100)` 预览再决定分析策略
- 如果列名含空格或特殊字符，用 `df["列名"]` 方式访问，不用 `df.列名`
- Excel 日期列可能被读为字符串，需 `pd.to_datetime(df["日期"])` 转换
- 若文件读取报错，检查 `sheet_name` 是否与 `list_data_files` 返回的一致
