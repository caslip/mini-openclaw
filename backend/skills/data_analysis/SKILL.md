---
name: data_analysis
description: 数据分析与 Excel 处理工具集 - 用于分析 data/ 目录下的 Excel 数据文件
---

## 触发条件

当用户请求以下类型时使用本技能：
- 数据查询（"2024 Q3 销售额是多少？"、"Q1-Q4 销售趋势"）
- 数据统计（"每月平均订单量"、"最高销售额客户"）
- 多表关联（"按客户查看销售"、"按产品类别汇总"）
- 可视化（"画趋势图"）
- 数据导出（"导出为 CSV"）

---

## 重要：数据格式说明

**Sell-in 数据文件是 SAP BusinessObjects (BEx) 格式的导出**，前 10 行是元数据，真正的数据从第 11 行开始：
- 第 10 行（索引 10）：列名（如 "Absatzmenge", "Summe Produkt-Nettoumsatz"）
- 第 11 行（索引 11）：单位（如 "ST", "EUR"）
- 第 12 行开始：实际数据

**必须使用特殊的读取函数**，否则无法正确读取数据！

---

## 使用流程

### 步骤 1：加载数据分析工具函数

在 Python REPL 中执行以下预定义函数：

```python
import pandas as pd
from pathlib import Path
from datetime import datetime

# 配置
DATA_BASE = Path("backend/data")

# === SAP BEx 格式专用读取函数 ===

def load_sap_bex(file_key_or_path, sheet=0):
    """
    读取 SAP BusinessObjects BEx 格式的 Excel 文件
    
    特点：前 10 行是元数据，第 11 行是列名，第 12 行开始是数据
    
    用法:
        df = load_sap_bex("Actuals_2024_Q3")
        df = load_sap_bex("10_Sell-in data/Actuals 2024 Q3.xlsx")
    """
    # 确定文件路径
    if file_key_or_path.startswith('Actuals_') or file_key_or_path.startswith('10_'):
        # 使用 catalog key 映射
        catalog_map = {
            "Actuals_2023_Q3": "10_Sell-in data/Actuals 2023 Q3.xlsx",
            "Actuals_2023_Q4": "10_Sell-in data/Actuals 2023 Q4.xlsx",
            "Actuals_2024_Q1": "10_Sell-in data/Actuals 2024 Q1.xlsx",
            "Actuals_2024_Q2": "10_Sell-in data/Actuals 2024 Q2.xlsx",
            "Actuals_2024_Q3": "10_Sell-in data/Actuals 2024 Q3.xlsx",
            "Actuals_2024_Q4": "10_Sell-in data/Actuals 2024 Q4.xlsx",
            "Actuals_2025_Q1": "10_Sell-in data/Actuals 2025 Q1.xlsx",
            "Actuals_2025_Q2": "10_Sell-in data/Actuals 2025 Q2.xlsx",
            "Actuals_2025_Q3": "10_Sell-in data/Actuals 2025 Q3.xlsx",
            "Actuals_2025_Q4": "10_Sell-in data/Actuals 2025 Q4.xlsx",
        }
        file_path = DATA_BASE / catalog_map.get(file_key_or_path, file_key_or_path)
    else:
        file_path = DATA_BASE / file_key_or_path.replace('\\', '/')
    
    print(f"加载文件: {file_path}")
    
    # 读取 Excel，跳过前 10 行元数据
    df = pd.read_excel(file_path, sheet_name=sheet, skiprows=10, header=None)
    
    # 获取列名（第 0 行）和单位（第 1 行），我们只需要列名
    col_names = df.iloc[0].tolist()
    
    # 跳过前两行（列名行和单位行）
    df = df.iloc[2:].copy()
    df.columns = col_names
    
    # 重命名已知列
    rename_map = {
        'Absatzmenge': 'Menge',
        'Summe Produkt-Nettoumsatz': 'Umsatz',
        'Deckungsbeitrag II': 'Deckungsbeitrag'
    }
    for old, new in rename_map.items():
        if old in df.columns:
            df.rename(columns={old: new}, inplace=True)
    
    # 清理列名中的 NaN
    new_cols = []
    for i, col in enumerate(df.columns):
        if pd.isna(col):
            new_cols.append(f'Col_{i}')
        else:
            new_cols.append(str(col))
    df.columns = new_cols
    
    # 转换数值列
    for col in ['Menge', 'Umsatz', 'Deckungsbeitrag']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # 转换日期列
    if 'Datum' in df.columns:
        df['Datum'] = pd.to_numeric(df['Datum'], errors='coerce')
        # SAP 日期格式：20240701 -> 2024-07-01
        df['Datum'] = df['Datum'].apply(lambda x: pd.to_datetime(str(int(x)), format='%Y%m%d') if pd.notna(x) else None)
    
    print(f"已加载 {len(df)} 行, {len(df.columns)} 列")
    return df


# === 标准读取函数（用于非 SAP 格式文件）===

def load_file(file_key_or_path, sheet=0):
    """
    标准方式读取 Excel/CSV 文件
    
    用法:
        df = load_file("Kundenhierarchie")
    """
    catalog_map = {
        "Kundenhierarchie_alleVKO": "10_Sell-in data/Kundenhierarchie_alleVKO_20260105.xlsx",
        "Produkthierarchie": "10_Sell-in data/Produkthierarchie.xlsx",
    }
    
    if file_key_or_path in catalog_map:
        file_path = DATA_BASE / catalog_map[file_key_or_path]
    else:
        file_path = DATA_BASE / file_key_or_path.replace('\\', '/')
    
    print(f"加载文件: {file_path}")
    df = pd.read_excel(file_path, sheet_name=sheet)
    print(f"已加载 {len(df)} 行, {len(df.columns)} 列")
    return df


# === 数据处理工具 ===

def sum_sales(df):
    """计算销售额总计
    
    用法:
        total = sum_sales(df)
    """
    if 'Umsatz' in df.columns:
        return df['Umsatz'].sum()
    return None


def sales_by_customer(df, top_n=10):
    """按客户汇总销售额
    
    用法:
        result = sales_by_customer(df, 10)
    """
    if 'Umsatz' not in df.columns:
        return None
    
    if 'Kunde' in df.columns:
        return df.groupby('Kunde')['Umsatz'].sum().sort_values(ascending=False).head(top_n)
    else:
        # 尝试从 Kunde 列提取 VKO
        return None


def sales_by_product(df, top_n=10):
    """按产品汇总销售额
    
    用法:
        result = sales_by_product(df, 10)
    """
    if 'Umsatz' not in df.columns or 'Artikel' not in df.columns:
        return None
    
    return df.groupby('Artikel')['Umsatz'].sum().sort_values(ascending=False).head(top_n)


def monthly_sales(df):
    """按月汇总销售额
    
    用法:
        trend = monthly_sales(df)
    """
    if 'Umsatz' not in df.columns or 'Datum' not in df.columns:
        return None
    
    df = df.copy()
    df['Month'] = df['Datum'].dt.to_period('M')
    return df.groupby('Month')['Umsatz'].sum()


# === 常用查询快捷函数 ===

def q_sales_total(year=2024, quarter=3):
    """查询指定季度销售额总计
    
    用法:
        total = q_sales_total(2024, 3)   # 2024 Q3
        total = q_sales_total(2025, 1)   # 2025 Q1
    """
    df = load_sap_bex(f"Actuals_{year}_Q{quarter}")
    return sum_sales(df)


def q_sales_by_customer(year=2024, quarter=3, top_n=5):
    """按客户查询销售额
    
    用法:
        result = q_sales_by_customer(2024, 3, 10)
    """
    df = load_sap_bex(f"Actuals_{year}_Q{quarter}")
    return sales_by_customer(df, top_n)


def q_monthly_trend(year=2024, quarter=3):
    """月度销售趋势
    
    用法:
        trend = q_monthly_trend(2024, 3)
    """
    df = load_sap_bex(f"Actuals_{year}_Q{quarter}")
    return monthly_sales(df)


print("=" * 60)
print("✅ 数据分析工具函数已加载")
print("=" * 60)
print()
print("【SAP BEx 格式专用函数】")
print("  load_sap_bex(key)      - 读取 SAP BEx 格式的 Actuals 文件")
print()
print("【标准函数】")
print("  load_file(key)          - 读取普通 Excel/CSV 文件")
print("  sum_sales(df)           - 销售额总计")
print("  sales_by_customer(df)   - 按客户汇总")
print("  sales_by_product(df)    - 按产品汇总")
print("  monthly_sales(df)       - 按月趋势")
print()
print("【快捷查询】")
print("  q_sales_total(year, q)           - 查询季度销售额")
print("  q_sales_by_customer(year, q, n)   - 按客户查询 Top N")
print("  q_monthly_trend(year, q)          - 月度趋势")
print()
print("【使用示例】")
print("  total = q_sales_total(2024, 3)")
print("  print(f'2024 Q3 销售额: {total:,.2f} EUR')")
print("=" * 60)
```

