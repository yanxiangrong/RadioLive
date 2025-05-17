import json
import os
import sys
import tkinter as tk
from tkinter import messagebox, ttk

if sys.platform == "win32":
    import ctypes

    ctypes.windll.shcore.SetProcessDpiAwareness(1)


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("广播直播")
        self.wm_minsize(600, 400)
        self.geometry("900x600")

        # 创建水平方向的 PanedWindow
        paned = tk.PanedWindow(self, orient="horizontal")
        paned.pack(fill="both", expand=True)

        left_frame = tk.Frame(paned, padx=5, pady=5)
        right_frame = tk.Frame(paned)

        # 添加到 PanedWindow（顺序很重要）
        paned.add(left_frame, minsize=200, width=280)  # 可设最小宽度
        paned.add(right_frame, minsize=200)

        # 左侧：广播列表
        left_frame.columnconfigure(0, weight=1)
        left_frame.columnconfigure(1, weight=0)  # 保证右侧竖向滚动条为最小宽度
        left_frame.rowconfigure(0, weight=1)
        left_frame.rowconfigure(1, weight=0)  # 横向滚动条也是

        self.tree = ttk.Treeview(left_frame, columns=["desc"])
        self.tree.grid(row=0, column=0, sticky="nsew")

        self.tree.heading("#0", text="广播分类/节目", anchor="w")
        self.tree.heading("desc", text="描述", anchor="w")

        self.tree.column("#0", width=260, minwidth=200, stretch=False)  # 广播分类/节目
        self.tree.column("desc", width=2000, minwidth=200, stretch=False)  # 描述

        # 树形控件的列宽
        tree_scrollbar = ttk.Scrollbar(
            left_frame, orient="vertical", command=self.tree.yview
        )
        tree_scrollbar.grid(row=0, column=1, sticky="ns")
        tree_scroll_x = ttk.Scrollbar(
            left_frame, orient="horizontal", command=self.tree.xview
        )
        tree_scroll_x.grid(row=1, column=0, sticky="ew")

        self.tree.configure(
            yscrollcommand=tree_scrollbar.set, xscrollcommand=tree_scroll_x.set
        )

        # 右侧：上为播放区，下为控制区
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

        # self.update_idletasks()
        # self.geometry(f"{self.winfo_reqwidth()}x{self.winfo_reqheight()}")

        # ----------- 启动后自动加载 -----------
        self.after(100, self.load_radios_from_default)

    def load_radios_tree(self, result):
        def add_nodes(parent, groups):
            for group in groups:
                node = self.tree.insert(
                    parent, "end", text=group.get("name") or "未命名"
                )
                for radio in group.get("radios", []):
                    self.tree.insert(
                        node,
                        "end",
                        text=radio.get("name") or "未命名",
                        values=(radio.get("description") or "",),
                    )
                for child in group.get("children", []):
                    add_nodes(node, [child])

        self.tree.delete(*self.tree.get_children())
        add_nodes("", result)

    def load_radios_from_default(self):
        default_path = "radios.json"  # 可以改成自己的文件名
        if not os.path.exists(default_path):
            messagebox.showwarning("提示", f"未找到广播列表文件: {default_path}")
            return
        result = load_radios_from_json(default_path)
        self.load_radios_tree(result)


def load_radios_from_json(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"读取广播列表JSON失败: {e}")
        return []


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
