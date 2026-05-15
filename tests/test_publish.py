import pytest
from unittest.mock import AsyncMock, patch

from src.publish.service import publish


@pytest.mark.asyncio
async def test_publish_no_cookie_returns_not_configured():
    with patch("src.publish.service.get_settings") as mock_settings:
        mock_settings.return_value.csdn_cookie = ""

        result = await publish("title", "content", [], [])

        assert result["status"] == "not_configured"
        assert result["article_id"] == ""


@pytest.mark.asyncio
async def test_publish_success():
    with (
        patch("src.publish.service.get_settings") as mock_settings,
        patch("httpx.AsyncClient.post") as mock_post,
    ):
        mock_settings.return_value.csdn_cookie = "valid_cookie"
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": {"article_id": 12345}}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        result = await publish("Test Title", "Test Content", ["鸿蒙"], ["HarmonyOS"])

        assert result["article_id"] == "12345"
        assert result["status"] == "draft"
        assert "12345" in result["url"]


@pytest.mark.asyncio
async def test_publish_http_error():
    with (
        patch("src.publish.service.get_settings") as mock_settings,
        patch("httpx.AsyncClient.post") as mock_post,
    ):
        import httpx

        mock_settings.return_value.csdn_cookie = "valid_cookie"
        mock_response = AsyncMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        error = httpx.HTTPStatusError("unauthorized", request=AsyncMock(), response=mock_response)
        mock_response.raise_for_status.side_effect = error
        mock_post.return_value = mock_response

        with pytest.raises(httpx.HTTPStatusError):
            await publish("Title", "Content", [], [])
