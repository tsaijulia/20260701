"""網站健康檢查 App — tkinter 圖形介面。

執行方式:
    python gui.py
"""

from __future__ import annotations

import os
import subprocess
import sys
import threading
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext
from typing import Optional
from urllib.parse import urlparse

import ttkbootstrap as ttk
from ttkbootstrap.constants import *

# ---------------------------------------------------------------------------
# 導入核心檢查函式
# ---------------------------------------------------------------------------
# 確保 lesson10_5.py 所在目錄可被匯入
_SYS_DIR = Path(__file__).resolve().parent
if str(_SYS_DIR) not in sys.path:
    sys.path.insert(0, str(_SYS_DIR))

from lesson10_5 import OUTPUT_DIR, CheckResult, check_website  # noqa: E402


# ===========================================================================
# 色彩常數
# ===========================================================================
COLOR_BG_DARK = "#0d1b2a"       # 深藍背景
COLOR_BG_PANEL = "#1b2838"      # 面板背景
COLOR_BG_CARD = "#243447"       # 卡片背景
COLOR_ACCENT = "#00b4d8"        # 青綠強調
COLOR_ACCENT_HOVER = "#0096c7"  # 青綠 hover
COLOR_SUCCESS = "#06d6a0"       # 成功綠
COLOR_WARNING = "#ffd166"       # 警告黃
COLOR_ERROR = "#ef476f"         # 失敗紅
COLOR_TEXT = "#e0e0e0"          # 主要文字
COLOR_TEXT_DIM = "#8899aa"      # 次要文字


# ===========================================================================
# 工具函式
# ===========================================================================

def _validate_url(url: str) -> str:
    """驗證 URL 格式，回傳錯誤訊息或空字串（表示通過）。"""
    if not url or not url.strip():
        return "請輸入網址，不可為空白。"
    url = url.strip()
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return f"網址必須以 http:// 或 https:// 開頭，\n您輸入的是：{parsed.scheme or '(無)'}://..."
    if not parsed.netloc:
        return "網址缺少域名，請輸入完整的 URL，例如：\nhttps://example.com/"
    return ""


def _validate_timeout(value: str) -> tuple[Optional[int], str]:
    """驗證 timeout 輸入，回傳 (毫秒數, 錯誤訊息)。"""
    value = value.strip()
    if not value:
        return 30_000, ""
    try:
        ms = int(value)
    except ValueError:
        return None, f"Timeout 必須是整數（毫秒），您輸入的是：「{value}」"
    if ms < 1000:
        return None, "Timeout 最小值為 1000 毫秒（1 秒）。\n建議設為 30000（30 秒）。"
    if ms > 300_000:
        return None, "Timeout 最大值為 300000 毫秒（5 分鐘）。\n建議設為 30000（30 秒）。"
    return ms, ""


# ===========================================================================
# 主視窗
# ===========================================================================

