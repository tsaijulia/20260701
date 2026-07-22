# 維基百科搜尋器 - Gradio 介面

基於 `lesson11_5.py` 的 Playwright 爬蟲功能，建立的 Gradio Web 介面。

## 功能特點

- 🌐 自動搜尋中文維基百科
- 📝 顯示搜尋主題和摘要
- 🖼️ 截圖記錄搜尋過程
- 🎨 美觀的 Gradio 介面
- 📱 響應式設計

## 安裝與執行

### 方法一：使用批次檔案（推薦）

1. 雙擊執行 `run_gradio.bat`
2. 等待安裝完成
3. 瀏覽器將自動開啟 http://localhost:7860

### 方法二：手動執行

```bash
# 1. 安裝依賴
uv sync

# 2. 安裝 Playwright 瀏覽器
uv run playwright install chromium

# 3. 啟動 Gradio 介面
uv run python lesson11/lesson11_5_gradio.py
```

### 方法三：使用 UV 直接執行

```bash
uv run --with gradio python lesson11/lesson11_5_gradio.py
```

## 使用方式

1. 在輸入框中輸入要搜尋的關鍵字（預設：臺灣）
2. 點擊「開始搜尋」按鈕或按 Enter
3. 等待爬蟲執行完成
4. 在下方查看搜尋結果和截圖

## 介面說明

- **搜尋結果分頁**：顯示搜尋主題和摘要
- **截圖分頁**：顯示搜尋過程的截圖
- **錯誤訊息**：顯示執行過程中的錯誤

## 注意事項

- 首次執行需要下載 Chromium 瀏覽器（約 100MB）
- 確保網路連線正常
- 截圖會自動儲存在目前目錄
- 介面預設在 http://localhost:7860 啟動

## 檔案結構

```
lesson11/
├── lesson11_5.py          # 原始爬蟲程式碼
├── lesson11_5_gradio.py   # Gradio 介面版本
├── run_gradio.bat         # Windows 執行腳本
└── README_GRADIO.md       # 本說明文件
```

## 技術細節

- **前端框架**：Gradio 4.x
- **爬蟲工具**：Playwright
- **瀏覽器**：Chromium
- **執行環境**：UV 虛擬環境