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
        self.current_radio_name = tk.StringVar(value="未播放")

        self.title("广播直播")
        self.wm_minsize(600, 400)
        self.geometry("900x600")

        # 创建水平方向的 PanedWindow
        paned = tk.PanedWindow(self, orient="horizontal", sashwidth=4)
        paned.pack(fill="both", expand=True)

        left_frame = tk.Frame(paned, padx=5, pady=5)
        right_frame = tk.Frame(paned)

        # 添加到 PanedWindow（顺序很重要）
        paned.add(right_frame, minsize=200)
        paned.add(left_frame, minsize=200)  # 可设最小宽度

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
        # 播放区，Frame用于嵌入VLC
        self.player_area = tk.Frame(right_frame, bg="black", width=320, height=320)
        self.player_area.pack(padx=5, pady=(5, 2))
        right_frame.bind("<Configure>", self.keep_player_area_square)

        # 广播信息
        ttk.Label(
            right_frame,
            textvariable=self.current_radio_name,
        ).pack(padx=5, pady=2)

        # 状态栏
        self.status_label = tk.Label(
            right_frame,
        )
        self.status_label.pack(padx=5, pady=2)
        self.time_label = tk.Label(
            right_frame,
        )
        self.time_label.pack(padx=5, pady=2)

        # 控制按钮区
        control_frame = tk.Frame(right_frame)
        control_frame.pack(padx=5, pady=2)
        control_frame.columnconfigure(0, weight=1)
        control_frame.columnconfigure(1, weight=1)

        play_btn = ttk.Button(control_frame, text="播放", command=self.play_selected)
        stop_btn = ttk.Button(control_frame, text="停止", command=self.stop_playback)
        play_btn.grid(row=0, column=0, padx=2)
        stop_btn.grid(row=0, column=1, padx=2)

        # ----------- VLC 相关 重点 -----------
        self.vlc_instance = vlc.Instance("--audio-visual=visual")
        self.vlc_player = self.vlc_instance.media_player_new()

        self.bind("<Map>", self._on_map)  # 确保窗口创建后再嵌入

        # 事件绑定
        event_manager = self.vlc_player.event_manager()
        for value, name in vlc.EventType._enum_names_.items():
            event_manager.event_attach(vlc.EventType(value), self._on_vlc_event)

        # ----------- 启动后自动加载 -----------
        self.after(100, self.load_radios_from_default)
        self.status_label.config(text="准备就绪")
        self.reset_time_label()

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

    def vlc_play(self, url: str):
        if self.vlc_player.is_playing():
            self.vlc_player.stop()
        media = self.vlc_instance.media_new(url)
        self.vlc_player.set_media(media)
        self.vlc_player.play()

    def stop_playback(self):
        self.vlc_player.stop()

    def on_tree_double_click(self, _event):
        # 获取鼠标所在item的iid
        self.play_selected()

    def update_status(self, status: str):
        self.status_label.config(text=status)

    def get_selected_or_first(self):
        def get_first_leaf(parent=None):
            nodes = self.tree.get_children(parent)
            for node in nodes:
                children = self.tree.get_children(node)
                if children:
                    leaf = get_first_leaf(node)
                    if leaf:
                        return leaf
                else:
                    return node
            return None

        selection = self.tree.selection()
        if selection:
            return selection[0]
        else:
            return get_first_leaf()

    def play_selected(self):
        item_id = self.get_selected_or_first()
        if item_id is None or item_id not in self.radios_map:
            return
        # 设Treeview选中项高亮
        self.tree.selection_set(item_id)
        radio_name = self.tree.item(item_id, "text")
        self.set_radio_name(radio_name)
        # 获取第一个流的URL
        if stream_url := self.radios_map[item_id].get("streams", [{}])[0].get("url"):
            self.vlc_play(stream_url)
            self.update_status(f"加载中...")
        else:
            self.update_status("无可播放项")
            messagebox.showwarning(
                "提示", f"未找到可播放的流: {radio_name}", parent=self
            )
            return

    def set_radio_name(self, name):
        self.current_radio_name.set(name)

    def _on_vlc_event(self, event):
        if event.type == vlc.EventType.MediaPlayerPlaying:
            self.status_label.config(text="正在播放")
        elif event.type == vlc.EventType.MediaPlayerBuffering:
            # 只在未播放/首次出现时显示加载中
            if self.vlc_player.get_state() != vlc.State.Playing:
                self.status_label.config(text="加载中...")
            # 否则忽略，或用更弱提示提醒用户
        elif event.type == vlc.EventType.MediaPlayerPaused:
            self.status_label.config(text="已暂停")
        elif event.type == vlc.EventType.MediaPlayerStopped:
            self.status_label.config(text="已停止")
        elif event.type == vlc.EventType.MediaPlayerEndReached:
            self.status_label.config(text="已结束")
            self.reset_time_label()
        elif event.type == vlc.EventType.MediaPlayerTimeChanged:
            # 处理时间变化事件
            self.update_time_label()

    def update_time_label(self):
        # 获取播放时间（毫秒）
        played_ms = self.vlc_player.get_time()
        if played_ms < 0:
            played_ms = 0  # 防止未播放时显示负数
        # 格式化为 mm:ss
        m, s = divmod(played_ms // 1000, 60)
        h, m = divmod(m, 60)
        # 可按需只显示mm:ss或hh:mm:ss
        if h > 0:
            time_str = f"{h:02d}:{m:02d}:{s:02d}"
        else:
            time_str = f"{m:02d}:{s:02d}"
        # 更新标签
        self.time_label.config(text=time_str)

    def reset_time_label(self):
        self.time_label.config(text="--:--")

    def keep_player_area_square(self, event):
        size = min(event.width, event.height, 400)
        self.player_area.config(width=size)
        self.update_idletasks()
        self.player_area.config(height=self.player_area.winfo_width())


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
