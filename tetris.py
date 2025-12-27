import pygame
import random
import sys

# 初始化Pygame
pygame.init()

# 游戏常量
COLS = 10
ROWS = 20
BLOCK_SIZE = 30
SCREEN_WIDTH = 300
SCREEN_HEIGHT = 600
INFO_PANEL_WIDTH = 150

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (50, 50, 50)
DARK_GRAY = (30, 30, 30)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)

# 方块颜色
COLORS = [
    None,
    (255, 13, 114),   # I - 红色
    (13, 194, 255),   # J - 蓝色
    (13, 255, 114),   # L - 绿色
    (245, 56, 255),   # O - 紫色
    (255, 142, 13),   # S - 橙色
    (255, 225, 56),   # T - 黄色
    (56, 119, 255),   # Z - 蓝色
    (255, 165, 0)     # 山药 - 橙色
]

# 方块形状
SHAPES = [
    None,
    # I
    [
        [0, 0, 0, 0],
        [1, 1, 1, 1],
        [0, 0, 0, 0],
        [0, 0, 0, 0]
    ],
    # J
    [
        [2, 0, 0],
        [2, 2, 2],
        [0, 0, 0]
    ],
    # L
    [
        [0, 0, 3],
        [3, 3, 3],
        [0, 0, 0]
    ],
    # O
    [
        [4, 4],
        [4, 4]
    ],
    # S
    [
        [0, 5, 5],
        [5, 5, 0],
        [0, 0, 0]
    ],
    # T
    [
        [0, 6, 0],
        [6, 6, 6],
        [0, 0, 0]
    ],
    # Z
    [
        [7, 7, 0],
        [0, 7, 7],
        [0, 0, 0]
    ]
]

class TetrisGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH + INFO_PANEL_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("俄罗斯方块 - 无限关卡+整蛊版")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 20)
        self.small_font = pygame.font.SysFont("Arial", 16)
        
        # 游戏状态
        self.board = self.create_matrix(COLS, ROWS)
        self.player = {
            'pos': {'x': 0, 'y': 0},
            'matrix': None,
            'score': 0,
            'level': 1,
            'lines': 0,
            'next_piece': None
        }
        
        self.drop_counter = 0
        self.drop_interval = 1000
        self.last_time = 0
        self.game_active = False
        self.prank_activated = False
        self.prank_type = 0
        
        # 初始化游戏
        self.player['next_piece'] = self.create_piece()
        self.player_reset()
        
    def create_matrix(self, width, height):
        """创建矩阵"""
        return [[0 for _ in range(width)] for _ in range(height)]
    
    def create_piece(self):
        """创建随机方块"""
        piece = random.randint(1, 7)
        return [row[:] for row in SHAPES[piece]]
    
    def draw_matrix(self, matrix, offset):
        """绘制方块"""
        for y, row in enumerate(matrix):
            for x, value in enumerate(row):
                if value != 0:
                    rect = pygame.Rect(
                        (x + offset['x']) * BLOCK_SIZE,
                        (y + offset['y']) * BLOCK_SIZE,
                        BLOCK_SIZE, BLOCK_SIZE
                    )
                    pygame.draw.rect(self.screen, COLORS[value], rect)
                    pygame.draw.rect(self.screen, BLACK, rect, 1)
    
    def draw_board(self):
        """绘制游戏板"""
        for y, row in enumerate(self.board):
            for x, value in enumerate(row):
                if value != 0:
                    rect = pygame.Rect(
                        x * BLOCK_SIZE,
                        y * BLOCK_SIZE,
                        BLOCK_SIZE, BLOCK_SIZE
                    )
                    pygame.draw.rect(self.screen, COLORS[value], rect)
                    pygame.draw.rect(self.screen, BLACK, rect, 1)
    
    def draw_next_piece(self):
        """绘制下一个方块"""
        # 绘制预览框
        next_piece_rect = pygame.Rect(
            SCREEN_WIDTH + 15, 50, 120, 120
        )
        pygame.draw.rect(self.screen, DARK_GRAY, next_piece_rect)
        pygame.draw.rect(self.screen, WHITE, next_piece_rect, 2)
        
        if self.player['next_piece']:
            # 在预览框中居中绘制下一个方块
            piece_width = len(self.player['next_piece'][0])
            piece_height = len(self.player['next_piece'])
            
            offset_x = SCREEN_WIDTH + 15 + (120 - piece_width * 20) // 2
            offset_y = 50 + (120 - piece_height * 20) // 2
            
            for y, row in enumerate(self.player['next_piece']):
                for x, value in enumerate(row):
                    if value != 0:
                        rect = pygame.Rect(
                            offset_x + x * 20,
                            offset_y + y * 20,
                            20, 20
                        )
                        pygame.draw.rect(self.screen, COLORS[value], rect)
                        pygame.draw.rect(self.screen, BLACK, rect, 1)
    
    def draw_info_panel(self):
        """绘制信息面板"""
        # 绘制分数
        score_text = self.font.render(f"得分: {self.player['score']}", True, WHITE)
        self.screen.blit(score_text, (SCREEN_WIDTH + 15, 200))
        
        level_text = self.font.render(f"关卡: {self.player['level']}", True, WHITE)
        self.screen.blit(level_text, (SCREEN_WIDTH + 15, 230))
        
        lines_text = self.font.render(f"消除行数: {self.player['lines']}", True, WHITE)
        self.screen.blit(lines_text, (SCREEN_WIDTH + 15, 260))
        
        # 绘制控制说明
        controls_y = 320
        controls = [
            "控制:",
            "← → 移动",
            "↑ 旋转",
            "↓ 加速下降",
            "空格 瞬间下落"
        ]
        
        for i, text in enumerate(controls):
            ctrl_text = self.small_font.render(text, True, WHITE)
            self.screen.blit(ctrl_text, (SCREEN_WIDTH + 15, controls_y + i * 25))
        
        # 绘制开始/暂停按钮
        button_rect = pygame.Rect(SCREEN_WIDTH + 15, 450, 120, 40)
        pygame.draw.rect(self.screen, (76, 175, 80), button_rect)
        pygame.draw.rect(self.screen, WHITE, button_rect, 2)
        
        button_text = "开始/暂停" if not self.game_active else "暂停"
        text_surf = self.font.render(button_text, True, WHITE)
        text_rect = text_surf.get_rect(center=button_rect.center)
        self.screen.blit(text_surf, text_rect)
        
        return button_rect
    
    def draw_game_over(self):
        """绘制游戏结束界面"""
        if not self.game_active and self.player['score'] > 0:
            overlay = pygame.Surface((SCREEN_WIDTH + INFO_PANEL_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(200)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))
            
            game_over_text = self.font.render("游戏结束", True, WHITE)
            score_text = self.font.render(f"最终得分: {self.player['score']}", True, WHITE)
            restart_text = self.font.render("按R重新开始", True, WHITE)
            
            self.screen.blit(game_over_text, ((SCREEN_WIDTH + INFO_PANEL_WIDTH) // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 60))
            self.screen.blit(score_text, ((SCREEN_WIDTH + INFO_PANEL_WIDTH) // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2 - 20))
            self.screen.blit(restart_text, ((SCREEN_WIDTH + INFO_PANEL_WIDTH) // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))
    
    def draw_prank_message(self):
        """绘制整蛊消息"""
        if self.prank_activated:
            message = ""
            if self.prank_type == 1:
                message = "方块大小变了！"
            elif self.prank_type == 2:
                message = "方块太脆了，碎了！"
            elif self.prank_type == 3:
                message = "卡住了，移不动了！"
            elif self.prank_type == 4:
                message = "没卡住，掉下去了！"
            elif self.prank_type == 5:
                message = "来了个山药！"
            
            # 绘制整蛊消息
            message_surf = self.font.render(message, True, WHITE)
            message_rect = pygame.Rect(
                (SCREEN_WIDTH + INFO_PANEL_WIDTH) // 2 - 100,
                50,
                200,
                50
            )
            
            pygame.draw.rect(self.screen, RED, message_rect)
            pygame.draw.rect(self.screen, WHITE, message_rect, 2)
            
            text_rect = message_surf.get_rect(center=message_rect.center)
            self.screen.blit(message_surf, text_rect)
    
    def draw(self):
        """绘制游戏"""
        # 绘制背景
        self.screen.fill((240, 240, 240))
        
        # 绘制游戏区域边框
        game_rect = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        pygame.draw.rect(self.screen, DARK_GRAY, game_rect, 2)
        
        # 绘制游戏内容
        inner_rect = pygame.Rect(2, 2, SCREEN_WIDTH - 4, SCREEN_HEIGHT - 4)
        pygame.draw.rect(self.screen, (17, 17, 17), inner_rect)
        
        self.draw_board()
        self.draw_matrix(self.player['matrix'], self.player['pos'])
        
        # 绘制信息面板
        info_rect = pygame.Rect(SCREEN_WIDTH, 0, INFO_PANEL_WIDTH, SCREEN_HEIGHT)
        pygame.draw.rect(self.screen, GRAY, info_rect)
        
        self.draw_next_piece()
        button_rect = self.draw_info_panel()
        self.draw_prank_message()
        self.draw_game_over()
        
        pygame.display.flip()
        return button_rect
    
    def merge(self):
        """合并方块到游戏板"""
        for y, row in enumerate(self.player['matrix']):
            for x, value in enumerate(row):
                if value != 0:
                    board_y = y + self.player['pos']['y']
                    board_x = x + self.player['pos']['x']
                    if 0 <= board_y < ROWS and 0 <= board_x < COLS:
                        self.board[board_y][board_x] = value
    
    def collide(self):
        """检查碰撞"""
        for y, row in enumerate(self.player['matrix']):
            for x, value in enumerate(row):
                if value != 0:
                    board_y = y + self.player['pos']['y']
                    board_x = x + self.player['pos']['x']
                    
                    if (board_y >= ROWS or board_x < 0 or board_x >= COLS or 
                        (board_y >= 0 and self.board[board_y][board_x] != 0)):
                        return True
        return False
    
    def rotate(self, matrix, dir):
        """旋转方块"""
        # 转置矩阵
        rotated = [[matrix[y][x] for y in range(len(matrix))] 
                  for x in range(len(matrix[0]))]
        
        # 根据方向反转行或列
        if dir > 0:
            rotated = [row[::-1] for row in rotated]
        else:
            rotated = rotated[::-1]
            
        return rotated
    
    def player_move(self, dir):
        """玩家移动"""
        # 如果触发了整蛊"卡住了"效果，则有一定概率无法移动
        if self.prank_activated and self.prank_type == 3 and random.random() < 0.3:
            return  # 30%概率卡住无法移动
        
        self.player['pos']['x'] += dir
        if self.collide():
            self.player['pos']['x'] -= dir
    
    def player_rotate(self, dir):
        """玩家旋转"""
        original_matrix = self.player['matrix']
        original_x = self.player['pos']['x']
        offset = 1
        
        self.player['matrix'] = self.rotate(self.player['matrix'], dir)
        
        while self.collide():
            self.player['pos']['x'] += offset
            offset = -(offset + (1 if offset > 0 else -1))
            if abs(offset) > len(self.player['matrix'][0]):
                self.player['matrix'] = original_matrix
                self.player['pos']['x'] = original_x
                return
    
    def player_drop(self):
        """玩家下落"""
        # 如果触发了整蛊"太脆了"效果，则有一定概率直接碎掉
        if self.prank_activated and self.prank_type == 2 and random.random() < 0.2:
            # 方块碎掉了，直接重置
            self.player_reset()
            return
        
        self.player['pos']['y'] += 1
        if self.collide():
            self.player['pos']['y'] -= 1
            self.merge()
            self.player_reset()
            self.sweep_rows()
            self.update_score()
        self.drop_counter = 0
    
    def player_hard_drop(self):
        """瞬间下落"""
        # 如果触发了整蛊"没卡住"效果，则有一定概率不起作用
        if self.prank_activated and self.prank_type == 4 and random.random() < 0.5:
            # 50%概率失效
            return
        
        while not self.collide():
            self.player['pos']['y'] += 1
        self.player['pos']['y'] -= 1
        self.player_drop()
    
    def make_piece_bigger(self, matrix):
        """让方块变大"""
        bigger_matrix = [row[:] for row in matrix]
        # 添加一些额外的方块让它看起来更大
        for y in range(len(bigger_matrix)):
            for x in range(len(bigger_matrix[y])):
                if bigger_matrix[y][x] != 0 and random.random() < 0.3:
                    # 30%概率在周围添加方块
                    if y > 0 and bigger_matrix[y-1][x] == 0:
                        bigger_matrix[y-1][x] = bigger_matrix[y][x]
                    if y < len(bigger_matrix)-1 and bigger_matrix[y+1][x] == 0:
                        bigger_matrix[y+1][x] = bigger_matrix[y][x]
                    if x > 0 and bigger_matrix[y][x-1] == 0:
                        bigger_matrix[y][x-1] = bigger_matrix[y][x]
                    if x < len(bigger_matrix[y])-1 and bigger_matrix[y][x+1] == 0:
                        bigger_matrix[y][x+1] = bigger_matrix[y][x]
        return bigger_matrix
    
    def make_piece_smaller(self, matrix):
        """让方块变小"""
        smaller_matrix = [row[:] for row in matrix]
        for y in range(len(smaller_matrix)):
            for x in range(len(smaller_matrix[y])):
                if smaller_matrix[y][x] != 0 and random.random() < 0.3:
                    # 30%概率移除方块
                    smaller_matrix[y][x] = 0
        return smaller_matrix
    
    def player_reset(self):
        """重置玩家"""
        # 如果没有下一个方块，创建一个
        if not self.player['next_piece']:
            self.player['next_piece'] = self.create_piece()
        
        # 设置当前方块为下一个方块
        self.player['matrix'] = self.player['next_piece']
        self.player['next_piece'] = self.create_piece()
        
        # 检查是否触发"方块大小变化"整蛊
        if self.prank_activated and self.prank_type == 1:
            # 50%概率变大，50%概率变小
            if random.random() < 0.5:
                # 方块变大（视觉效果）
                self.player['matrix'] = self.make_piece_bigger(self.player['matrix'])
            else:
                # 方块变小（视觉效果）
                self.player['matrix'] = self.make_piece_smaller(self.player['matrix'])
        
        # 重置位置
        self.player['pos']['y'] = 0
        self.player['pos']['x'] = COLS // 2 - len(self.player['matrix'][0]) // 2
        
        # 检查游戏结束
        if self.collide():
            self.game_active = False
    
    def sweep_rows(self):
        """清除完整行"""
        row_count = 0
        y = ROWS - 1
        while y >= 0:
            if all(self.board[y]):
                # 删除这一行
                del self.board[y]
                # 在顶部添加新的一行
                self.board.insert(0, [0 for _ in range(COLS)])
                row_count += 1
                
                # 每清除一行就有80%概率触发恶作剧（增加整蛊频率）
                if random.random() < 0.8 and not self.prank_activated:
                    self.activate_prank()
                
                # 因为我们删除了一行，所以不需要减少y
            else:
                y -= 1
        
        # 更新消除行数和等级
        if row_count > 0:
            self.player['lines'] += row_count
            # 每消除10行升一级
            self.player['level'] = self.player['lines'] // 10 + 1
            # 根据等级调整下落速度
            self.drop_interval = max(100, 1000 - (self.player['level'] - 1) * 100)
            
            # 计算得分
            scores = {1: 40, 2: 100, 3: 300, 4: 1200}
            if row_count in scores:
                self.player['score'] += scores[row_count] * self.player['level']
            
            self.update_score()
    
    def update_score(self):
        """更新得分显示"""
        pass  # 在draw方法中处理
    
    def activate_prank(self):
        """激活整蛊"""
        self.prank_activated = True
        # 随机选择一种整蛊类型
        self.prank_type = random.randint(1, 5)  # 1-5种整蛊
        
        if self.prank_type == 5:
            # 山药效果：替换当前方块为特殊形状
            self.player['matrix'] = [
                [0, 0, 0, 0, 0],
                [0, 0, 8, 0, 0],
                [0, 8, 8, 8, 0],
                [8, 8, 8, 8, 8],
                [0, 0, 0, 0, 0]
            ]
        
        # 3秒后关闭整蛊
        pygame.time.set_timer(pygame.USEREVENT, 3000)
    
    def reset_game(self):
        """重置游戏"""
        self.board = self.create_matrix(COLS, ROWS)
        self.player['score'] = 0
        self.player['level'] = 1
        self.player['lines'] = 0
        self.player['next_piece'] = self.create_piece()
        self.drop_interval = 1000
        self.game_active = True
        self.player_reset()
    
    def handle_events(self):
        """处理事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.KEYDOWN:
                if self.game_active:
                    if event.key == pygame.K_LEFT:
                        self.player_move(-1)
                    elif event.key == pygame.K_RIGHT:
                        self.player_move(1)
                    elif event.key == pygame.K_DOWN:
                        self.player_drop()
                    elif event.key == pygame.K_UP:
                        self.player_rotate(1)
                    elif event.key == pygame.K_SPACE:
                        self.player_hard_drop()
                
                if event.key == pygame.K_r:
                    self.reset_game()
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                button_rect = pygame.Rect(SCREEN_WIDTH + 15, 450, 120, 40)
                if button_rect.collidepoint(event.pos):
                    self.game_active = not self.game_active
            
            elif event.type == pygame.USEREVENT:
                # 整蛊时间结束
                self.prank_activated = False
                self.prank_type = 0
                
                # 如果是山药效果，恢复正常的方块
                if self.prank_type == 5:
                    self.player_reset()
                
                # 停止计时器
                pygame.time.set_timer(pygame.USEREVENT, 0)
        
        return True
    
    def update(self):
        """更新游戏状态"""
        if not self.game_active:
            return
        
        current_time = pygame.time.get_ticks()
        delta_time = current_time - self.last_time
        self.last_time = current_time
        
        self.drop_counter += delta_time
        if self.drop_counter > self.drop_interval:
            self.player_drop()
    
    def run(self):
        """运行游戏"""
        self.last_time = pygame.time.get_ticks()
        running = True
        
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = TetrisGame()
    game.run()