class WebsiteCheckerApp:
    """ tkinter 網站健康檢查主視窗。"""

    # -----------------------------------------------------------------------
    # 初始化
    # -----------------------------------------------------------------------
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("網站健康檢查工具")
        self.root.geometry("1200x760")
        self.root.minsize(1000, 600)
        self.root.configure(bg=COLOR_BG_DARK)

        self._is_running = False          # 防止重複執行
        self._result: Optional[CheckResult] = None

        self._setup_styles()
        self._build_ui()

    # -----------------------------------------------------------------------
    # ttk Style
    # -----------------------------------------------------------------------
    def _setup_styles(self) -> None:
        style = ttk.Style("darkly")
        style.configure(".", background=COLOR_BG_DARK, foreground=COLOR_TEXT,
                        font=("Microsoft JhengHei UI", 10))
        style.configure("TFrame", background=COLOR_BG_DARK)
        style.configure("Card.TFrame", background=COLOR_BG_CARD)
        style.configure("TLabel", background=COLOR_BG_DARK, foreground=COLOR_TEXT)
        style.configure("Card.TLabel", background=COLOR_BG_CARD, foreground=COLOR_TEXT)
        style.configure("Title.TLabel", background=COLOR_BG_DARK, foreground=COLOR_ACCENT,
                        font=("Microsoft JhengHei UI", 18, "bold"))
        style.configure("Section.TLabel", background=COLOR_BG_CARD, foreground=COLOR_ACCENT,
                        font=("Microsoft JhengHei UI", 11, "bold"))
        style.configure("Value.TLabel", background=COLOR_BG_CARD, foreground=COLOR_TEXT,
                        font=("Microsoft JhengHei UI", 10))
        style.configure("Status.TLabel", background=COLOR_BG_CARD,
                        font=("Microsoft JhengHei UI", 12, "bold"))
        style.configure("Accent.TButton", font=("Microsoft JhengHei UI", 11, "bold"))
        style.configure("TCombobox", fieldbackground=COLOR_BG_CARD,
                        background=COLOR_BG_CARD, foreground=COLOR_TEXT)
        style.configure("TEntry", fieldbackground=COLOR_BG_CARD, foreground=COLOR_TEXT)
        style.configure("TCheckbutton", background=COLOR_BG_CARD, foreground=COLOR_TEXT)
        style.configure("TNotebook", background=COLOR_BG_DARK)
        style.configure("TNotebook.Tab", font=("Microsoft JhengHei UI", 10))

    # -----------------------------------------------------------------------
    # 建構 UI
    # -----------------------------------------------------------------------
    def _build_ui(self) -> None:
        # ---- 標題列 ----
        header = ttk.Frame(self.root)
        header.pack(fill=X, padx=20, pady=(15, 5))
        ttk.Label(header, text="🌐 網站健康檢查工具",
                  style="Title.TLabel").pack(side=LEFT)

        # ---- 主容器（左右雙欄） ----
        body = ttk.Frame(self.root)
        body.pack(fill=BOTH, expand=True, padx=20, pady=5)
        body.columnconfigure(0, weight=2)   # 左側
        body.columnconfigure(1, weight=3)   # 右側
        body.rowconfigure(0, weight=1)

        self._build_left_panel(body)
        self._build_right_panel(body)

        # ---- 底部區域 ----
        self._build_bottom_bar()

    # ------------------------------------------------------------------
    # 左側面板：輸入控制
    # ------------------------------------------------------------------
    def _build_left_panel(self, parent: ttk.Frame) -> None:
        left = ttk.Frame(parent)
        left.grid(row=0, column=0, sticky=NSEW, padx=(0, 10))

        # -- 卡片 --
        card = tk.Frame(left, bg=COLOR_BG_CARD, highlightbackground=COLOR_ACCENT,
                        highlightthickness=1, bd=0)
        card.pack(fill=BOTH, expand=True)

        inner = ttk.Frame(card)
        inner.configure(style="Card.TFrame")
        inner.pack(fill=BOTH, expand=True, padx=20, pady=20)

        # 標題
        ttk.Label(inner, text="檢查設定", style="Section.TLabel").pack(anchor=W)
        ttk.Frame(inner, height=10, style="Card.TFrame").pack()

        # URL
        ttk.Label(inner, text="網址 (URL)", style="Card.TLabel").pack(anchor=W)
        self._url_var = tk.StringVar(value="https://example.com/")
        url_entry = ttk.Entry(inner, textvariable=self._url_var, width=40)
        url_entry.pack(fill=X, pady=(2, 10))

        # 瀏覽器
        ttk.Label(inner, text="瀏覽器", style="Card.TLabel").pack(anchor=W)
        self._browser_var = tk.StringVar(value="chromium")
        browser_frame = ttk.Frame(inner, style="Card.TFrame")
        browser_frame.pack(fill=X, pady=(2, 10))
        for name in ("chromium", "firefox", "webkit"):
            ttk.Radiobutton(browser_frame, text=name.capitalize(),
                             variable=self._browser_var, value=name,
                             style="Card.TRadiobutton").pack(side=LEFT, padx=(0, 12))

        # Headless
        self._headless_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(inner, text="Headless 模式（無視窗）",
                         variable=self._headless_var,
                         style="Card.TCheckbutton").pack(anchor=W, pady=(0, 10))

        # Timeout
        ttk.Label(inner, text="Timeout（毫秒）", style="Card.TLabel").pack(anchor=W)
        self._timeout_var = tk.StringVar(value="30000")
        ttk.Entry(inner, textvariable=self._timeout_var, width=20).pack(
            fill=X, pady=(2, 10))

        # 提示
        ttk.Label(inner, text="提示：30000 = 30 秒，最小 1000，最大 300000",
                  style="Card.TLabel", foreground=COLOR_TEXT_DIM).pack(anchor=W)

        ttk.Frame(inner, height=15, style="Card.TFrame").pack()

        # 開始檢查按鈕
        self._start_btn = ttk.Button(inner, text="▶  開始檢查",
                                      bootstyle="success",
                                      command=self._on_start)
        self._start_btn.pack(fill=X, ipady=6)

        ttk.Frame(inner, height=10, style="Card.TFrame").pack()

        # 進度條
        self._progress_var = tk.DoubleVar(value=0)
        self._progress = ttk.Progressbar(inner, variable=self._progress_var,
                                          maximum=100, bootstyle="info-striped")
        self._progress.pack(fill=X)

    # ------------------------------------------------------------------
    # 右側面板：結果顯示
    # ------------------------------------------------------------------
    def _build_right_panel(self, parent: ttk.Frame) -> None:
        right = ttk.Frame(parent)
        right.grid(row=0, column=1, sticky=NSEW, padx=(10, 0))

        # -- 結果卡片 --
        card = tk.Frame(right, bg=COLOR_BG_CARD, highlightbackground=COLOR_ACCENT,
                        highlightthickness=1, bd=0)
        card.pack(fill=BOTH, expand=True)

        inner = ttk.Frame(card)
        inner.configure(style="Card.TFrame")
        inner.pack(fill=BOTH, expand=True, padx=20, pady=20)

        ttk.Label(inner, text="檢查結果", style="Section.TLabel").pack(anchor=W)
        ttk.Frame(inner, height=8, style="Card.TFrame").pack()

        # 狀態標籤
        self._status_label = ttk.Label(inner, text="等待檢查…",
                                        style="Status.TLabel",
                                        foreground=COLOR_TEXT_DIM)
        self._status_label.pack(anchor=W, pady=(0, 10))

        # 結果表格
        result_grid = ttk.Frame(inner, style="Card.TFrame")
        result_grid.pack(fill=X)
        for i in range(6):
            result_grid.rowconfigure(i, pad=4)
        result_grid.columnconfigure(1, weight=1)

        labels = ["HTTP 狀態", "回應時間", "頁面標題", "主標題", "最終 URL", "截圖"]
        self._result_vars: dict[str, tk.StringVar] = {}
        for i, name in enumerate(labels):
            ttk.Label(result_grid, text=f"{name}：", style="Card.TLabel",
                      foreground=COLOR_TEXT_DIM, width=10).grid(row=i, column=0, sticky=W)
            var = tk.StringVar(value="—")
            self._result_vars[name] = var
            ttk.Label(result_grid, textvariable=var,
                      style="Value.TLabel", wraplength=350).grid(
                row=i, column=1, sticky=W, padx=(8, 0))

        ttk.Frame(inner, height=10, style="Card.TFrame").pack()

        # 截圖預覽區
        preview_label = ttk.Label(inner, text="截圖預覽", style="Section.TLabel")
        preview_label.pack(anchor=W)

        self._preview_frame = tk.Frame(inner, bg=COLOR_BG_CARD,
                                       highlightbackground=COLOR_TEXT_DIM,
                                       highlightthickness=1, height=220)
        self._preview_frame.pack(fill=X, pady=(5, 0))
        self._preview_frame.pack_propagate(False)

        self._preview_label = ttk.Label(self._preview_frame, text="尚無截圖",
                                         background=COLOR_BG_CARD,
                                         foreground=COLOR_TEXT_DIM,
                                         font=("Microsoft JhengHei UI", 10))
        self._preview_label.pack(expand=True)

        self._preview_image: Optional[tk.PhotoImage] = None  # 防止 GC

    # ------------------------------------------------------------------
    # 底部工具列
    # ------------------------------------------------------------------
    def _build_bottom_bar(self) -> None:
        bottom = ttk.Frame(self.root)
        bottom.pack(fill=BOTH, expand=False, padx=20, pady=(5, 15))

        # -- 執行日誌（可滾動） --
        log_frame = tk.Frame(bottom, bg=COLOR_BG_CARD,
                             highlightbackground=COLOR_ACCENT,
                             highlightthickness=1)
        log_frame.pack(fill=BOTH, expand=True, pady=(0, 8))

        self._log = scrolledtext.ScrolledText(
            log_frame, height=6, bg=COLOR_BG_CARD, fg=COLOR_TEXT,
            insertbackground=COLOR_TEXT, font=("Consolas", 9),
            relief=FLAT, wrap=WORD, state=DISABLED,
        )
        self._log.pack(fill=BOTH, expand=True, padx=4, pady=4)

        # -- 按鈕列 --
        btn_row = ttk.Frame(bottom)
        btn_row.pack(fill=X)

        self._open_folder_btn = ttk.Button(
            btn_row, text="📂  開啟輸出資料夾", bootstyle="info",
            command=self._open_output_folder)
        self._open_folder_btn.pack(side=LEFT, padx=(0, 8), ipady=4)

        self._clear_btn = ttk.Button(
            btn_row, text="🗑  清除結果", bootstyle="danger-outline",
            command=self._clear_results)
        self._clear_btn.pack(side=LEFT, ipady=4)

    # ------------------------------------------------------------------
    # 日誌
    # ------------------------------------------------------------------
    def _log_msg(self, msg: str) -> None:
        """安全地將訊息附加到日誌（可在任何執行緒呼叫）。"""
        ts = datetime.now().strftime("%H:%M:%S")
        line = f"[{ts}] {msg}\n"

        def _append():
            self._log.configure(state=NORMAL)
            self._log.insert(END, line)
            self._log.see(END)
            self._log.configure(state=DISABLED)

        # 確保在主執行緒更新 UI
        self.root.after(0, _append)

    # ------------------------------------------------------------------
    # 檢查流程
    # ------------------------------------------------------------------
    def _on_start(self) -> None:
        """按鈕點擊事件：啟動背景執行緒進行檢查。"""
        if self._is_running:
            messagebox.showwarning("提示", "目前已有檢查進行中，請稍候。")
            return

        # 驗證 URL
        url = self._url_var.get().strip()
        err = _validate_url(url)
        if err:
            messagebox.showerror("網址格式錯誤", err)
            return

        # 驗證 Timeout
        timeout_ms, err = _validate_timeout(self._timeout_var.get())
        if err:
            messagebox.showerror("Timeout 設定錯誤", err)
            return

        browser_name = self._browser_var.get()
        headless = self._headless_var.get()

        self._is_running = True
        self._start_btn.configure(state=DISABLED)
        self._progress_var.set(0)

        # 重置結果面板
        self._status_label.configure(text="檢查中…", foreground=COLOR_WARNING)
        for var in self._result_vars.values():
            var.set("…")
        self._log_msg(f"開始檢查 {url}（{browser_name}）")

        # 啟動背景執行緒
        t = threading.Thread(
            target=self._worker,
            args=(url, browser_name, headless, timeout_ms),
            daemon=True,
        )
        t.start()

    def _worker(self, url: str, browser_name: str, headless: bool,
                timeout_ms: int) -> None:
        """背景執行緒：執行 Playwright 檢查。"""
        self._log_msg("Playwright 啟動中…")
        self.root.after(0, lambda: self._progress_var.set(20))

        result = check_website(
            url=url,
            browser_name=browser_name,
            headless=headless,
            timeout_ms=timeout_ms,
        )

        self.root.after(0, lambda: self._progress_var.set(90))
        self._result = result

        # 回到主執行緒更新 UI
        self.root.after(0, self._on_result, result)

    def _on_result(self, result: CheckResult) -> None:
        """在主執行緒更新結果面板。"""
        # HTTP 狀態
        status_text = str(result.status) if result.status else "無回應"
        self._result_vars["HTTP 狀態"].set(status_text)

        # 回應時間
        self._result_vars["回應時間"].set(f"{result.response_time_ms:.0f} ms")

        # 頁面標題
        self._result_vars["頁面標題"].set(result.title or "—")

        # 主標題
        self._result_vars["主標題"].set(result.heading or "—")

        # 最終 URL
        self._result_vars["最終 URL"].set(result.final_url or "—")

        # 截圖路徑
        self._result_vars["截圖"].set(str(result.screenshot) if result.screenshot else "—")

        # 狀態標籤
        if result.success:
            if result.status and 200 <= result.status < 400:
                self._status_label.configure(text="✓ 檢查成功", foreground=COLOR_SUCCESS)
            else:
                self._status_label.configure(text="⚠ 回應異常", foreground=COLOR_WARNING)
            self._log_msg(f"完成 — HTTP {result.status}, 耗時 {result.response_time_ms:.0f}ms")
        else:
            self._status_label.configure(text="✗ 檢查失敗", foreground=COLOR_ERROR)
            self._log_msg(f"失敗 — {result.message}")

        # 截圖預覽
        if result.screenshot and result.screenshot.exists():
            self._show_preview(result.screenshot)
        else:
            self._preview_label.configure(text="無截圖")

        self._progress_var.set(100)
        self._is_running = False
        self._start_btn.configure(state=NORMAL)

    def _show_preview(self, path: Path) -> None:
        """在右側面板顯示截圖縮圖。"""
        try:
            img = tk.PhotoImage(file=str(path))
            # 縮放（tk.PhotoImage 只支援整數倍縮放）
            w, h = img.width(), img.height()
            # 目標寬度約 350px
            ratio = max(1, w // 350)
            img = img.subsample(ratio, ratio)
            self._preview_image = img
            self._preview_label.configure(image=img, text="")
        except Exception:
            self._preview_label.configure(text="無法載入截圖預覽")

    # ------------------------------------------------------------------
    # 工具操作
    # ------------------------------------------------------------------
    def _open_output_folder(self) -> None:
        """用系統檔案總管開啟 output 資料夾。"""
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        if sys.platform == "win32":
            os.startfile(str(OUTPUT_DIR))
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(OUTPUT_DIR)])
        else:
            subprocess.Popen(["xdg-open", str(OUTPUT_DIR)])
        self._log_msg(f"已開啟輸出資料夾：{OUTPUT_DIR}")

    def _clear_results(self) -> None:
        """清除所有結果與日誌。"""
        self._status_label.configure(text="等待檢查…", foreground=COLOR_TEXT_DIM)
        for var in self._result_vars.values():
            var.set("—")
        self._preview_label.configure(text="尚無截圖", image="")
        self._preview_image = None
        self._progress_var.set(0)
        self._log.configure(state=NORMAL)
        self._log.delete("1.0", END)
        self._log.configure(state=DISABLED)
        self._result = None
        self._log_msg("已清除所有結果")


# ===========================================================================
# 程式進入點
# ===========================================================================

def main() -> None:
    root = tk.Tk()
    root.style = ttk.Style("darkly")  # ttkbootstrap 主題
    WebsiteCheckerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
