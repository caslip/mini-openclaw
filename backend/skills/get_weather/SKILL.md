---
name: get_weather
description: 获取指定城市的实时天气信息（通过 fetch_url 调用 wttr.in API）
---

## 功能说明
获取用户指定的城市实时天气信息，包括温度、降水概率、风速等详细数据。

## 使用方式
1. 用户请求时，提取城市名称
2. 构造 wttr.in API URL: `https://wttr.in/城市名?lang=zh&unit=c`
3. 调用 fetch_url 工具获取天气信息
4. 解析返回的文本格式数据并展示给用户

## 注意事项
- 支持中英文城市名，API 自动识别
- 单位可选：c(摄氏度) / f(华氏度)
- 语言可选：zh(中文) / en(英文)
- 若用户未指定城市，可询问或默认使用北京作为示例

## 调用流程
1. 确认目标城市（支持模糊匹配）
2. 调用 fetch_url(url="https://wttr.in/{城市}?lang=zh&unit=c")
3. 解析返回内容并格式化展示
4. 向用户反馈天气信息