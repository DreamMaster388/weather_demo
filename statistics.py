# statistics.py
from typing import List, Dict
from weather_info import DayWeather

def compute_w(weather_list: List[DayWeather], metrics: List[str]) -> Dict[str, float]:
    """
    根据天气数据列表和需求指标，计算并返回统计结果。

    Args:
        weather_list: DayWeather 对象列表
        metrics: 统计指标列表，支持 "avg_temp", "rain_ratio", "cloudy_ratio", "sunny_ratio"

    Returns:
        字典，键为指标名，值为计算结果（浮点数）
    """
    total_days = len(weather_list)
    result = {}

    # 无数据时直接返回默认值
    if total_days == 0:
        for metric in metrics:
            if metric == "avg_temp":
                result[metric] = 0.0
            elif metric.endswith("_ratio"):
                result[metric] = 0.0
        return result

    # 统计各类天气天数
    rainy_days = sum(1 for w in weather_list if w.weather_type == "雨")
    cloudy_days = sum(1 for w in weather_list if w.weather_type == "阴")
    sunny_days = sum(1 for w in weather_list if w.weather_type == "晴")
    # 注意：可能有“雪”等其他类型，不计入上述三类，也不影响比例计算

    metrics = sorted(metrics)
    for metric in metrics:
        if metric == "avg_temp":
            avg_temp = sum(w.temp_avg for w in weather_list) / total_days
            result[metric] = round(avg_temp, 1)
        elif metric == "rain_ratio":
            result[metric] = rainy_days / total_days
        elif metric == "cloudy_ratio":
            result[metric] = cloudy_days / total_days
        elif metric == "sunny_ratio":
            result[metric] = sunny_days / total_days
        # 忽略未知指标

    return result