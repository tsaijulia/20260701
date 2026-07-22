# 匯入 Playwright 相關模組：sync_playwright 用於同步操作，
# Playwright、Browser、Page 為型別提示用的類別
from playwright.sync_api import sync_playwright, Playwright, Browser, Page

def crawl(p: Playwright) -> None:
  """
  使用 Playwright 爬取維基百科頁面的爬蟲函式。
  步驟：開啟瀏覽器 → 前往維基百科 → 搜尋「臺灣」→
        截圖 → 取得標題與摘要 → 返回首頁 → 關閉瀏覽器
  """
  # 啟動 Chromium 瀏覽器（無頭模式，headless=True 為預設）
  browser: Browser = p.chromium.launch()

  # 開啟一個新的瀏覽器分頁
  page: Page = browser.new_page()

  # 前往中文維基百科首頁
  page.goto("https://zh.wikipedia.org")

  # 在搜尋欄位輸入「臺灣」
  page.locator("#searchInput").fill("臺灣")

  # 截圖並儲存為 screenshot.png（截圖搜尋欄已填入關鍵字的畫面）
  page.screenshot(path="screenshot.png")

  # 模擬按下 Enter 鍵執行搜尋
  page.keyboard.press("Enter")

  # 等待頁面網路活動完全停止（確保頁面載入完成）
  page.wait_for_load_state("networkidle")

  # 取得搜尋結果頁面的主標題文字
  first_heading: str = page.locator("#firstHeading").inner_text()
  print(f"搜尋主題: {first_heading}")

  # 取得內文第一段的摘要文字，並只顯示前 100 字元
  content: str = page.locator("#mw-content-text p").first.inner_text()
  print(f"摘要: {content[:100]}")

  # 返回上一頁（維基百科首頁）
  page.go_back()

  # 等待首頁載入完成
  page.wait_for_load_state("networkidle")

  # 印出首頁標題，確認已成功返回
  print(f"返回首頁: {page.title()}")

  # 關閉瀏覽器，釋放資源
  browser.close()


# 使用同步上下文管理器啟動 Playwright，並將實例傳入 crawl 函式
with sync_playwright() as p:
  crawl(p)

  """用opencode，請幫我加上註解，並建立一個markdown檔案，裡面做的程式建議(code review)"""