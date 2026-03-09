"""
数据表关联关系配置
定义各个数据表之间的关联字段
"""

from datetime import datetime

# 表关系定义
RELATIONSHIPS = {
    "sell_in": {
        "description": "Sell-in 数据（销售给渠道商）",
        "tables": {
            "Actuals_2024_Q1": {
                "alias": "actuals_q1",
                "path": "data/10_Sell-in data/Actuals 2024 Q1.xlsx",
                "key_columns": ["VKO", "Artikel", "Datum"],
                "value_columns": ["Menge", "Umsatz"],
                "description": "2024 Q1 销售数据"
            },
            "Actuals_2024_Q2": {
                "alias": "actuals_q2",
                "path": "data/10_Sell-in data/Actuals 2024 Q2.xlsx",
                "key_columns": ["VKO", "Artikel", "Datum"],
                "value_columns": ["Menge", "Umsatz"],
                "description": "2024 Q2 销售数据"
            },
            "Actuals_2024_Q3": {
                "alias": "actuals_q3",
                "path": "data/10_Sell-in data/Actuals 2024 Q3.xlsx",
                "key_columns": ["VKO", "Artikel", "Datum"],
                "value_columns": ["Menge", "Umsatz"],
                "description": "2024 Q3 销售数据"
            },
            "Actuals_2024_Q4": {
                "alias": "actuals_q4",
                "path": "data/10_Sell-in data/Actuals 2024 Q4.xlsx",
                "key_columns": ["VKO", "Artikel", "Datum"],
                "value_columns": ["Menge", "Umsatz"],
                "description": "2024 Q4 销售数据"
            },
            "Actuals_2025_Q1": {
                "alias": "actuals_q1_2025",
                "path": "data/10_Sell-in data/Actuals 2025 Q1.xlsx",
                "key_columns": ["VKO", "Artikel", "Datum"],
                "value_columns": ["Menge", "Umsatz"],
                "description": "2025 Q1 销售数据"
            },
            "Actuals_2025_Q2": {
                "alias": "actuals_q2_2025",
                "path": "data/10_Sell-in data/Actuals 2025 Q2.xlsx",
                "key_columns": ["VKO", "Artikel", "Datum"],
                "value_columns": ["Menge", "Umsatz"],
                "description": "2025 Q2 销售数据"
            },
            "Actuals_2025_Q3": {
                "alias": "actuals_q3_2025",
                "path": "data/10_Sell-in data/Actuals 2025 Q3.xlsx",
                "key_columns": ["VKO", "Artikel", "Datum"],
                "value_columns": ["Menge", "Umsatz"],
                "description": "2025 Q3 销售数据"
            },
            "Actuals_2025_Q4": {
                "alias": "actuals_q4_2025",
                "path": "data/10_Sell-in data/Actuals 2025 Q4.xlsx",
                "key_columns": ["VKO", "Artikel", "Datum"],
                "value_columns": ["Menge", "Umsatz"],
                "description": "2025 Q4 销售数据"
            },
            "Kundenhierarchie_alleVKO": {
                "alias": "kunden",
                "path": "data/10_Sell-in data/Kundenhierarchie_alleVKO_20260105.xlsx",
                "key_columns": ["VKO"],
                "description_columns": ["Kundenname", "Name 1", "Name 2", "Name 3"],
                "description": "客户层级结构"
            },
            "Produkthierarchie": {
                "alias": "produkte",
                "path": "data/10_Sell-in data/Produkthierarchie.xlsx",
                "key_columns": ["Artikel"],
                "description_columns": ["Produktgruppe", "Artikelgruppe", "Artikelname"],
                "description": "产品层级结构"
            }
        },
        "joins": [
            {
                "left": "actuals.*",
                "right": "kunden",
                "on": "VKO",
                "type": "left",
                "description": "销售数据关联客户名称"
            },
            {
                "left": "actuals.*",
                "right": "produkte",
                "on": "Artikel",
                "type": "left",
                "description": "销售数据关联产品类别"
            }
        ]
    },
    "sell_out": {
        "description": "Sell-out 数据（渠道商销售给最终用户）",
        "tables": {
            "Edeka_Absatzdaten": {
                "alias": "edeka",
                "path": "data/20_Sell-out data/10 EDEKA/Edeka_Absatzdaten.xlsx",
                "key_columns": ["VKO", "Artikel", "Datum"],
                "value_columns": ["Menge"],
                "description": "EDEKA 销售数据"
            },
            "POS_Daten_Dohle": {
                "alias": "dohle",
                "path": "data/20_Sell-out data/20 HIT, AEZ etc/POS Daten Dohle.xlsx",
                "key_columns": ["VKO", "Artikel", "Datum"],
                "value_columns": ["Menge"],
                "description": "Dohle POS 数据"
            },
            "Globus_Daten_Listung": {
                "alias": "globus",
                "path": "data/20_Sell-out data/30 Globus/2026-01_Globus Daten Listung.xlsx",
                "key_columns": ["VKO", "Artikel"],
                "description": "Globus 上架数据"
            },
            "Bünting_Absatzmengen": {
                "alias": "bunting",
                "path": "data/20_Sell-out data/40 Bünting/2026-01-08_Absatzmengen_Bünting.xlsx",
                "key_columns": ["VKO", "Artikel", "Datum"],
                "value_columns": ["Menge"],
                "description": "Bünting 销售数据"
            }
        },
        "joins": [
            {
                "left": "sell_out.*",
                "right": "kunden",
                "on": "VKO",
                "type": "left",
                "description": "Sell-out 关联客户"
            }
        ]
    },
    "promo": {
        "description": "促销数据",
        "tables": {
            "Drotax_GlobalView_2024": {
                "alias": "promo_2024",
                "path": "data/30_Promo data/Drotax_GlobalView 2024.xlsx",
                "key_columns": ["VKO", "Artikel", "PromoStart", "PromoEnde"],
                "description": "2024 年促销数据"
            },
            "Drotax_GlobalView_2025": {
                "alias": "promo_2025",
                "path": "data/30_Promo data/Drotax_GlobalView 2025.xlsx",
                "key_columns": ["VKO", "Artikel", "PromoStart", "PromoEnde"],
                "description": "2025 年促销数据"
            }
        }
    },
    "listing": {
        "description": "上架/列表数据",
        "tables": {
            "Datentabellen": {
                "alias": "listing",
                "path": "data/40_Listing data/Datentabellen.xlsx",
                "key_columns": ["Artikel", "VKO"],
                "description": "产品上架信息"
            }
        }
    }
}

# 常用查询模板
QUERY_TEMPLATES = {
    "sales_by_period": {
        "description": "按时间段汇总销售额",
        "required_params": ["start_date", "end_date"],
        "table": "actuals",
        "aggregations": ["SUM(Umsatz) as Gesamtumsatz", "SUM(Menge) as Gesamtmenge"]
    },
    "sales_by_customer": {
        "description": "按客户汇总销售",
        "required_params": [],
        "table": "actuals",
        "group_by": "VKO",
        "joins": ["kunden"]
    },
    "sales_by_product": {
        "description": "按产品汇总销售",
        "required_params": [],
        "table": "actuals",
        "group_by": "Artikel",
        "joins": ["produkte"]
    },
    "promo_effect": {
        "description": "促销效果分析",
        "required_params": ["promo_period"],
        "tables": ["actuals", "promo"],
        "description": "对比促销期间与非促销期间的销售额"
    }
}


# 元信息
RELATIONSHIPS_METADATA = {
    "generated_at": datetime.now().isoformat(),
    "description": "数据表关联关系定义，用于多表查询",
    "usage": "Agent 在进行数据分析时，可以使用这些关联关系来 JOIN 多个表"
}
