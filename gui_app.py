"""
五子棋GUI界面模块
基于 tkinter 实现棋盘绘制、控件布局、事件处理、主题切换等功能
"""

import tkinter as tk
from tkinter import messagebox, ttk
import json
import os

from game_engine import GomokuGame
from ai_player import GomokuAI


# 主题色彩配置
THEMES = {
    "经典": {
        "bg": "#DEB887",
        "board": "#DCB468",
        "line": "#5D3A1A",
        "black_stone": "#1A1A1A",
        "white_stone": "#F5F5F5",
        "highlight": "#FF4444",
        "panel_bg": "#F0E6D3",
        "btn_bg": "#C8A882",
        "btn_fg": "#3E2723",
        "text": "#3E2723",
        "last_move": "#FFD700",
    },
    "海洋": {
        "bg": "#B0C4DE",
        "board": "#87CEEB",
        "line": "#1A3A5C",
        "black_stone": "#0D1B2A",
        "white_stone": "#E8F4FD",
        "highlight": "#FF6B6B",
        "panel_bg": "#D4E6F1",
        "btn_bg": "#5B8FA8",
        "btn_fg": "#FFFFFF",
        "text": "#1A3A5C",
        "last_move": "#FFD700",
    },
    "森林": {
        "bg": "#C5D5A8",
        "board": "#A8C878",
        "line": "#2D5016",
        "black_stone": "#1B3A0A",
        "white_stone": "#F0F7E6",
        "highlight": "#E74C3C",
        "panel_bg": "#D9E8C8",
        "btn_bg": "#6B8E4E",
        "btn_fg": "#FFFFFF",
        "text": "#2D5016",
        "last_move": "#FFD700",
    },
}

# 分数文件路径
SCORES_FILE = "high_scores.json"


