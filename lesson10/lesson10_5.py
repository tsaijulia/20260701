"""專案 01：開啟真實網頁，檢查標題並留下截圖。

核心模組：提供 check_website() 供 CLI 與 GUI 共用。
"""

from __future__ import annotations

import argparse
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from playwright.sync_api import sync_playwright


OUTPUT_DIR = Path(__file__).resolve().parent / "output"


# ---------------------------------------------------------------------------
# 資料結構
# ---------------------------------------------------------------------------

@dataclass
class CheckResult:
    """單次網站檢查的結果。"""
    url: str
    browser_name: str
    status: Optional[int] = None
    title: str = ""
    heading: str = ""
    final_url: str = ""
    response_time_ms: float = 0.0
    screenshot: Optional[Path] = None
    success: bool = False
    message: str = ""


# ---------------------------------------------------------------------------
# 核心函式
# ---------------------------------------------------------------------------

def check_website(
    url: str,
    browser_name: str = "chromium",
    headless: bool = True,
    timeout_ms: int = 30_000,
    output_dir: Path = OUTPUT_DIR,
) -> CheckResult:
    """開啟指定瀏覽器，前往目標網站，回傳檢查結果。

    Parameters
    ----------
    url : str
        要檢查的網址。
    browser_name : str
        瀏覽器類型，可選 chromium / firefox / webkit。
    headless : bool
        是否以無頭模式啟動。
    timeout_ms : int
        導航逾時毫秒數。
    output_dir : Path
        截圖儲存目錄。

    Returns
    -------
    CheckResult
        包含 HTTP 狀態、標題、截圖路徑等資訊。
    """
    result = CheckResult(url=url, browser_name=browser_name)

    # 確保輸出目錄存在
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        with sync_playwright() as pw:
            browser_type = getattr(pw, browser_name)
            browser = browser_type.launch(headless=headless)
            page = browser.new_page(viewport={"width": 1280, "height": 720})

            # 導航並計時
            t0 = time.perf_counter()
            response = page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
            result.response_time_ms = (time.perf_counter() - t0) * 1000

            result.status = response.status if response else None
            result.title = page.title()
            result.final_url = page.url

            # 嘗試取得主標題（容錯：若找不到 heading 不中斷）
            try:
                heading_el = page.locator("h1").first
                result.heading = heading_el.inner_text(timeout=5000)
            except Exception:
                result.heading = "(無法取得)"

            # 截圖
            screenshot_path = output_dir / f"homepage_{browser_name}.png"
            page.screenshot(path=screenshot_path, full_page=True)
            result.screenshot = screenshot_path

            browser.close()

        result.success = True
        result.message = "檢查完成"

    except Exception as exc:
        result.message = f"檢查失敗：{exc}"

    return result


# ---------------------------------------------------------------------------
# CLI 入口（保留原始執行方式）
# ---------------------------------------------------------------------------

def main() -> None:
    """命令列入口。"""
    parser = argparse.ArgumentParser(description="網站健康檢查工具")
    parser.add_argument("url", nargs="?", default="https://example.com/",
                        help="要檢查的網址（預設 https://example.com/）")
    parser.add_argument("--browser", choices=["chromium", "firefox", "webkit"],
                        default="chromium", help="瀏覽器類型")
    parser.add_argument("--no-headless", action="store_true",
                        help="以有頭模式啟動瀏覽器")
    parser.add_argument("--timeout", type=int, default=30000,
                        help="導航逾時（毫秒，預設 30000）")
    args = parser.parse_args()

    result = check_website(
        url=args.url,
        browser_name=args.browser,
        headless=not args.no_headless,
        timeout_ms=args.timeout,
    )

    print(f"瀏覽器: {result.browser_name}")
    print(f"HTTP 狀態: {result.status if result.status else '無回應'}")
    print(f"頁面標題: {result.title}")
    print(f"主標題: {result.heading}")
    print(f"回應時間: {result.response_time_ms:.0f} ms")
    print(f"最終 URL: {result.final_url}")
    print(f"截圖: {result.screenshot}")
    verdict = "[OK] 成功" if result.success else "[FAIL] 失敗"
    print(f"結果: {verdict} - {result.message}")


if __name__ == "__main__":
    main()
