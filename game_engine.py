"""
五子棋游戏引擎模块
负责棋盘状态管理、落子验证、胜负判定等核心逻辑
"""


class GomokuGame:
    """五子棋游戏核心逻辑类"""

    def __init__(self, board_size=15):
        """初始化游戏"""
        self.board_size = board_size
        self.board = [[0] * board_size for _ in range(board_size)]
        self.current_player = 1  # 1=黑子(玩家), 2=白子(AI)
        self.move_history = []   # 落子历史 [(row, col, player), ...]
        self.game_over = False
        self.winner = 0          # 0=未结束, 1=黑胜, 2=白胜
        self.win_line = []       # 获胜的5子坐标列表
        self.score = 0           # 玩家得分
        self.total_moves = 0     # 总步数

    def reset(self):
        """重置游戏状态"""
        self.board = [[0] * self.board_size for _ in range(self.board_size)]
        self.current_player = 1
        self.move_history.clear()
        self.game_over = False
        self.winner = 0
        self.win_line.clear()
        self.total_moves = 0

    def is_valid_move(self, row, col):
        """判断指定位置是否可以落子"""
        if self.game_over:
            return False
        if not (0 <= row < self.board_size and 0 <= col < self.board_size):
            return False
        return self.board[row][col] == 0

    def place_stone(self, row, col):
        """
        在指定位置落子
        返回: (成功标志, 是否获胜)
        """
        if not self.is_valid_move(row, col):
            return False, False

        player = self.current_player
        self.board[row][col] = player
        self.move_history.append((row, col, player))
        self.total_moves += 1

        # 检查是否获胜
        if self._check_win(row, col, player):
            self.game_over = True
            self.winner = player
            return True, True

        # 检查是否平局（棋盘已满）
        if self.total_moves == self.board_size * self.board_size:
            self.game_over = True
            return True, False

        # 切换玩家
        self.current_player = 3 - player  # 1->2, 2->1
        return True, False

    def _check_win(self, row, col, player):
        """
        检查从 (row, col) 出发是否形成五连
        四个方向：水平、垂直、主对角线、副对角线
        """
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]

        for dr, dc in directions:
            line = [(row, col)]
            # 正方向延伸
            r, c = row + dr, col + dc
            while (0 <= r < self.board_size and 0 <= c < self.board_size
                   and self.board[r][c] == player):
                line.append((r, c))
                r += dr
                c += dc
            # 反方向延伸
            r, c = row - dr, col - dc
            while (0 <= r < self.board_size and 0 <= c < self.board_size
                   and self.board[r][c] == player):
                line.insert(0, (r, c))
                r -= dr
                c -= dc

            if len(line) >= 5:
                self.win_line = line
                return True
        return False

    def get_empty_cells(self):
        """获取所有空白位置"""
        cells = []
        for r in range(self.board_size):
            for c in range(self.board_size):
                if self.board[r][c] == 0:
                    cells.append((r, c))
        return cells

    def get_nearby_empty_cells(self, distance=2):
        """获取已落子位置附近 distance 格内的空白位置"""
        candidates = set()
        for r in range(self.board_size):
            for c in range(self.board_size):
                if self.board[r][c] != 0:
                    for dr in range(-distance, distance + 1):
                        for dc in range(-distance, distance + 1):
                            nr, nc = r + dr, c + dc
                            if (0 <= nr < self.board_size
                                    and 0 <= nc < self.board_size
                                    and self.board[nr][nc] == 0):
                                candidates.add((nr, nc))
        # 如果棋盘为空，返回中心点
        if not candidates:
            center = self.board_size // 2
            candidates.add((center, center))
        return list(candidates)

    def undo(self):
        """悔棋：撤销上一步（用于AI搜索）"""
        if not self.move_history:
            return
        row, col, player = self.move_history.pop()
        self.board[row][col] = 0
        self.current_player = player
        self.total_moves -= 1
        self.game_over = False
        self.winner = 0
        self.win_line.clear()

    def get_board_copy(self):
        """返回棋盘副本"""
        return [row[:] for row in self.board]
