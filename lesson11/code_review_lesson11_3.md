# Code Review: lesson11_3.py — 維基百科爬蟲

> 原始檔案：`lesson11/lesson11_3.py`

---

## 功能概述

使用 Playwright 以同步方式操控 Chromium 瀏覽器，前往中文維基百科搜尋「臺灣」，取得搜尋結果的標題與摘要，最後返回首頁。

---

## 程式建議 (Code Review)

### 1. 加入錯誤處理（Exception Handling）

目前程式完全沒有 try-except，若網站改版、元素找不到或網路中斷，程式會直接崩潰。

**建議：** 針對關鍵操作加入 try-except，尤其是 `page.goto()`、`page.locator().inner_text()` 等可能失敗的步驟。

```python
try:
    page.goto("https://zh.wikipedia.org", timeout=10000)
except Exception as e:
    print(f"頁面載入失敗: {e}")
    return
```

---

### 2. 補充 `timeout` 參數

`wait_for_load_state("networkidle")` 沒有設定超時時間，若網路異常會無限等待。

**建議：** 加入 `timeout` 參數避免永遠卡住。

```python
page.wait_for_load_state("networkidle", timeout=30000)  # 最多等 30 秒
```

---

### 3. 使用 `with` 語法管理瀏覽器

目前在函式內手動呼叫 `browser.close()`，若中途發生例外，瀏覽器不會被正確關閉。

**建議：** 改用 `with` 語句或 `try-finally` 確保資源釋放。

```python
def crawl(p: Playwright) -> None:
    browser = p.chromium.launch()
    try:
        page = browser.new_page()
        # ... 操作 ...
    finally:
        browser.close()
```

---

### 4. 截圖時機與命名

`screenshot.png` 每次執行都會被覆蓋，若需要保留歷史紀錄會找不到。

**建議：** 使用帶有時間戳的檔名。

```python
import datetime
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
page.screenshot(path=f"screenshot_{timestamp}.png")
```

---

### 5. 硬編碼的 URL 與關鍵字

搜尋關鍵字 `"臺灣"` 和網址 `"https://zh.wikipedia.org"` 直接寫死在程式中。

**建議：** 把它們抽出為函式參數或常數，方便重用與維護。

```python
WIKI_URL = "https://zh.wikipedia.org"
SEARCH_TERM = "臺灣"

def crawl(p: Playwright, url: str = WIKI_URL, keyword: str = SEARCH_TERM) -> None:
    ...
```

---

### 6. 補充回傳值

目前 `crawl()` 回傳 `None`，呼叫端無法得知爬取結果。

**建議：** 可考慮回傳一個 dict，方便後續處理。

```python
def crawl(p: Playwright, ...) -> dict:
    ...
    return {"heading": first_heading, "summary": content[:100]}
```

---

### 7. `content[:100]` 可能截斷不完整

直接取前 100 字元可能在中文字中間截斷。

**建議：** 可改用 `textwrap.shorten()` 或自行判斷字數上限。

---

### 8. 缺少 docstring 與類型提示的一致性

部分變數有型別提示（如 `browser: Browser`），但函式參數 `p` 和回傳值已有提示，整體算一致。不過 docstring 缺少參數說明。

**建議：** 補充 docstring 中的 `Args` 和 `Returns` 區段。

```python
def crawl(p: Playwright) -> None:
    """
    爬取維基百科「臺灣」條目並截圖。

    Args:
        p: Playwright 同步實例
    """
```

---

### 9. 加入 logging 取代 print

在正式專案中，建議使用 `logging` 模組取代 `print`，方便調整輸出等級。

```python
import logging
logger = logging.getLogger(__name__)
logger.info(f"搜尋主題: {first_heading}")
```

---

## 總結

| 分類 | 狀態 |
|------|------|
| 功能正確性 | ✅ 可正常執行 |
| 錯誤處理 | ❌ 缺乏，建議加入 |
| 資源管理 | ⚠️ 建議改用 try-finally |
| 可維護性 | ⚠️ 硬編碼，建議抽出常數 |
| 可重用性 | ⚠️ 可加入參數與回傳值 |

整體而言，作為教學範例程式碼結構清晰、流程明確；若要投入正式使用，建議補強錯誤處理與資源管理。
