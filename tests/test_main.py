import json
import pytest


class TestRunAgent:
    def test_no_tool_call(self, mocker, capsys):
        import main
        mock_msg = mocker.MagicMock()
        mock_msg.content = "北京明天晴天，22°C"
        mock_msg.tool_calls = None

        mock_choice = mocker.MagicMock()
        mock_choice.message = mock_msg

        mock_resp = mocker.MagicMock()
        mock_resp.choices = [mock_choice]

        mocker.patch("main.client.chat.completions.create", return_value=mock_resp)

        main.run_agent("北京明天天气怎么样")
        captured = capsys.readouterr()
        assert "北京明天晴天" in captured.out

    def test_tool_call_then_response(self, mocker, capsys):
        import main
        mock_tc = mocker.MagicMock()
        mock_tc.id = "call_001"
        mock_tc.function.name = "query_weather"
        mock_tc.function.arguments = json.dumps({
            "city": "北京", "start_date": "2026-05-14", "end_date": "2026-05-14"
        })

        tool_msg = mocker.MagicMock()
        tool_msg.content = None
        tool_msg.tool_calls = [mock_tc]

        final_msg = mocker.MagicMock()
        final_msg.content = "北京明天晴，22°C，适合户外活动。"
        final_msg.tool_calls = None

        tool_choice = mocker.MagicMock()
        tool_choice.message = tool_msg

        final_choice = mocker.MagicMock()
        final_choice.message = final_msg

        tool_resp = mocker.MagicMock()
        tool_resp.choices = [tool_choice]

        final_resp = mocker.MagicMock()
        final_resp.choices = [final_choice]

        mock_create = mocker.patch("main.client.chat.completions.create",
                                   side_effect=[tool_resp, final_resp])
        mock_execute = mocker.patch("main._execute_tool", return_value='{"ok": true}')

        main.run_agent("北京明天天气怎么样")
        captured = capsys.readouterr()
        assert "适合户外活动" in captured.out
        assert mock_create.call_count == 2

    def test_max_rounds_exceeded(self, mocker, capsys):
        import main
        mock_tc = mocker.MagicMock()
        mock_tc.id = "call_001"
        mock_tc.function.name = "query_weather"
        mock_tc.function.arguments = json.dumps({
            "city": "北京", "start_date": "2026-05-14", "end_date": "2026-05-14"
        })

        tool_msg = mocker.MagicMock()
        tool_msg.content = None
        tool_msg.tool_calls = [mock_tc]

        tool_choice = mocker.MagicMock()
        tool_choice.message = tool_msg

        tool_resp = mocker.MagicMock()
        tool_resp.choices = [tool_choice]

        mock_create = mocker.patch("main.client.chat.completions.create",
                                   return_value=tool_resp)
        mocker.patch("main._execute_tool", return_value='{"ok": true}')

        main.run_agent("北京明天天气怎么样")
        captured = capsys.readouterr()
        assert "已达到最大交互轮数" in captured.out
        assert mock_create.call_count == 5
