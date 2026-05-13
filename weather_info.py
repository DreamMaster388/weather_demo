import requests
from datetime import date, timedelta
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class DayWeather:
    date: str
    weather_type: str
    temp_high: float
    temp_low: float
    temp_avg: float

# WMO 天气代码 → 中文天气类型（简化版）
WEATHER_CODE_MAP = {
    0: "晴",
    1: "晴", 2: "晴", 3: "晴",
    45: "阴", 48: "阴",
    51: "雨", 53: "雨", 55: "雨",
    61: "雨", 63: "雨", 65: "雨",
    71: "雪", 73: "雪", 75: "雪", 77: "雪",
    80: "雨", 81: "雨", 82: "雨",
    85: "雪", 86: "雪",
    95: "雨", 96: "雨", 99: "雨",
}


def _get_coordinates(city: str) -> Optional[tuple[float, float]]:
    """通过地理编码API获取城市经纬度"""
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": city, "count": 1, "language": "zh"}
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        results = data.get("results")
        if not results:
            print(f"地理编码未找到城市：{city}")
            return None
        return results[0]["latitude"], results[0]["longitude"]
    except Exception as e:
        print(f"地理编码请求失败：{e}")
        return None
    

def _fetch_daily_weather(lat: float, lon: float, start: str, end: str) -> Optional[dict]:
    """调用Open-Meteo每日天气预报接口（仅支持今天~未来15天）"""
    today = date.today()
    start_d = date.fromisoformat(start)
    end_d = date.fromisoformat(end)

    valid_start = max(start_d, today)
    valid_end = min(end_d, today + timedelta(days=15))

    if valid_start > valid_end:
        print(f"日期范围 {start} ~ {end} 不在可查询范围（今天~未来15天）")
        return None

    if valid_start != start_d or valid_end != end_d:
        start = valid_start.isoformat()
        end = valid_end.isoformat()
        print(f"日期范围已自动裁剪为 {start} ~ {end}（API仅支持今天~未来15天）")

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,temperature_2m_mean",
        "timezone": "Asia/Shanghai",
        "start_date": start,
        "end_date": end,
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"天气数据请求失败：{e}")
        return None

def get_weather(city: str, start_date: str, end_date: str) -> List[DayWeather]:
    """
    获取指定城市在日期范围内的每日天气。
    参数:
        city:       城市中文名
        start_date: 起始日期 (YYYY-MM-DD)
        end_date:   结束日期 (YYYY-MM-DD)
    返回:
        DayWeather 对象列表
    """
    coords = _get_coordinates(city)
    if not coords:
        print(f"无法获取城市 {city} 的坐标")
        return []

    raw_data = _fetch_daily_weather(coords[0], coords[1], start_date, end_date)
    if not raw_data:
        return []

    daily = raw_data.get("daily")
    if not daily:
        return []

    dates = daily["time"]
    codes = daily["weather_code"]
    highs = daily["temperature_2m_max"]
    lows = daily["temperature_2m_min"]
    means = daily["temperature_2m_mean"]

    result = []
    for i in range(len(dates)):
        wt_code = codes[i]
        weather_type = WEATHER_CODE_MAP.get(wt_code, "未知")
        result.append(DayWeather(
            date=dates[i],
            weather_type=weather_type,
            temp_high=highs[i],
            temp_low=lows[i],
            temp_avg=means[i],
        ))
    return result
    
if __name__ == '__main__':
    print(get_weather('北京','2026-05-12','2026-05-13'))