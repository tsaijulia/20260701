from playwright.sync_api import ScreencastFrame, sync_playwright, Browser,Page

with sync_playwright() as p:
    #開啟瀏覽器
    browser: Browser = p.chromium.launch()
    page:Page = browser.new_page()
    browser.close()
