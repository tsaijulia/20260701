import random
import tkinter as tk
from tkinter import messagebox

class GuessNumberGame:
    def __init__(self, root):
        self.root = root
        self.root.title("猜數字遊戲")
        self.root.geometry("400x350")
        self.root.resizable(False, False)

        self.target = random.randint(1, 100)
        self.low = 1
        self.high = 100
        self.attempts = 0

        # 標題
        tk.Label(root, text="猜數字遊戲", font=("Microsoft JhengHei", 20, "bold")).pack(pady=10)

        # 範圍顯示
        self.range_label = tk.Label(root, text=f"請猜一個 {self.low} ~ {self.high} 之間的數字", font=("Microsoft JhengHei", 12))
        self.range_label.pack(pady=5)

        # 輸入框
        self.entry = tk.Entry(root, font=("Microsoft JhengHei", 14), justify="center", width=10)
        self.entry.pack(pady=10)
        self.entry.bind("<Return>", lambda event: self.check_guess())
        self.entry.focus()

        # 猜測按鈕
        tk.Button(root, text="猜！", font=("Microsoft JhengHei", 12), width=10, command=self.check_guess).pack(pady=5)

        # 結果顯示
        self.result_label = tk.Label(root, text="", font=("Microsoft JhengHei", 14))
        self.result_label.pack(pady=5)

        # 猜測次數
        self.attempts_label = tk.Label(root, text="已猜次數：0", font=("Microsoft JhengHei", 11))
        self.attempts_label.pack(pady=5)

        # 重新開始按鈕
        tk.Button(root, text="重新開始", font=("Microsoft JhengHei", 11), command=self.restart).pack(pady=10)

    def check_guess(self):
        # 取得輸入並進行錯誤處理
        try:
            guess = int(self.entry.get())
        except ValueError:
            messagebox.showwarning("輸入錯誤", "請輸入有效的整數！")
            return

        # 範圍檢查
        if guess < self.low or guess > self.high:
            messagebox.showwarning("超出範圍", f"請輸入 {self.low} ~ {self.high} 之間的數字！")
            return

        # 累加猜測次數
        self.attempts += 1
        self.attempts_label.config(text=f"已猜次數：{self.attempts}")

        # 判斷猜測結果
        if guess == self.target:
            self.result_label.config(text=f"恭喜你猜中了！答案是 {self.target}", fg="green")
            messagebox.showinfo("恭喜", f"你猜中了！答案就是 {self.target}\n你總共猜了 {self.attempts} 次")
            self.entry.config(state="disabled")
        elif guess < self.target:
            self.low = guess + 1
            self.result_label.config(text="再大一點！", fg="blue")
            self.range_label.config(text=f"請猜一個 {self.low} ~ {self.high} 之間的數字")
        else:
            self.high = guess - 1
            self.result_label.config(text="再小一點！", fg="blue")
            self.range_label.config(text=f"請猜一個 {self.low} ~ {self.high} 之間的數字")

        self.entry.delete(0, tk.END)

    def restart(self):
        self.target = random.randint(1, 100)
        self.low = 1
        self.high = 100
        self.attempts = 0
        self.entry.config(state="normal")
        self.entry.delete(0, tk.END)
        self.result_label.config(text="")
        self.attempts_label.config(text="已猜次數：0")
        self.range_label.config(text=f"請猜一個 {self.low} ~ {self.high} 之間的數字")

if __name__ == "__main__":
    root = tk.Tk()
    app = GuessNumberGame(root)
    root.mainloop()
