import pytest


class MockResponse:
    def __init__(self, json_data, status_code=200):
        self._json = json_data
        self.status_code = status_code

    def json(self):
        return self._json

    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f"HTTP {self.status_code}")


class TestGetCoordinates:
    def test_success(self, mocker):
        mock_get = mocker.patch("weather_info.requests.get")
        mock_get.return_value = MockResponse({
            "results": [{"latitude": 39.9, "longitude": 116.4}]
        })
        from weather_info import _get_coordinates
        result = _get_coordinates("北京")
        assert result == (39.9, 116.4)

    def test_city_not_found(self, mocker):
        mock_get = mocker.patch("weather_info.requests.get")
        mock_get.return_value = MockResponse({"results": []})
        from weather_info import _get_coordinates
        result = _get_coordinates("火星镇")
        assert result is None

    def test_network_error(self, mocker):
        mocker.patch("weather_info.requests.get", side_effect=Exception("timeout"))
        from weather_info import _get_coordinates
        result = _get_coordinates("北京")
        assert result is None


class TestFetchDailyWeather:
    def test_success(self, mocker):
        mock_get = mocker.patch("weather_info.requests.get")
        mock_get.return_value = MockResponse({
            "daily": {
                "time": ["2026-05-13"],
                "weather_code": [0],
                "temperature_2m_max": [25.0],
                "temperature_2m_min": [15.0],
                "temperature_2m_mean": [20.0],
            }
        })
        from weather_info import _fetch_daily_weather
        result = _fetch_daily_weather(39.9, 116.4, "2026-05-13", "2026-05-13")
        assert result["daily"]["time"] == ["2026-05-13"]

    def test_partial_overlap_clips(self, mocker):
        mock_get = mocker.patch("weather_info.requests.get")
        mock_get.return_value = MockResponse({
            "daily": {
                "time": ["2026-05-13", "2026-05-14"],
                "weather_code": [0, 61],
                "temperature_2m_max": [25.0, 20.0],
                "temperature_2m_min": [15.0, 12.0],
                "temperature_2m_mean": [20.0, 16.0],
            }
        })
        from weather_info import _fetch_daily_weather
        result = _fetch_daily_weather(39.9, 116.4, "2026-05-01", "2026-06-01")
        assert result is not None

    def test_entirely_out_of_range(self):
        from weather_info import _fetch_daily_weather
        result = _fetch_daily_weather(39.9, 116.4, "2020-01-01", "2020-01-02")
        assert result is None

    def test_api_error_returns_none(self, mocker):
        mocker.patch("weather_info.requests.get", side_effect=Exception("API error"))
        from weather_info import _fetch_daily_weather
        result = _fetch_daily_weather(39.9, 116.4, "2026-05-13", "2026-05-13")
        assert result is None


class TestGetWeather:
    def test_success(self, mocker):
        mock_get = mocker.patch("weather_info.requests.get")
        mock_get.side_effect = [
            MockResponse({"results": [{"latitude": 39.9, "longitude": 116.4}]}),
            MockResponse({
                "daily": {
                    "time": ["2026-05-13"],
                    "weather_code": [0],
                    "temperature_2m_max": [25.0],
                    "temperature_2m_min": [15.0],
                    "temperature_2m_mean": [20.0],
                }
            }),
        ]
        from weather_info import get_weather
        result = get_weather("北京", "2026-05-13", "2026-05-13")
        assert len(result) == 1
        assert result[0].weather_type == "晴"
        assert result[0].temp_avg == 20.0
        assert mock_get.call_count == 2

    def test_city_not_found(self, mocker):
        mock_get = mocker.patch("weather_info.requests.get")
        mock_get.return_value = MockResponse({"results": []})
        from weather_info import get_weather
        result = get_weather("火星镇", "2026-05-13", "2026-05-13")
        assert result == []
        mock_get.assert_called_once()

    def test_multiple_days(self, mocker):
        mock_get = mocker.patch("weather_info.requests.get")
        mock_get.side_effect = [
            MockResponse({"results": [{"latitude": 31.2, "longitude": 121.4}]}),
            MockResponse({
                "daily": {
                    "time": ["2026-05-13", "2026-05-14", "2026-05-15"],
                    "weather_code": [0, 61, 71],
                    "temperature_2m_max": [25.0, 20.0, 0.0],
                    "temperature_2m_min": [15.0, 12.0, -5.0],
                    "temperature_2m_mean": [20.0, 16.0, -2.0],
                }
            }),
        ]
        from weather_info import get_weather
        result = get_weather("上海", "2026-05-13", "2026-05-15")
        assert len(result) == 3
        assert result[0].weather_type == "晴"
        assert result[1].weather_type == "雨"
        assert result[2].weather_type == "雪"
