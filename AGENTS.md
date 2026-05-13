# AGENTS.md — weather_demo

Chinese NL → Agent (Tool Calling) → Open-Meteo API → stats.

## Setup

```bash
pip install openai requests
```

Python 3.9+ required.

## Secrets

`config.py` hardcodes a DeepSeek API key. Prefer `DEEPSEEK_API_KEY` env var; do not commit the file.

## Run

```bash
python main.py                                    # default query
python main.py "北京未来三天平均气温"              # custom query
```

## Structure

| File | Role |
|---|---|
| `main.py` | Agent loop — LLM decides tool calls, executes, responds |
| `prompts.py` | System prompt + `TOOLS` definition (single tool `query_weather`) |
| `weather_info.py` | Open-Meteo API client (geocoding + forecast, free, no key) |
| `statistics.py` | Compute avg_temp / rain_ratio / cloudy_ratio / sunny_ratio |
| `config.py` | API key, base URL, model name |

## Agent flow

```
用户 → LLM(tools=TOOLS) → 调用 query_weather → 后端 get_weather ± compute_w
  → LLM 分析结果 → 自然语言回答
```

- `query_weather` 接受可选 `metrics` 参数。用户问统计时传入，只问天气时仅返回 daily 数据
- `main.py:run_agent()` 最多 5 轮交互，超出则报错

## API dependencies

- **DeepSeek** (via OpenAI SDK): requires `DEEPSEEK_API_KEY` + `DEEPSEEK_BASE_URL`
- **Open-Meteo** (geocoding + weather): free, no auth, 今天~未来15天

## Gotchas

- `weather_info.py` 日期自动裁剪到 `[today, today+15]`，超出则返回 `[]`
- WMO 码映射简化：晴/阴/雨/雪 (`weather_info.py:15-25`)
- `deepseek-chat` 支持工具调用，避免使用 `response_format` 参数
