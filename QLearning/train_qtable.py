from MAP.maze import Maze, ACTIONS
from GUI.draw import draw_table_root_by_time
from MAP.maze_map import Mazes

import random
import numpy as np
import matplotlib.pyplot as plt

NUM_ACTION = 4  # 动作数量
epoch_num = 30000  # 训练次数


#  Q表类的实现，Q表类有Q值的存储，决策的进行，Q表的学习等功能函数，进行预测和学习时会与迷宫（“环境”）进行交互，对其输入动作，得到反馈
class QTableModel(object):
    def __init__(self, my_maze, epsilon=0.1, learning_rate=0.1, gamma=0.9):
        self.Q_table = dict()
        self.my_maze = my_maze  # 迷宫
        self.epsilon_ = epsilon  # 探索因子，通常设置为0.1，意味着在每10次action中，有一次汽车将采取完全随机的动作
        self.learning_rate = learning_rate  # 学习率
        self.gamma = gamma  # 折现系数
        self.hsize = my_maze.maze.size // 2

    # 获取Q表的值
    def q_value(self, state):
        return np.array([self.Q_table.get((state, action), 0.0) for action in ACTIONS])

    # 预测下一个动作
    def predict(self, state):
        return ACTIONS[np.argmax(self.q_value(state))]

    # 开始训练
    def train(self, output_line=None, main_ui=None, epoch_N=epoch_num):
        self.Q_table = dict()
        win_history = []
        win_rate = 0.0  # 胜率
        # 训练的次数
        for epoch in range(epoch_N):
            if self.my_maze.period == 0:
                car_cell = random.choice(self.my_maze.free_cells)
            else:
                car_cell = (0, 0)
            self.my_maze.reset(car_cell, 0)
            game_over = False

            state = self.my_maze.get_current_state_simple()

            n_episodes = 0
            while not game_over:
                valid_actions = self.my_maze.valid_actions()
                if not valid_actions: break
                state_now = state

                # epsilon-贪心算法
                if np.random.rand() < self.epsilon_:
                    action = random.choice(valid_actions)
                else:
                    action = self.predict(state_now)

                # 实施action
                state_next, reward, game_status = self.my_maze.act(action,
                                                                   self.my_maze.get_current_state_simple)

                if (state, action) not in self.Q_table.keys():  # 确保存在值(state, action)以避免密钥错误
                    self.Q_table[(state, action)] = 0.0

                max_next_Q = max([self.Q_table.get((state_next, a), 0.0) for a in ACTIONS])
                self.Q_table[(state, action)] += self.learning_rate * (
                        reward + self.gamma * max_next_Q - self.Q_table[(state, action)])

                if game_status == 'win':
                    win_history.append(1)
                    game_over = True
                elif game_status == 'lose':
                    win_history.append(0)
                    game_over = True
                else:
                    game_over = False

                state = state_next

                n_episodes += 1

            if len(win_history) > self.hsize:
                win_rate = sum(win_history[-self.hsize:]) / self.hsize

            template = "Epoch: {:03d}/{:d}    Episodes: {:d}  Win count: {:d} Win rate: {:.3f}"
            print(template.format(epoch, epoch_N - 1, n_episodes, sum(win_history), win_rate))
            if type(output_line) != type(None) and type(main_ui) != type(None):
                output_line.setText(template.format(epoch, epoch_N - 1, n_episodes, sum(win_history), win_rate))
                if epoch % 200 == 0:
                    main_ui.repaint()

            # 测试是否训练成熟
            if win_rate > 0.9: self.epsilon_ = 0.05
            if self.my_maze.period == 0:
                if sum(win_history[-self.hsize:]) == self.hsize and self.completion_check():
                    print("Reached 100%% win rate at epoch: %d" % (epoch,))
                    break
            else:
                if win_rate > 0.8 and self.play_game((0, 0), 0):
                    # if sum(win_history[-self.hsize:]) == self.hsize and self.play_game((0, 0), 0):
                    print("Reached 100%% win rate at epoch: %d" % (epoch,))
                    break

    # 完成度检测，检验每一个cell的动作是否不会出现任何错误
    def completion_check(self):
        if self.my_maze.period == 0:
            period_temp = 1
        else:
            period_temp = self.my_maze.period
        for time_ in range(period_temp):
            for cell in self.my_maze.free_cells:
                if not self.my_maze.valid_actions(cell):
                    return False
                if not self.play_game(cell, time_):
                    return False
        return True

    # 开始新的一轮游戏，其中car_cell为汽车的起始细胞
    def play_game(self, car_cell, time):
        self.my_maze.reset(car_cell, time)
        env_state = self.my_maze.get_current_state_simple()  # 得到迷宫状态
        while True:
            prev_env_state = env_state  # 得到上一个迷宫状态
            # 得到下一个动作：上下左右
            action = self.predict(prev_env_state)

            # 应用动作，获得奖励和新的状态
            env_state, reward, game_status = self.my_maze.act(action, self.my_maze.get_current_state_simple)
            if game_status == 'win':
                return True
            elif game_status == 'lose':
                return False

    # 存储表
    def save_table(self, filename):
        # with open(filename,'w') as json_file:
        #   json.dump(self.Q_table, json_file, ensure_ascii=False)
        np.save(filename, self.Q_table)

    # 加载表
    def load_table(self, filename):
        self.Q_table = np.load(filename).item()
        return self.Q_table


if __name__ == "__main__":
    maze_name = 'maze11_1'
    maze = np.array(Mazes[maze_name])

    my_maze = Maze(maze_map=maze, period=2)
    model = QTableModel(my_maze)
    model.train()
    model.save_table("Saved_QTable/" + maze_name)
    # model.load_table('saved_qtable/'+maze_name+'.npy')

    model.play_game((0, 0), 0)
    draw_table_root_by_time(model, model.my_maze, (0, 0))
    plt.show()
    print()
