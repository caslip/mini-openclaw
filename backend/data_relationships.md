# 数据表关联关系

生成时间: 2026-03-07

---

## 概述

本文档定义了各个数据表之间的关联关系，帮助 Agent 理解如何进行多表关联查询。

---

## 1. Sell-in 数据（销售给渠道商）

### 1.1 主数据表

| 表名 | 别名 | 路径 | 关键字段 | 说明 |
|------|------|------|----------|------|
| Actuals_2024_Q1 | actuals_q1 | data/10_Sell-in data/Actuals 2024 Q1.xlsx | VKO, Artikel, Datum | 2024 Q1 销售数据 |
| Actuals_2024_Q2 | actuals_q2 | data/10_Sell-in data/Actuals 2024 Q2.xlsx | VKO, Artikel, Datum | 2024 Q2 销售数据 |
| Actuals_2024_Q3 | actuals_q3 | data/10_Sell-in data/Actuals 2024 Q3.xlsx | VKO, Artikel, Datum | 2024 Q3 销售数据 |
| Actuals_2024_Q4 | actuals_q4 | data/10_Sell-in data/Actuals 2024 Q4.xlsx | VKO, Artikel, Datum | 2024 Q4 销售数据 |
| Actuals_2025_Q1 | actuals_q1_2025 | data/10_Sell-in data/Actuals 2025 Q1.xlsx | VKO, Artikel, Datum | 2025 Q1 销售数据 |
| Actuals_2025_Q2 | actuals_q2_2025 | data/10_Sell-in data/Actuals 2025 Q2.xlsx | VKO, Artikel, Datum | 2025 Q2 销售数据 |
| Actuals_2025_Q3 | actuals_q3_2025 | data/10_Sell-in data/Actuals 2025 Q3.xlsx | VKO, Artikel, Datum | 2025 Q3 销售数据 |
| Actuals_2025_Q4 | actuals_q4_2025 | data/10_Sell-in data/Actuals 2025 Q4.xlsx | VKO, Artikel, Datum | 2025 Q4 销售数据 |

### 1.2 维度表

| 表名 | 别名 | 路径 | 关键字段 | 说明 |
|------|------|------|----------|------|
| Kundenhierarchie_alleVKO | kunden | data/10_Sell-in data/Kundenhierarchie_alleVKO_20260105.xlsx | VKO | 客户层级结构 |
| Produkthierarchie | produkte | data/10_Sell-in data/Produkthierarchie.xlsx | Artikel | 产品层级结构 |

### 1.3 关联关系

```
销售数据 (Actuals_*) 
    ↕ 通过 VKO 关联 → 客户层级 (Kundenhierarchie)
    ↕ 通过 Artikel 关联 → 产品层级 (Produkthierarchie)
```

---

## 2. Sell-out 数据（渠道商销售给最终用户）

### 2.1 主数据表

| 表名 | 别名 | 路径 | 关键字段 | 说明 |
|------|------|------|----------|------|
| Edeka_Absatzdaten | edeka | data/20_Sell-out data/10 EDEKA/Edeka_Absatzdaten.xlsx | VKO, Artikel, Datum | EDEKA 销售数据 |
| POS_Daten_Dohle | dohle | data/20_Sell-out data/20 HIT, AEZ etc/POS Daten Dohle.xlsx | VKO, Artikel, Datum | Dohle POS 数据 |
| Globus_Daten_Listung | globus | data/20_Sell-out data/30 Globus/2026-01_Globus Daten Listung.xlsx | VKO, Artikel | Globus 上架数据 |
| Bünting_Absatzmengen | bunting | data/20_Sell-out data/40 Bünting/2026-01-08_Absatzmengen_Bünting.xlsx | VKO, Artikel, Datum | Bünting 销售数据 |

---

## 3. 促销数据

### 3.1 主数据表

| 表名 | 别名 | 路径 | 关键字段 | 说明 |
|------|------|------|----------|------|
| Drotax_GlobalView_2024 | promo_2024 | data/30_Promo data/Drotax_GlobalView 2024.xlsx | VKO, Artikel, PromoStart, PromoEnde | 2024 年促销数据 |
| Drotax_GlobalView_2025 | promo_2025 | data/30_Promo data/Drotax_GlobalView 2025.xlsx | VKO, Artikel, PromoStart, PromoEnde | 2025 年促销数据 |

---

## 4. 上架/列表数据

### 4.1 主数据表

| 表名 | 别名 | 路径 | 关键字段 | 说明 |
|------|------|------|----------|------|
| Datentabellen | listing | data/40_Listing data/Datentabellen.xlsx | Artikel, VKO | 产品上架信息 |

---

## 5. 常用查询模式

### 5.1 按时间段汇总销售额

```python
# 使用 actuals 表（任一季度），按日期过滤后汇总
df.groupby('Datum')['Umsatz'].sum()
```

### 5.2 按客户汇总销售

```python
# 销售数据 LEFT JOIN 客户层级
pd.merge(df, kunden, on='VKO', how='left')
df.groupby('Kundenname')['Umsatz'].sum()
```

### 5.3 按产品汇总销售

```python
# 销售数据 LEFT JOIN 产品层级
pd.merge(df, produkte, on='Artikel', how='left')
df.groupby('Produktgruppe')['Umsatz'].sum()
```

### 5.4 促销效果分析

```python
# 对比促销期间与非促销期间的销售额
promo_dates = df[df['Datum'].isin(promo_period)]
non_promo_dates = df[~df['Datum'].isin(promo_period)]
```

---

## 6. 关键字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| VKO | string | 客户编号（Vertriebs-Kunden-Organisation） |
| Artikel | string | 产品编号 |
| Datum | datetime | 日期 |
| Menge | int/float | 销售数量 |
| Umsatz | float | 销售额 |
| Kundenname | string | 客户名称 |
| Produktgruppe | string | 产品组 |
| Artikelgruppe | string | 产品类别 |
