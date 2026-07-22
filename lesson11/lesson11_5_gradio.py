import gradio as gr
from datetime import datetime
from playwright.sync_api import sync_playwright, Playwright, Browser, Page
import os
import glob
import time


def launch_browser(p: Playwright) -> Browser:
    """啟動 Chromium 瀏覽器實例"""
    return p.chromium.launch()


def search_wikipedia(page: Page, keyword: str) -> str:
    """在維基百科搜尋指定關鍵字，返回截圖路徑"""
    page.goto("https://zh.wikipedia.org")
    page.locator("#searchInput").fill(keyword)
    screenshot_path = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    page.screenshot(path=screenshot_path)
    page.keyboard.press("Enter")
    page.wait_for_load_state("networkidle")
    return screenshot_path


def get_search_result(page: Page) -> dict:
    """擷取搜尋結果頁面的標題與摘要"""
    heading: str = page.locator("#firstHeading").inner_text()
    elements = page.locator("#mw-content-text p")
    content: str = elements.first.inner_text() if elements.count() > 0 else ""
    return {"heading": heading, "content": content[:200]}


def crawl_wikipedia(keyword: str) -> tuple:
    """爬蟲主流程：啟動瀏覽器、搜尋、擷取結果、返回首頁"""
    screenshot_paths = []
    result_text = ""
    error_msg = ""
    
    try:
        with sync_playwright() as p:
            browser: Browser = launch_browser(p)
            try:
                page: Page = browser.new_page()
                screenshot1 = search_wikipedia(page, keyword)
                screenshot_paths.append(screenshot1)
                
                result: dict = get_search_result(page)
                result_text = f"搜尋主題: {result['heading']}\n摘要: {result['content']}"
                
                page.go_back()
                page.wait_for_load_state("networkidle")
                
                # 截圖返回首頁
                screenshot2 = f"homepage_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                page.screenshot(path=screenshot2)
                screenshot_paths.append(screenshot2)
                
            except Exception as e:
                error_msg = f"爬蟲執行失敗: {e}"
            finally:
                browser.close()
    except Exception as e:
        error_msg = f"Playwright 啟動失敗: {e}"
    
    return result_text, screenshot_paths, error_msg


def clean_old_screenshots():
    """清理舊的截圖文件"""
    for f in glob.glob("screenshot_*.png"):
        try:
            os.remove(f)
        except:
            pass
    for f in glob.glob("homepage_*.png"):
        try:
            os.remove(f)
        except:
            pass


def search_action(keyword: str) -> tuple:
    """搜尋按鈕的回調函數"""
    if not keyword.strip():
        return "請輸入搜尋關鍵字", [], ""
    
    clean_old_screenshots()
    result_text, screenshot_paths, error_msg = crawl_wikipedia(keyword)
    
    # 只返回存在的截圖
    valid_screenshots = [s for s in screenshot_paths if os.path.exists(s)]
    
    return result_text, valid_screenshots, error_msg


# 建立 Gradio 介面
with gr.Blocks(title="維基百科搜尋器") as demo:
    gr.Markdown(
        """
        # 🌐 維基百科搜尋器
        
        輸入關鍵字，自動搜尋維基百科並顯示結果
        """
    )
    
    with gr.Row():
        with gr.Column(scale=2):
            keyword_input = gr.Textbox(
                label="搜尋關鍵字",
                placeholder="請輸入要搜尋的關鍵字，例如：臺灣",
                value="臺灣"
            )
            
            search_btn = gr.Button(
                "🔍 開始搜尋",
                variant="primary",
                size="lg"
            )
        
        with gr.Column(scale=3):
            with gr.Tabs():
                with gr.TabItem("📝 搜尋結果"):
                    result_output = gr.Textbox(
                        label="搜尋結果",
                        lines=5,
                        interactive=False
                    )
                
                with gr.TabItem("🖼️ 截圖"):
                    gallery = gr.Gallery(
                        label="截圖預覽",
                        columns=2,
                        height=400
                    )
    
    with gr.Row():
        error_output = gr.Textbox(
            label="錯誤訊息",
            lines=2,
            interactive=False,
            visible=True
        )
    
    gr.Markdown(
        """
        ---
        ### 使用說明
        1. 在輸入框中輸入要搜尋的關鍵字
        2. 點擊「開始搜尋」按鈕
        3. 等待爬蟲執行完成
        4. 在下方查看搜尋結果和截圖
        
        ### 功能特點
        - 自動搜尋中文維基百科
        - 顯示搜尋主題和摘要
        - 截圖記錄搜尋過程
        - 支援多種關鍵字搜尋
        """
    )
    
    # 設定事件處理
    search_btn.click(
        fn=search_action,
        inputs=[keyword_input],
        outputs=[result_output, gallery, error_output]
    )
    
    keyword_input.submit(
        fn=search_action,
        inputs=[keyword_input],
        outputs=[result_output, gallery, error_output]
    )


if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        theme=gr.themes.Soft(),
        css="""
        .container { max-width: 800px; margin: auto; }
        .header { text-align: center; margin-bottom: 20px; }
        .result-box { 
            background-color: #f0f8ff; 
            padding: 15px; 
            border-radius: 8px;
            border: 1px solid #add8e6;
        }
        """
    )