### 步骤 2：执行分析

示例：

```python
# 查询 2024 Q3 销售额总计
total = q_sales_total(2024, 3)
print(f"2024 Q3 销售额: {total:,.2f} EUR")

# 按客户查看 Top 5
top_customers = q_sales_by_customer(2024, 3, 5)
print(top_customers)

# 月度趋势
trend = q_monthly_trend(2024, 3)
print(trend)
```

---

## 注意事项

1. **SAP BEx 格式**：必须使用 `load_sap_bex()` 函数读取 Actuals 文件，否则列名会变成 "Unnamed"
2. **大文件处理**：Promo 数据文件（~78MB）加载可能较慢，首次分析建议先查看数据
3. **日期格式**：SAP 日期是整數格式（如 20240701），会自动转换为日期类型
4. **数值列**：Menge（数量）、Umsatz（销售额）、Deckungsbeitrag（利润）需要转换
5. **路径分隔**：使用正斜杠 `/` 或 `Path` 对象

---

## 数据目录参考

| 文件 | Key | 说明 |
|------|-----|------|
| Actuals 2024 Q3.xlsx | `Actuals_2024_Q3` | 2024 Q3 销售数据 |
| Actuals 2024 Q4.xlsx | `Actuals_2024_Q4` | 2024 Q4 销售数据 |
| Actuals 2025 Q1.xlsx | `Actuals_2025_Q1` | 2025 Q1 销售数据 |
| ... | ... | ... |
| Kundenhierarchie | `Kundenhierarchie_alleVKO` | 客户层级 |
| Produkthierarchie | `Produkthierarchie` | 产品层级 |
