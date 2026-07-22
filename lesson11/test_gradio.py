"""測試 Gradio 介面是否正常載入"""
import sys
sys.path.insert(0, 'lesson11')

def test_gradio_import():
    """測試 Gradio 模組導入"""
    try:
        import gradio as gr
        print(f"[OK] Gradio 版本: {gr.__version__}")
        return True
    except ImportError as e:
        print(f"[FAIL] Gradio 導入失敗: {e}")
        return False

def test_playwright_import():
    """測試 Playwright 模組導入"""
    try:
        from playwright.sync_api import sync_playwright
        print("[OK] Playwright 導入成功")
        return True
    except ImportError as e:
        print(f"[FAIL] Playwright 導入失敗: {e}")
        return False

def test_gradio_interface():
    """測試 Gradio 介面載入"""
    try:
        from lesson11_5_gradio import demo
        print("[OK] Gradio 介面載入成功")
        return True
    except Exception as e:
        print(f"[FAIL] Gradio 介面載入失敗: {e}")
        return False

def main():
    print("=== Gradio 介面測試 ===\n")
    
    tests = [
        ("Gradio 模組", test_gradio_import),
        ("Playwright 模組", test_playwright_import),
        ("Gradio 介面", test_gradio_interface),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"測試 {name}...")
        result = test_func()
        results.append((name, result))
        print()
    
    print("=== 測試結果 ===")
    all_passed = True
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{name}: {status}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n所有測試通過！可以執行 Gradio 介面。")
        print("執行指令: uv run python lesson11/lesson11_5_gradio.py")
    else:
        print("\n部分測試失敗，請檢查安裝。")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)