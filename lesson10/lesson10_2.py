import asyncio
import time

async def download_file_async(file_name):
    """模擬下載檔案（非同步版本）"""
    print(f"開始下載 {file_name}...")
    await asyncio.sleep(2)  # 關鍵差異：使用 await，讓出控制權
    print(f"✅ {file_name} 下載完成")
    return f"{file_name}_data"

# 使用 asyncio：同時下載多個檔案
async def main_async():
    start = time.time()

    # 同時啟動 3 個下載任務
    results = await asyncio.gather(
        download_file_async("檔案A.pdf"),
        download_file_async("檔案B.pdf"),
        download_file_async("檔案C.pdf")
    )

    end = time.time() #結束時間
    print(f"\n總耗時: {end - start:.2f} 秒")

# 執行（在 Jupyter 中直接 await main_async()）
asyncio.run(main_async())
