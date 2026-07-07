"""
五子棋（含人机对战）— 主程序入口
基于 tkinter 实现，支持三种难度AI、计分系统、排行榜、主题切换等功能

运行方式: python main.py
"""

import tkinter as tk
from gui_app import GomokuApp


def main():
    """主函数：创建窗口并启动游戏"""
    root = tk.Tk()
    root.geometry("680x720")
    root.minsize(640, 680)

    # 设置窗口图标（如果存在）
    try:
        root.iconbitmap("icon.ico")
    except Exception:
        pass  # 图标不存在则忽略

    # 创建游戏应用
    app = GomokuApp(root)

    # 进入 tkinter 主事件循环
    root.mainloop()


if __name__ == "__main__":
    main()
