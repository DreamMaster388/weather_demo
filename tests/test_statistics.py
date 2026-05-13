import pytest
from statistics import compute_w


class TestComputeW:
    def test_empty_list(self):
        result = compute_w([], ["avg_temp", "rain_ratio"])
        assert result == {"avg_temp": 0.0, "rain_ratio": 0.0}

    def test_single_day(self, sunny_day):
        result = compute_w([sunny_day], ["avg_temp", "sunny_ratio"])
        assert result["avg_temp"] == 25.0
        assert result["sunny_ratio"] == 1.0

    def test_all_sunny(self, sunny_day):
        days = [sunny_day] * 3
        result = compute_w(days, ["avg_temp", "sunny_ratio", "rain_ratio"])
        assert result["avg_temp"] == 25.0
        assert result["sunny_ratio"] == 1.0
        assert result["rain_ratio"] == 0.0

    def test_all_rainy(self, rainy_day):
        days = [rainy_day] * 4
        result = compute_w(days, ["rain_ratio", "sunny_ratio"])
        assert result["rain_ratio"] == 1.0
        assert result["sunny_ratio"] == 0.0

    def test_mixed_weather(self, sunny_day, rainy_day, cloudy_day):
        days = [sunny_day, rainy_day, cloudy_day, sunny_day]
        result = compute_w(days, ["avg_temp", "rain_ratio", "cloudy_ratio", "sunny_ratio"])
        assert result["avg_temp"] == 22.2
        assert result["rain_ratio"] == 0.25
        assert result["cloudy_ratio"] == 0.25
        assert result["sunny_ratio"] == 0.5

    def test_partial_metrics(self, sunny_day, rainy_day):
        days = [sunny_day, rainy_day]
        result = compute_w(days, ["avg_temp"])
        assert list(result.keys()) == ["avg_temp"]
        assert "rain_ratio" not in result

    def test_neutral_weather_not_counted_in_ratios(self, snowy_day, sunny_day, rainy_day):
        days = [snowy_day, sunny_day, rainy_day]
        result = compute_w(days, ["rain_ratio", "sunny_ratio", "cloudy_ratio"])
        assert result["rain_ratio"] == pytest.approx(1 / 3)
        assert result["sunny_ratio"] == pytest.approx(1 / 3)
        assert result["cloudy_ratio"] == 0.0
