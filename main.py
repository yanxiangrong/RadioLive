import json
import os
import sys
import tkinter as tk
import uuid
from tkinter import messagebox, ttk

import vlc

if sys.platform == "win32":
    import ctypes

    ctypes.windll.shcore.SetProcessDpiAwareness(1)


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.radios_map = {}

        self.title("广播直播")
        self.wm_minsize(600, 400)
        self.geometry("900x600")

        # 创建水平方向的 PanedWindow
        paned = tk.PanedWindow(self, orient="horizontal", sashwidth=8)
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

        self.tree.bind("<Double-1>", self.on_tree_double_click)

        # 右侧：上为播放区，下为控制区
        right_frame.rowconfigure(0, weight=0)  # 状态栏，不伸缩
        right_frame.rowconfigure(1, weight=0)  # 播放区
        right_frame.rowconfigure(2, weight=1)  # 控制区
        right_frame.columnconfigure(0, weight=1)

        # 状态栏
        self.status_label = tk.Label(
            right_frame,
            text="没有播放",
            anchor="w",
        )
        self.status_label.grid(row=0, column=0, sticky="ew", padx=5, pady=2)

        # 播放区，Frame用于嵌入VLC
        self.player_area = tk.Frame(right_frame, bg="black", width=400, height=400)
        self.player_area.grid(row=1, column=0, padx=5, pady=(5, 2))

        # 控制按钮区
        control_frame = tk.Frame(right_frame)
        control_frame.grid(row=2, column=0, sticky="n", padx=5, pady=(2, 5))

        play_btn = ttk.Button(control_frame, text="播放", command=self.vlc_play)
        pause_btn = ttk.Button(control_frame, text="暂停", command=self.vlc_pause)
        stop_btn = ttk.Button(control_frame, text="停止", command=self.vlc_stop)
        play_btn.pack(side="left", padx=(0, 5))
        pause_btn.pack(side="left", padx=(0, 5))
        stop_btn.pack(side="left")

        # ----------- VLC 相关 重点 -----------
        self.vlc_instance = vlc.Instance("--audio-visual=visual")
        self.vlc_player = self.vlc_instance.media_player_new()

        self.bind("<Map>", self._on_map)  # 确保窗口创建后再嵌入

        # ----------- 启动后自动加载 -----------
        self.after(100, self.load_radios_from_default)

    def load_radios_tree(self, result):
        """
        加载广播分组与广播到Treeview，并为每个广播分配唯一iid，保存iid和url映射。
        """

        def add_nodes(parent, groups):
            for group in groups:
                node = self.tree.insert(
                    parent, "end", text=group.get("name") or "未命名"
                )
                # 广播
                for radio in group.get("radios", []):
                    iid = str(uuid.uuid4())
                    self.tree.insert(
                        node,
                        "end",
                        iid=iid,
                        text=radio.get("name") or "未命名",
                        values=(radio.get("description") or "",),
                    )
                    self.radios_map[iid] = radio
                # 子分组递归
                for child in group.get("children", []):
                    add_nodes(node, [child])

        self.tree.delete(*self.tree.get_children())
        add_nodes("", result)

    def load_radios_from_default(self):
        default_path = "radios.json"  # 可以改成自己的文件名
        if not os.path.exists(default_path):
            messagebox.showwarning(
                "提示", f"未找到广播列表文件: {default_path}", parent=self
            )
            return
        result = self.load_radios_from_json(default_path)
        self.load_radios_tree(result)

    def load_radios_from_json(self, filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data
        except Exception as e:
            messagebox.showerror("错误", f"读取广播列表JSON失败: {e}", parent=self)
            print(f"读取广播列表JSON失败: {e}")
            return []

    def _on_map(self, event=None):
        """窗口映射后获取window id，把vlc渲染嵌入player_area"""
        win_id = self.player_area.winfo_id()
        if sys.platform.startswith("win"):
            self.vlc_player.set_hwnd(win_id)
        elif sys.platform.startswith("linux"):
            self.vlc_player.set_xwindow(win_id)
        elif sys.platform == "darwin":
            self.vlc_player.set_nsobject(win_id)
        # 只绑定一次
        self.unbind("<Map>")

    def vlc_play(self):
        # 示例：播放本地或网络流
        media = self.vlc_instance.media_new("https://www.radiostream.com/someurl.mp3")
        self.vlc_player.set_media(media)
        self.vlc_player.play()

    def vlc_pause(self):
        self.vlc_player.pause()

    def vlc_stop(self):
        self.vlc_player.stop()

    def on_tree_double_click(self, event):
        # 获取鼠标所在item的iid
        item = self.tree.identify_row(event.y)
        if not item:
            return
        if radio := self.radios_map.get(item):
            # 获取第一个流的URL
            stream_url = radio.get("streams", [{}])[0].get("url")
            self.vlc_player.stop()
            media = self.vlc_instance.media_new(stream_url)
            self.vlc_player.set_media(media)
            self.vlc_player.play()

    def update_status(self, is_playing, name=None):
        if is_playing and name:
            self.status_label.config(text=f"正在播放：{name}")
        else:
            self.status_label.config(text="没有播放")


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
