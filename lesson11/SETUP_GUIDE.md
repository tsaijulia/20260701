# Gradio 維基百科搜尋器 - 完成指南

## 已建立的檔案

1. **lesson11/lesson11_5_gradio.py** - Gradio 介面主程式
2. **lesson11/run_gradio.bat** - Windows 執行腳本
3. **lesson11/test_gradio.py** - 測試腳本
4. **lesson11/README_GRADIO.md** - 詳細說明文件
5. **pyproject.toml** - 已新增 gradio 依賴

## 快速開始（3 個步驟）

### 步驟 1：安裝依賴
```bash
uv sync
```

### 步驟 2：安裝 Playwright 瀏覽器
```bash
uv run playwright install chromium
```

### 步驟 3：啟動 Gradio 介面
```bash
uv run python lesson11/lesson11_5_gradio.py
```

或者直接雙擊 `lesson11/run_gradio.bat`

## 介面功能

- **輸入框**：輸入搜尋關鍵字（預設：臺灣）
- **搜尋按鈕**：點擊開始搜尋
- **搜尋結果分頁**：顯示標題和摘要
- **截圖分頁**：顯示搜尋過程的截圖
- **錯誤訊息**：顯示執行錯誤

## 訪問位址

啟動後，瀏覽器將自動開啟：
- 本機：http://localhost:7860
- 網路：http://你的IP:7860

## 測試安裝

```bash
uv run python lesson11/test_gradio.py
```

## 檔案結構

```
20260701/
├── pyproject.toml              # 已更新，包含 gradio 依賴
├── lesson11/
│   ├── lesson11_5.py           # 原始爬蟲程式碼
│   ├── lesson11_5_gradio.py    # Gradio 介面版本（新建）
│   ├── run_gradio.bat          # Windows 執行腳本（新建）
│   ├── test_gradio.py          # 測試腳本（新建）
│   └── README_GRADIO.md        # 說明文件（新建）
```

## 注意事項

1. 首次執行需要下載 Chromium（約 100MB）
2. 確保網路連線正常
3. 截圖會自動儲存在目前目錄
4. 介面支援 Enter 鍵快速搜尋

## 技術資訊

- **Gradio 版本**：6.20.0
- **Python 版本**：3.12+
- **執行環境**：UV 虛擬環境
- **瀏覽器**：Chromium（Playwright 控制）