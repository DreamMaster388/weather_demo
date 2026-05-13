import pytest
from weather_info import DayWeather


@pytest.fixture
def sunny_day():
    return DayWeather(date="2026-05-13", weather_type="晴", temp_high=30, temp_low=20, temp_avg=25)


@pytest.fixture
def rainy_day():
    return DayWeather(date="2026-05-14", weather_type="雨", temp_high=20, temp_low=15, temp_avg=17.5)


@pytest.fixture
def cloudy_day():
    return DayWeather(date="2026-05-15", weather_type="阴", temp_high=25, temp_low=18, temp_avg=21.5)


@pytest.fixture
def snowy_day():
    return DayWeather(date="2026-05-16", weather_type="雪", temp_high=-2, temp_low=-10, temp_avg=-6)