class GomokuApp:
    """五子棋主应用程序"""

    def __init__(self, root):
        self.root = root
        self.root.title("五子棋 - 人机对战")
        self.root.resizable(False, False)

        # 游戏参数
        self.board_size = 15
        self.cell_size = 38
        self.margin = 30
        self.canvas_size = self.margin * 2 + self.cell_size * (self.board_size - 1)

        # 游戏状态
        self.game = GomokuGame(self.board_size)
        self.ai = GomokuAI("normal")
        self.is_paused = False
        self.is_player_turn = True  # 玩家执黑先手
        self.human_player = 1       # 人类玩家用黑子(1)
        self.ai_player = 2          # AI用白子(2)
        self.current_theme = "经典"
        self.high_scores = self._load_scores()

        # 构建界面
        self._setup_ui()
        self._apply_theme()

        # 初始绘制棋盘
        self._draw_board()

    # ==================== 界面搭建 ====================

    def _setup_ui(self):
        """搭建整个GUI界面结构"""
        # 主容器
        self.main_frame = tk.Frame(self.root, padx=10, pady=10)
        self.main_frame.pack()

        # 标题标签
        self.title_label = tk.Label(
            self.main_frame,
            text="五子棋 — 人机对战",
            font=("微软雅黑", 20, "bold"),
        )
        self.title_label.pack(pady=(0, 8))

        # 棋盘画布
        self.canvas = tk.Canvas(
            self.main_frame,
            width=self.canvas_size,
            height=self.canvas_size,
            cursor="hand2",
        )
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self._on_canvas_click)
        self.canvas.bind("<Motion>", self._on_mouse_move)

        # 控制面板
        self.control_frame = tk.Frame(self.main_frame, pady=8)
        self.control_frame.pack(fill=tk.X)

        # 第一行：难度选择 + 得分信息
        self.info_frame = tk.Frame(self.control_frame)
        self.info_frame.pack(fill=tk.X, pady=2)

        tk.Label(self.info_frame, text="难度:", font=("微软雅黑", 10)).pack(
            side=tk.LEFT, padx=(0, 4))

        self.difficulty_var = tk.StringVar(value="普通")
        self.difficulty_menu = tk.OptionMenu(
            self.info_frame, self.difficulty_var,
            "简单", "普通", "困难",
            command=self._on_difficulty_change,
        )
        self.difficulty_menu.config(font=("微软雅黑", 10), width=6)
        self.difficulty_menu.pack(side=tk.LEFT, padx=(0, 20))

        self.score_label = tk.Label(
            self.info_frame, text="得分: 0",
            font=("微软雅黑", 10, "bold"))
        self.score_label.pack(side=tk.LEFT, padx=(0, 20))

        self.high_score_label = tk.Label(
            self.info_frame, text="最高分: 0",
            font=("微软雅黑", 10, "bold"))
        self.high_score_label.pack(side=tk.LEFT)

        # 第二行：按钮
        self.btn_frame = tk.Frame(self.control_frame)
        self.btn_frame.pack(fill=tk.X, pady=4)

        self.new_game_btn = tk.Button(
            self.btn_frame, text="新游戏",
            command=self._on_new_game,
            font=("微软雅黑", 10), width=8)
        self.new_game_btn.pack(side=tk.LEFT, padx=3)

        self.pause_btn = tk.Button(
            self.btn_frame, text="暂停",
            command=self._on_pause,
            font=("微软雅黑", 10), width=8)
        self.pause_btn.pack(side=tk.LEFT, padx=3)

        self.undo_btn = tk.Button(
            self.btn_frame, text="悔棋",
            command=self._on_undo,
            font=("微软雅黑", 10), width=8)
        self.undo_btn.pack(side=tk.LEFT, padx=3)

        self.theme_btn = tk.Button(
            self.btn_frame, text="主题",
            command=self._on_theme_switch,
            font=("微软雅黑", 10), width=8)
        self.theme_btn.pack(side=tk.LEFT, padx=3)

        self.leaderboard_btn = tk.Button(
            self.btn_frame, text="排行榜",
            command=self._on_leaderboard,
            font=("微软雅黑", 10), width=8)
        self.leaderboard_btn.pack(side=tk.LEFT, padx=3)

        # 第三行：状态标签
        self.status_label = tk.Label(
            self.control_frame,
            text="你的回合 — 请点击棋盘落子",
            font=("微软雅黑", 10),
        )
        self.status_label.pack(pady=(4, 0))

    # ==================== 棋盘绘制 ====================

    def _draw_board(self):
        """绘制棋盘网格和星位点"""
        self.canvas.delete("grid")
        theme = THEMES[self.current_theme]
        m = self.margin
        s = self.cell_size
        n = self.board_size

        # 绘制背景
        self.canvas.configure(bg=theme["board"])

        # 绘制网格线
        for i in range(n):
            # 水平线
            self.canvas.create_line(
                m, m + i * s, m + (n - 1) * s, m + i * s,
                fill=theme["line"], tags="grid")
            # 垂直线
            self.canvas.create_line(
                m + i * s, m, m + i * s, m + (n - 1) * s,
                fill=theme["line"], tags="grid")

        # 星位点（天元和四角星位）
        star_positions = []
        if n == 15:
            star_positions = [(3, 3), (3, 7), (3, 11),
                              (7, 3), (7, 7), (7, 11),
                              (11, 3), (11, 7), (11, 11)]
        for r, c in star_positions:
            x = m + c * s
            y = m + r * s
            self.canvas.create_oval(
                x - 3, y - 3, x + 3, y + 3,
                fill=theme["line"], outline=theme["line"], tags="grid")

        # 坐标标注
        for i in range(n):
            # 列标 (字母，跳过 I)
            label = chr(ord('A') + i + (1 if i >= 8 else 0))
            self.canvas.create_text(
                m + i * s, m - 15, text=label,
                fill=theme["text"], font=("Arial", 8), tags="grid")
            # 行标
            self.canvas.create_text(
                m - 15, m + i * s, text=str(i + 1),
                fill=theme["text"], font=("Arial", 8), tags="grid")

        # 重绘所有棋子
        self._redraw_stones()

    def _redraw_stones(self):
        """重绘所有已落棋子"""
        self.canvas.delete("stone")
        self.canvas.delete("last_move")
        self.canvas.delete("preview")
        theme = THEMES[self.current_theme]
        m = self.margin
        s = self.cell_size
        r_stone = s // 2 - 2

        for r in range(self.board_size):
            for c in range(self.board_size):
                if self.game.board[r][c] != 0:
                    x = m + c * s
                    y = m + r * s
                    color = (theme["black_stone"]
                             if self.game.board[r][c] == 1
                             else theme["white_stone"])
                    outline = (theme["white_stone"]
                               if self.game.board[r][c] == 1
                               else theme["black_stone"])
                    self.canvas.create_oval(
                        x - r_stone, y - r_stone,
                        x + r_stone, y + r_stone,
                        fill=color, outline=outline, width=1,
                        tags="stone")

        # 高亮最后一手
        if self.game.move_history:
            r, c, player = self.game.move_history[-1]
            x = m + c * s
            y = m + r * s
            self.canvas.create_oval(
                x - 4, y - 4, x + 4, y + 4,
                fill=theme["last_move"], outline="",
                tags="last_move")

        # 高亮获胜连线
        if self.game.win_line:
            for r, c in self.game.win_line:
                x = m + c * s
                y = m + r * s
                self.canvas.create_oval(
                    x - 4, y - 4, x + 4, y + 4,
                    fill=theme["highlight"], outline="",
                    tags="last_move")

    # ==================== 事件处理 ====================

    def _on_canvas_click(self, event):
        """处理棋盘点击事件 — 体现事件驱动编程思想"""
        if self.game.game_over:
            return
        if self.is_paused:
            return
        if not self.is_player_turn:
            return

        # 将像素坐标转换为棋盘坐标
        row, col = self._pixel_to_board(event.x, event.y)
        if row is None:
            return

        # 执行玩家落子
        self._player_move(row, col)

    def _on_mouse_move(self, event):
        """处理鼠标移动 — 在棋盘上显示预览效果"""
        self.canvas.delete("preview")
        if self.game.game_over or self.is_paused or not self.is_player_turn:
            return

        row, col = self._pixel_to_board(event.x, event.y)
        if row is None:
            return
        if not self.game.is_valid_move(row, col):
            return

        theme = THEMES[self.current_theme]
        m = self.margin
        s = self.cell_size
        x = m + col * s
        y = m + row * s

        preview_color = theme["black_stone"]
        self.canvas.create_oval(
            x - s//2 + 3, y - s//2 + 3,
            x + s//2 - 3, y + s//2 - 3,
            fill="", outline=preview_color, width=1, dash=(3, 3),
            tags="preview")

    def _pixel_to_board(self, x, y):
        """像素坐标转棋盘行列坐标"""
        m = self.margin
        s = self.cell_size
        col = round((x - m) / s)
        row = round((y - m) / s)
        # 容差：距离交叉点太远则忽略
        px = m + col * s
        py = m + row * s
        if abs(x - px) > s // 2 or abs(y - py) > s // 2:
            return None, None
        if 0 <= row < self.board_size and 0 <= col < self.board_size:
            return row, col
        return None, None

    def _player_move(self, row, col):
        """执行玩家落子"""
        success, win = self.game.place_stone(row, col)
        if not success:
            return

        self._redraw_stones()
        self._update_score_display()

        if win:
            self._on_game_end(1)
            return

        if self.game.game_over:  # 平局
            self._on_game_end(0)
            return

        # AI回合（使用 after 避免界面冻结）
        self.is_player_turn = False
        self.status_label.config(text="AI思考中...")
        self.root.after(300, self._ai_move)

    def _ai_move(self):
        """执行AI落子（通过 after 延迟调用，体现定时器机制）"""
        best_move = self.ai.get_best_move(self.game)
        if best_move is None:
            return

        success, win = self.game.place_stone(best_move[0], best_move[1])
        if not success:
            return

        self._redraw_stones()

        if win:
            self._on_game_end(2)
            return

        if self.game.game_over:  # 平局
            self._on_game_end(0)
            return

        # 恢复玩家回合
        self.is_player_turn = True
        self.status_label.config(text="你的回合 — 请点击棋盘落子")

    # ==================== 游戏结束处理 ====================

    def _on_game_end(self, winner):
        """游戏结束处理"""
        if winner == 1:  # 玩家胜
            self.game.score += self._calculate_score()
            self._update_score_display()
            self._save_high_score()
            self.status_label.config(text="恭喜！你赢了！")
            msg = f"恭喜你获胜！\n当前得分: {self.game.score}\n总步数: {self.game.total_moves}"
        elif winner == 2:  # AI胜
            self.status_label.config(text="AI获胜，再接再厉！")
            msg = f"AI获胜了，再接再厉！\n当前得分: {self.game.score}\n总步数: {self.game.total_moves}"
        else:  # 平局
            self.status_label.config(text="平局！")
            msg = f"平局！\n当前得分: {self.game.score}\n总步数: {self.game.total_moves}"

        self.is_player_turn = False

        # 使用 messagebox 弹出统计信息
        result = messagebox.askquestion(
            "游戏结束",
            msg + "\n\n是否再来一局？",
            parent=self.root)

        if result == "yes":
            self._on_new_game()
        else:
            self.status_label.config(text="游戏结束 — 点击「新游戏」开始")

    def _calculate_score(self):
        """根据难度和步数计算得分"""
        base_score = 100
        difficulty_bonus = {"简单": 0, "普通": 50, "困难": 100}
        # 步数越少，额外加分越多
        efficiency_bonus = max(0, (225 - self.game.total_moves) * 2)
        return (base_score
                + difficulty_bonus.get(self.difficulty_var.get(), 50)
                + efficiency_bonus)

    def _update_score_display(self):
        """更新得分显示"""
        self.score_label.config(text=f"得分: {self.game.score}")
        # 加载历史最高分
        best = self._get_best_score()
        self.high_score_label.config(text=f"最高分: {best}")

    # ==================== 按钮回调 ====================

    def _on_new_game(self):
        """新游戏按钮回调"""
        self.game.reset()
        self.is_player_turn = True
        self.is_paused = False
        self.pause_btn.config(text="暂停")
        self.status_label.config(text="你的回合 — 请点击棋盘落子")
        self._draw_board()
        self._update_buttons_state()

    def _on_pause(self):
        """暂停 / 继续按钮回调"""
        if self.game.game_over:
            return

        self.is_paused = not self.is_paused
        if self.is_paused:
            self.pause_btn.config(text="继续")
            self.status_label.config(text="游戏已暂停")
        else:
            self.pause_btn.config(text="暂停")
            if self.is_player_turn:
                self.status_label.config(text="你的回合 — 请点击棋盘落子")
            else:
                self.status_label.config(text="AI思考中...")
                self.root.after(300, self._ai_move)

        self._update_buttons_state()

    def _on_undo(self):
        """悔棋按钮回调 — 撤销玩家和AI各一步"""
        if self.game.game_over or self.is_paused:
            return
        if len(self.game.move_history) < 2:
            return
        if not self.is_player_turn:
            return

        # 撤销AI的一步
        self.game.undo()
        # 撤销玩家的一步
        self.game.undo()
        self._redraw_stones()
        self.status_label.config(text="已悔一步，你的回合")

    def _on_theme_switch(self):
        """切换主题"""
        themes = list(THEMES.keys())
        idx = themes.index(self.current_theme)
        self.current_theme = themes[(idx + 1) % len(themes)]
        self._apply_theme()
        self._draw_board()

    def _on_difficulty_change(self, value):
        """难度切换回调"""
        self.ai.difficulty = value
        if self.game.total_moves == 0:
            # 如果还没开始下棋，更新即可
            pass
        else:
            # 如果游戏正在进行，提示重新开始
            if messagebox.askyesno("难度切换", "切换难度将重新开始游戏，确定吗？"):
                self._on_new_game()
            else:
                self.difficulty_var.set(
                    {"easy": "简单", "normal": "普通", "hard": "困难"}.get(
                        self.ai.difficulty, "普通"))

    def _on_leaderboard(self):
        """显示排行榜"""
        scores = self._load_scores()
        if not scores:
            messagebox.showinfo("排行榜", "暂无记录，快来挑战吧！", parent=self.root)
            return

        # 创建排行榜窗口
        lb_window = tk.Toplevel(self.root)
        lb_window.title("排行榜 — Top 5")
        lb_window.geometry("360x280")
        lb_window.resizable(False, False)
        lb_window.transient(self.root)
        lb_window.grab_set()

        # 使用 Treeview 控件（第三种控件类型）
        columns = ("排名", "得分", "难度", "步数", "日期")
        tree = ttk.Treeview(lb_window, columns=columns, show="headings", height=5)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=65, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(lb_window, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

        for i, entry in enumerate(scores[:5], 1):
            tree.insert("", tk.END, values=(
                i, entry.get("score", 0), entry.get("difficulty", "-"),
                entry.get("moves", "-"), entry.get("date", "-")))

        # 关闭按钮
        tk.Button(lb_window, text="关闭", command=lb_window.destroy,
                  font=("微软雅黑", 10)).pack(pady=(0, 10))

    # ==================== 主题应用 ====================

    def _apply_theme(self):
        """应用当前主题色彩"""
        theme = THEMES[self.current_theme]
        bg = theme["bg"]
        self.root.configure(bg=bg)
        self.main_frame.configure(bg=bg)
        self.control_frame.configure(bg=theme["panel_bg"])
        self.info_frame.configure(bg=theme["panel_bg"])
        self.btn_frame.configure(bg=theme["panel_bg"])
        self.title_label.configure(bg=bg, fg=theme["text"])
        self.status_label.configure(bg=theme["panel_bg"], fg=theme["text"])
        self.score_label.configure(bg=theme["panel_bg"], fg=theme["text"])
        self.high_score_label.configure(bg=theme["panel_bg"], fg=theme["text"])

        btn_style = {"bg": theme["btn_bg"], "fg": theme["btn_fg"],
                     "activebackground": theme["highlight"],
                     "activeforeground": "#FFFFFF"}
        for btn in [self.new_game_btn, self.pause_btn, self.undo_btn,
                     self.theme_btn, self.leaderboard_btn]:
            btn.configure(**btn_style)

    def _update_buttons_state(self):
        """根据游戏状态更新按钮启用/禁用"""
        if self.is_paused:
            self.canvas.configure(cursor="")
        else:
            self.canvas.configure(cursor="hand2")

    # ==================== 数据持久化 ====================

    def _load_scores(self):
        """从JSON文件加载历史最高分"""
        if not os.path.exists(SCORES_FILE):
            return []
        try:
            with open(SCORES_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("high_scores", [])
        except (json.JSONDecodeError, IOError):
            return []

    def _save_high_score(self):
        """保存高分记录"""
        scores = self._load_scores()
        from datetime import datetime
        new_entry = {
            "score": self.game.score,
            "difficulty": self.difficulty_var.get(),
            "moves": self.game.total_moves,
            "date": datetime.now().strftime("%m/%d %H:%M"),
        }
        scores.append(new_entry)
        # 按得分降序排序，保留前5条
        scores.sort(key=lambda x: x.get("score", 0), reverse=True)
        scores = scores[:5]
        try:
            with open(SCORES_FILE, "w", encoding="utf-8") as f:
                json.dump({"high_scores": scores}, f, ensure_ascii=False, indent=2)
        except IOError:
            pass
        self.high_scores = scores
        self._update_score_display()

    def _get_best_score(self):
        """获取历史最高分"""
        scores = self._load_scores()
        if not scores:
            return 0
        return max(s.get("score", 0) for s in scores)
