"""
五子棋AI玩家模块
支持三种难度：简单（随机）、普通（评估函数）、困难（Minimax+Alpha-Beta剪枝）
"""

import random


# 棋型评分表
# 格式: (棋型标识, 长度, 开口数, 分数)
# 开口数: 2=两端开放, 1=一端开放, 0=两端封闭
PATTERN_SCORES = {
    "FIVE": 1000000,       # 五连（必胜）
    "OPEN_FOUR": 100000,   # 活四
    "CLOSED_FOUR": 10000,  # 冲四
    "OPEN_THREE": 10000,   # 活三
    "CLOSED_THREE": 1000,  # 眠三
    "OPEN_TWO": 1000,      # 活二
    "CLOSED_TWO": 100,     # 眠二
    "OPEN_ONE": 100,       # 活一
    "CLOSED_ONE": 10,      # 眠一
}


class GomokuAI:
    """五子棋AI，支持三种难度"""

    def __init__(self, difficulty="normal"):
        """
        difficulty: "easy" | "normal" | "hard"
        """
        self.difficulty = difficulty
        self.board_size = 15

    def get_best_move(self, game):
        """根据当前难度返回最佳落子位置"""
        self.board_size = game.board_size

        if self.difficulty == "easy":
            return self._easy_move(game)
        elif self.difficulty == "normal":
            return self._normal_move(game)
        elif self.difficulty == "hard":
            return self._hard_move(game)
        else:
            return self._normal_move(game)

    def _easy_move(self, game):
        """简单难度：在已有棋子附近随机落子"""
        candidates = game.get_nearby_empty_cells(distance=2)
        return random.choice(candidates)

    def _normal_move(self, game):
        """普通难度：对候选位置评分，选择得分最高的位置"""
        candidates = game.get_nearby_empty_cells(distance=2)
        ai_player = game.current_player
        opponent = 3 - ai_player

        best_score = -float("inf")
        best_moves = []

        for row, col in candidates:
            # 评估该位置对AI的得分 + 对防守方的价值（对手在此位置的得分）
            attack_score = self._evaluate_position(game.board, row, col, ai_player)
            defense_score = self._evaluate_position(game.board, row, col, opponent)
            # 攻守兼备：进攻分 + 防守分（如果对手在这里威胁很大也要占）
            total_score = attack_score + defense_score * 0.9

            if total_score > best_score:
                best_score = total_score
                best_moves = [(row, col)]
            elif total_score == best_score:
                best_moves.append((row, col))

        return random.choice(best_moves)

    def _hard_move(self, game):
        """困难难度：Minimax + Alpha-Beta剪枝，搜索深度2层"""
        candidates = game.get_nearby_empty_cells(distance=2)
        ai_player = game.current_player

        # 如果候选位置太多，先用评估函数筛选top候选
        if len(candidates) > 25:
            scored = []
            for row, col in candidates:
                attack = self._evaluate_position(game.board, row, col, ai_player)
                defense = self._evaluate_position(game.board, row, col, 3 - ai_player)
                scored.append((attack + defense * 0.9, row, col))
            scored.sort(reverse=True)
            candidates = [(r, c) for _, r, c in scored[:25]]

        best_score = -float("inf")
        best_moves = []
        alpha = -float("inf")
        beta = float("inf")

        for row, col in candidates:
            game.place_stone(row, col)
            # 如果这一步直接赢了，立即返回
            if game.winner == ai_player:
                game.undo()
                return (row, col)

            score = self._minimax(game, 1, False, alpha, beta, ai_player)
            game.undo()

            if score > best_score:
                best_score = score
                best_moves = [(row, col)]
            elif score == best_score:
                best_moves.append((row, col))

            alpha = max(alpha, score)

        return random.choice(best_moves) if best_moves else candidates[0]

    def _minimax(self, game, depth, is_maximizing, alpha, beta, ai_player):
        """Minimax搜索 + Alpha-Beta剪枝"""
        opponent = 3 - ai_player
        current = ai_player if is_maximizing else opponent

        # 终止条件
        if game.winner == ai_player:
            return 1000000 - depth  # AI赢，越早赢越好
        if game.winner == opponent:
            return -1000000 + depth  # 对手赢，越晚输越好
        if game.total_moves == game.board_size * game.board_size:
            return 0  # 平局
        if depth >= 2:  # 搜索深度限制
            return self._evaluate_board(game, ai_player)

        candidates = game.get_nearby_empty_cells(distance=1)

        # 候选位置太多时做筛选
        if len(candidates) > 15:
            scored = []
            for r, c in candidates:
                a = self._evaluate_position(game.board, r, c, current)
                d = self._evaluate_position(game.board, r, c, 3 - current)
                scored.append((a + d, r, c))
            scored.sort(reverse=True)
            candidates = [(r, c) for _, r, c in scored[:15]]

        if is_maximizing:
            value = -float("inf")
            for row, col in candidates:
                game.place_stone(row, col)
                value = max(value, self._minimax(game, depth + 1, False, alpha, beta, ai_player))
                game.undo()
                alpha = max(alpha, value)
                if alpha >= beta:
                    break  # Beta剪枝
            return value
        else:
            value = float("inf")
            for row, col in candidates:
                game.place_stone(row, col)
                value = min(value, self._minimax(game, depth + 1, True, alpha, beta, ai_player))
                game.undo()
                beta = min(beta, value)
                if alpha >= beta:
                    break  # Alpha剪枝
            return value

    def _evaluate_board(self, game, player):
        """评估整个棋盘在某个玩家视角下的总分"""
        opponent = 3 - player
        total_score = 0
        # 扫描所有行、列、对角线
        for r in range(game.board_size):
            for c in range(game.board_size):
                if game.board[r][c] == player:
                    total_score += self._evaluate_position_for_player(
                        game.board, r, c, player)
                elif game.board[r][c] == opponent:
                    total_score -= self._evaluate_position_for_player(
                        game.board, r, c, opponent)
        return total_score

    def _evaluate_position(self, board, row, col, player):
        """评估在 (row, col) 放置 player 棋子后的局面得分"""
        # 临时放置棋子
        old = board[row][col]
        board[row][col] = player
        score = self._evaluate_position_for_player(board, row, col, player)
        board[row][col] = old
        return score

    def _evaluate_position_for_player(self, board, row, col, player):
        """评估已放置棋子在四个方向的综合得分"""
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        total = 0
        for dr, dc in directions:
            total += self._analyze_direction(board, row, col, dr, dc, player)
        return total

    def _analyze_direction(self, board, row, col, dr, dc, player):
        """
        分析指定方向上以 (row, col) 为中心的棋型
        返回该方向的得分
        """
        size = len(board)
        count = 1  # 当前棋子
        open_ends = 0

        # 正方向延伸
        r, c = row + dr, col + dc
        while 0 <= r < size and 0 <= c < size and board[r][c] == player:
            count += 1
            r += dr
            c += dc
        if 0 <= r < size and 0 <= c < size and board[r][c] == 0:
            open_ends += 1

        # 反方向延伸
        r, c = row - dr, col - dc
        while 0 <= r < size and 0 <= c < size and board[r][c] == player:
            count += 1
            r -= dr
            c -= dc
        if 0 <= r < size and 0 <= c < size and board[r][c] == 0:
            open_ends += 1

        return self._score_pattern(count, open_ends)

    def _score_pattern(self, count, open_ends):
        """根据棋子数目和开口数计算得分"""
        if count >= 5:
            return PATTERN_SCORES["FIVE"]
        if count == 4:
            if open_ends == 2:
                return PATTERN_SCORES["OPEN_FOUR"]
            elif open_ends == 1:
                return PATTERN_SCORES["CLOSED_FOUR"]
        if count == 3:
            if open_ends == 2:
                return PATTERN_SCORES["OPEN_THREE"]
            elif open_ends == 1:
                return PATTERN_SCORES["CLOSED_THREE"]
        if count == 2:
            if open_ends == 2:
                return PATTERN_SCORES["OPEN_TWO"]
            elif open_ends == 1:
                return PATTERN_SCORES["CLOSED_TWO"]
        if count == 1:
            if open_ends == 2:
                return PATTERN_SCORES["OPEN_ONE"]
            elif open_ends == 1:
                return PATTERN_SCORES["CLOSED_ONE"]
        return 0
