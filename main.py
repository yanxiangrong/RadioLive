import sys
import tkinter as tk
from tkinter import ttk

if sys.platform == "win32":
    import ctypes

    ctypes.windll.shcore.SetProcessDpiAwareness(1)


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("广播直播")
        self.wm_minsize(400, 300)

        # 1. 顶层分为左右两栏
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=3)
        self.rowconfigure(0, weight=1)

        # 左侧：广播列表
        left_frame = tk.Frame(self)
        left_frame.grid(row=0, column=0, sticky="nsew")
        left_frame.rowconfigure(0, weight=1)
        left_frame.columnconfigure(0, weight=1)
        self.listbox = tk.Listbox(left_frame)
        self.listbox.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # 右侧：上为播放区，下为控制区
        right_frame = tk.Frame(self)
        right_frame.grid(row=0, column=1, sticky="nsew")
        right_frame.rowconfigure(0, weight=5)
        right_frame.rowconfigure(1, weight=1)
        right_frame.columnconfigure(0, weight=1)

        # 播放区 Canvas/placeholder
        self.player_area = tk.Label(
            right_frame, text="VLC播放器窗口", bg="black", fg="white"
        )
        self.player_area.grid(row=0, column=0, sticky="nsew", padx=5, pady=(5, 2))

        # 控制按钮区
        control_frame = tk.Frame(right_frame)
        control_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=(2, 5))

        play_btn = ttk.Button(control_frame, text="播放")
        pause_btn = ttk.Button(control_frame, text="暂停")
        stop_btn = ttk.Button(control_frame, text="停止")
        play_btn.pack(side="left", padx=(0, 5))
        pause_btn.pack(side="left", padx=(0, 5))
        stop_btn.pack(side="left")

        self.update_idletasks()
        self.geometry(f"{self.winfo_reqwidth()}x{self.winfo_reqheight()}")


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
