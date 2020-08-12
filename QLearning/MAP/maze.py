import numpy as np
import matplotlib.pyplot as plt

# 上下左右
RIGHT = 0
UP = 1
LEFT = 2
DOWN = 3
ACTIONS = [RIGHT, UP, LEFT, DOWN]

REWARD = {"move": -0.05, "finish": 1.0, "wall": -0.85, "bound": -0.85, "repeat": -0.3, "dead": -2}


# REWARD = {"move":-0.05, "finish":1.0, "wall":-0.3, "bound":-0.3, "repeat":-0.3, "dead":-2}

# 这是一个迷宫类
# 迷宫信息用一个二维数组表示，数组中的每个数代表一个方格，数字值代表方格类型（如0表示墙, 2表示陷阱, 3表示火）
# 火在每个周期的后半段出现，前半段消失，周期必须为偶数
class Maze(object):

    def __init__(self, period, maze_map=None):

        # 检测周期的类型是否正确
        if not isinstance(period, int):
            raise TypeError('Period should be int.')
        if not period % 2 == 0:
            raise TypeError('Period should be even.')

        self.period = period
        self.time = 0
        self.maze = np.array(maze_map, dtype=np.int)
        self.aim = (self.maze.shape[0] - 1, self.maze.shape[1] - 1)
        self.free_cells = [(i, j) for i in range(self.maze.shape[0]) for j in range(self.maze.shape[1]) if
                           self.maze[i, j] == 1 or self.maze[i, j] == 3]
        self.trap = [(i, j) for i in range(self.maze.shape[0]) for j in range(self.maze.shape[1]) if
                     self.maze[i, j] == 2]  # 老鼠夹
        self.fire = [(i, j) for i in range(self.maze.shape[0]) for j in range(self.maze.shape[1]) if
                     self.maze[i, j] == 3]  # 火
        if len(self.fire) == 0:
            self.period = 0
        self.car = (0, 0)
        self.score = 0
        self.min_reward = -0.5 * self.maze.shape[0] * self.maze.shape[1]
        self.visited = []
        self.reset()

    # 根据当前状态来执行动作
    def act(self, action, get_state_temp):
        rat_i, rat_j = self.car
        next_i, next_j = self.move2next(rat_i, rat_j, action)
        nrow, ncol = self.maze.shape

        game_status = ""
        if next_i >= nrow or next_j >= ncol or next_i < 0 or next_j < 0:
            award = REWARD['bound']
            next_i = rat_i
            next_j = rat_j
            self.visited.append((next_i, next_j))
            game_status = "blocked"
        elif self.maze[next_i, next_j] == 0:
            award = REWARD['wall']
            next_i = rat_i
            next_j = rat_j
            self.visited.append((next_i, next_j))
            game_status = "blocked"
        elif next_i == self.aim[0] and next_j == self.aim[1]:
            award = REWARD['finish']
            game_status = "win"
        elif (next_i, next_j) in self.visited:
            award = REWARD['repeat']
            self.visited.append((next_i, next_j))
            game_status = "normal"
        elif (next_i, next_j) in self.trap:
            award = REWARD['dead']
            game_status = "lose"
        elif (next_i, next_j) in self.fire and self.period != 0 and ((self.time + 1) % self.period) >= self.period / 2:
            award = REWARD['dead']
            game_status = "lose"
        else:
            award = REWARD['move']
            self.visited.append((next_i, next_j))
            game_status = "normal"

        if game_status == "blocked" and (rat_i, rat_j) in self.fire and self.period != 0 and (
                (self.time + 1) % self.period) >= self.period / 2:
            award = REWARD['dead']
            game_status = "lose"

        if self.period != 0:
            self.time = (self.time + 1) % self.period
        self.score += award  # 奖励
        self.car = (next_i, next_j)

        if self.score < self.min_reward:
            game_status = "lose"

        return get_state_temp(), award, game_status

    # 根据当前位置与动作获得下一个位置
    def move2next(self, i, j, action):
        if action == UP:
            next_i = i - 1
            next_j = j
        elif action == RIGHT:
            next_i = i
            next_j = j + 1
        elif action == LEFT:
            next_i = i
            next_j = j - 1
        elif action == DOWN:
            next_i = i + 1
            next_j = j
        return next_i, next_j

    # 重置地图
    def reset(self, rat=(0, 0), time=0):
        self.time = time
        self.car = rat
        self.score = 0
        self.visited = []

    # 获得当前坐标点的类型
    def get_current_state(self):
        maze_temp = np.copy(np.array(self.maze, dtype=np.float))
        maze_temp[self.car[0], self.car[1]] = 0.5  # 老鼠所在位置设为0.5
        maze_temp = maze_temp.reshape([1, -1])
        return maze_temp

    def get_current_state_simple(self):
        return (*self.car, self.time)

    # 重新验证动作，当汽车运动到地图边缘时，在动作列表中删除可能导致越界的动作
    def valid_actions(self, cell=None):
        if cell is None:
            row, col = self.car
        else:
            row, col = cell
        actions = [RIGHT, UP, LEFT, DOWN]
        n_rows, n_cols = self.maze.shape
        if row == 0:
            actions.remove(UP)
        elif row == n_rows - 1:
            actions.remove(DOWN)

        if col == 0:
            actions.remove(LEFT)
        elif col == n_cols - 1:
            actions.remove(RIGHT)

        if row > 0 and self.maze[row - 1, col] == 0:
            actions.remove(UP)
        if row < n_rows - 1 and self.maze[row + 1, col] == 0:
            actions.remove(DOWN)

        if col > 0 and self.maze[row, col - 1] == 0:
            actions.remove(LEFT)
        if col < n_cols - 1 and self.maze[row, col + 1] == 0:
            actions.remove(RIGHT)

        return actions


# 展示该迷宫
def show_maze(Maze):
    plt.grid(True)
    nrows, ncols = Maze.maze.shape
    ax = plt.gca()
    ax.set_xticks(np.arange(0.5, nrows, 1))
    ax.set_yticks(np.arange(0.5, ncols, 1))
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    canvas = np.copy(np.array(Maze.maze, dtype=np.float))
    for row, col in Maze.visited:
        canvas[row, col] = 0.6
    rat_row, rat_col = Maze.rat
    canvas[rat_row, rat_col] = 0.3  # rat cell
    canvas[nrows - 1, ncols - 1] = 0.9  # cheese cell
    img = plt.imshow(canvas, interpolation='none', cmap='gray')
    return img

# if __name__ == "__main__":
#     maze = np.array([
#         [1., 0., 1., 1., 1., 1., 1., 1.],
#         [1., 0., 1., 0, 1., 0., 1., 1.],
#         [1., 1., 1., 1., 0., 1., 0., 1.],
#         [1., 1., 1., 0., 1., 1., 1., 1.],
#         [0, 1., 0., 1., 1., 1., 1., 1.],
#         [1., 1., 1., 0., 1., 0., 0., 0.],
#         [1., 1., 1., 0., 1., 1., 1., 1.],
#         [1., 1., 1., 1., 0., 1., 1., 1.]
#     ])
#
#     my_maze = Maze(maze_map=maze, period=2)
#     my_maze.act(DOWN)
#     my_maze.act(LEFT)
#     my_maze.act(RIGHT)
#     my_maze.act(RIGHT)
#     my_maze.act(UP)
#
#     show_maze(my_maze)
#     plt.show()
#     print()
