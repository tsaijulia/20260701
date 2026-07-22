from playwright.sync_api import sync_playwright,Playwright,Browser,Page

#from lesson9.lesson9_1 import content


def crawl(p:Playwright) -> None:
  browser:Browser = p.chromium.launch(headless=False)#False開啟網頁
  page:Page = browser.new_page()

  page.goto("https://zh.wikipedia.org")
  page.get_by_role("searchbox",name="搜尋維基百科").fill("臺灣")
  page.screenshot(path="screenshot.png")
  page.keyboard.press("Enter")
  page.wait_for_load_state("networkidle")
  first_heading:str = page.locator("#firstHeading").inner_text()
  print(f"搜尋主題:{first_heading}")

  content:str = page.locator("#mw-content-text p").first.inner_text()
  print(f"摘要:{content[:100]}")
  page.go_back()
  page.wait_for_load_state("networkidle")
  print(f"返回首頁:{page.title()}")
  #page.wait_for_timeout(10000)
  browser.close()


with sync_playwright() as p:
  crawl(p)