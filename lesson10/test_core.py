"""lesson10_5 核心函式的基本測試。"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# 確保 lesson10_5 可被匯入
sys.path.insert(0, str(Path(__file__).resolve().parent))

from lesson10_5 import CheckResult, check_website


# ===========================================================================
# CheckResult 資料結構測試
# ===========================================================================

class TestCheckResult:
    """CheckResult dataclass 的基本行為。"""

    def test_default_values(self) -> None:
        r = CheckResult(url="https://example.com", browser_name="chromium")
        assert r.url == "https://example.com"
        assert r.browser_name == "chromium"
        assert r.status is None
        assert r.title == ""
        assert r.heading == ""
        assert r.success is False
        assert r.message == ""

    def test_success_result(self) -> None:
        r = CheckResult(
            url="https://example.com",
            browser_name="chromium",
            status=200,
            title="Example Domain",
            heading="Example Domain",
            success=True,
            message="檢查完成",
        )
        assert r.status == 200
        assert r.success is True


# ===========================================================================
# check_website 整合測試（需要網路 + Playwright）
# ===========================================================================

@pytest.mark.skipif(
    not pytest.importorskip("playwright"),
    reason="playwright 未安裝",
)
class TestCheckWebsite:
    """check_website() 的整合測試。"""

    def test_example_com_returns_200(self) -> None:
        result = check_website(
            url="https://example.com/",
            browser_name="chromium",
            headless=True,
        )
        assert result.success is True, result.message
        assert result.status == 200
        assert "Example Domain" in result.title
        assert result.screenshot is not None
        assert result.screenshot.exists()

    def test_invalid_url_returns_failure(self) -> None:
        result = check_website(
            url="https://this-site-definitely-does-not-exist-12345.example",
            browser_name="chromium",
            headless=True,
            timeout_ms=10_000,
        )
        # 網路錯誤應回傳失敗，不應拋出例外
        assert result.success is False
        assert result.message != ""

    def test_screenshot_saved(self, tmp_path: Path) -> None:
        result = check_website(
            url="https://example.com/",
            browser_name="chromium",
            headless=True,
            output_dir=tmp_path,
        )
        assert result.success is True, result.message
        assert result.screenshot is not None
        assert result.screenshot.parent == tmp_path
        assert result.screenshot.stat().st_size > 0
