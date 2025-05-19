# 广播直播桌面软件

这是一个使用 Python Tkinter + VLC 开发的广播直播桌面客户端，支持分类显示广播电台，双击即可播放，内置最基础的播放/停止功能。带有友好的
GUI 界面，适合网络收音机、网络广播直播、音频节目收听等场景。

## 主要特性

- 支持树状分类显示电台及分组
- 内嵌 VLC 播放器，支持多格式音频流播放
- 播放区伴随窗口大小自适应调整
- 实时显示正在播放电台名称与播放时长
- 支持播放、停止、播放状态提示
- 可读取外部 JSON 文件配置电台及流地址

## 运行截图

![](imgs\screenshot_1.png)

## 快速开始

1. **克隆本仓库**
   ```bash
   git clone https://github.com/你的用户名/你的仓库名.git
   cd 你的仓库名
   ```
2. **安装依赖**

   ```bash
   pip install -r requirements.txt
   ```
   或者手动安装主要依赖：
   ```bash
   pip install python-vlc requests
   ```

2. **准备 VLC**

    * 请确保已在本地安装 VLC 播放器（推荐 3.x 版本）。
    * Windows 用户请将 VLC 安装目录（如 C:\Program Files\VideoLAN\VLC）添加到系统 PATH 环境变量。
3. **运行程序**

   ```bash
   python main.py
   ```

## 使用说明

* 启动后，左侧为电台分组树，展开可浏览各地电台。
* 双击任意电台即可开始播放，当前播放信息会显示在下方。
* 播放区可自适应窗口大小，支持暂停/停止操作。
* 支持自定义电台列表，编辑 `radios.json` 文件即可。

## 配置说明

*电台数据存储在 `radios.json` 文件中，格式为分组+电台+流地址的嵌套结构。

* 可使用 src/fetch_radios.py 脚本自动抓取央广网最新电台数据，生成/更新 radios.json。

## 依赖说明

* Python 3.7 及以上
* python-vlc
* requests

## 常见问题

* 无法播放/找不到 VLC
  请确认已正确安装 VLC 并将其目录加入 PATH。


* 电台列表为空或加载失败
  检查 radios.json 文件格式是否正确，或重新运行抓取脚本。


* 界面显示异常
  建议使用 Windows 10 及以上系统，分辨率建议 1080p 及以上。

### 许可协议

本项目遵循 MIT License，欢迎自由使用和二次开发。

<hr></hr> 如有问题或建议，欢迎提交 Issue 或 PR！
