import json
import sys
from datetime import date
from openai import OpenAI
from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, MODEL_NAME
from prompts import SYSTEM_PROMPT, TOOLS
from weather_info import get_weather, DayWeather
from statistics import compute_w

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)


def _serialize_weather(w: DayWeather) -> dict:
    return {
        "date": w.date,
        "weather_type": w.weather_type,
        "temp_high": w.temp_high,
        "temp_low": w.temp_low,
        "temp_avg": w.temp_avg,
    }


def _execute_tool(name: str, args: dict) -> str:
    if name != "query_weather":
        return json.dumps({"error": f"未知工具: {name}"}, ensure_ascii=False)

    weather_list = get_weather(args["city"], args["start_date"], args["end_date"])
    if not weather_list:
        return json.dumps(
            {"error": f"无法获取{args['city']}在{args['start_date']}~{args['end_date']}的天气数据"},
            ensure_ascii=False,
        )

    result = {
        "city": args["city"],
        "start_date": args["start_date"],
        "end_date": args["end_date"],
        "daily": [_serialize_weather(w) for w in weather_list],
    }

    metrics = args.get("metrics")
    if metrics:
        result["statistics"] = compute_w(weather_list, metrics)

    return json.dumps(result, ensure_ascii=False)


def run_agent(user_input: str):
    today_str = date.today().isoformat()
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"今天是{today_str}，用户输入：{user_input}"},
    ]

    for _ in range(5):
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
        )
        msg = response.choices[0].message

        if not msg.tool_calls:
            print(msg.content)
            return

        messages.append(msg)

        for tc in msg.tool_calls:
            args = json.loads(tc.function.arguments)
            content = _execute_tool(tc.function.name, args)
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": content})

    print("已达到最大交互轮数，请重试")


if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else "武汉未来五天天气怎么样"
    run_agent(query)
