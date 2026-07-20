# 20260701
上課用

## lesson10 — 網站健康檢查工具

使用 Playwright 開啟真實網頁，檢查 HTTP 狀態、頁面標題並截圖。
提供 CLI 與 tkinter GUI 兩種操作方式。

### 檔案結構

| 檔案 | 說明 |
|------|------|
| `lesson10_5.py` | 核心模組 — `check_website()` 函式，CLI / GUI 共用 |
| `gui.py` | tkinter 圖形介面入口 |
| `test_core.py` | 核心函式的基本測試 |
| `output/` | 截圖輸出目錄 |

### 安裝

```bash
uv sync
```

### 執行

**CLI 模式：**

```bash
uv run python lesson10/lesson10_5.py
uv run python lesson10/lesson10_5.py https://tw.yahoo.com --browser firefox
uv run python lesson10/lesson10_5.py --timeout 60000 --no-headless
```

**GUI 模式：**

```bash
uv run python lesson10/gui.py
```

### 測試

```bash
uv run pytest lesson10/test_core.py -v
```
