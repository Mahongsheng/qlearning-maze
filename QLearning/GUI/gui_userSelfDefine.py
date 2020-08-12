from PyQt5.QtWidgets import QLabel, QComboBox, QPushButton, QMessageBox, QWidget, QGroupBox, QGridLayout, \
    QPlainTextEdit, QSpinBox
from PyQt5.QtCore import QBasicTimer, QRect
from PyQt5.QtGui import QFont
import numpy as np
from MAP.maze import Maze
from train_qtable import QTableModel
import time

from GUI.draw_ui import DrawUI


# GUI“用户自定义迷宫”Tab
# “用户自定义”标签页的实现，用户可以输入任意大小的迷宫，自定义火焰周期，训练次数上限。
# 之后进行训练，并以三种不同的速度查看完整的走迷宫结果
class UIUserDefine(QWidget):
    def __init__(self):
        super().__init__()
        self.model = None
        self.playing_index = -1
        self.problem_solving = False

    def init_ui(self):
        self.resize(1200, 680)

        self.timer = QBasicTimer()
        widget1 = QWidget(parent=self)
        widget1.setGeometry(QRect(30, 50, 800, 500))
        table_area = QGroupBox(parent=widget1)  # 图形显示区域
        table_area.setGeometry(QRect(widget1.x(), widget1.y(), widget1.width(), widget1.height()))

        self.Plot = DrawUI(width=3, height=3, dpi=100)
        gridlayout1 = QGridLayout(table_area)  # 继承容器groupBox
        gridlayout1.addWidget(self.Plot, 0, 1)

        pic_choose_label = QLabel(self)
        pic_choose_label.move(table_area.x() + table_area.width() + 30, table_area.y() + 20)
        pic_choose_label.setText("Input Maze：")
        pic_choose_label.setFont(QFont("Fixed", 10))
        pic_choose_label2 = QLabel(self)
        pic_choose_label2.move(pic_choose_label.geometry().x(), pic_choose_label.y() + pic_choose_label.height() + 20)
        pic_choose_label2.setText("（1 is space，0 is wall, 2 is grass, 3 is light）")
        pic_choose_label2.setFont(QFont("Fixed", 10))

        self.maze_input = QPlainTextEdit(parent=self)
        self.maze_input.setGeometry(
            QRect(pic_choose_label2.x(), pic_choose_label2.y() + pic_choose_label2.height() + 20, 250, 150))
        self.maze_input.setPlainText(
            '1, 0, 1, 1, 1, 1, 1,\r\n1, 1, 3, 0, 0, 1, 0,\r\n0, 0, 0, 1, 1, 1, 0,\r\n1, 1, 1, 1, 0, 0, 1,\r\n1, 0, 0, 0, 1, 1, 1,\r\n1, 0, 1, 1, 1, 2, 2,\r\n1, 1, 1, 0, 1, 1, 1,'
        )

        period_label = QLabel(parent=self)
        period_label.setText('Light Period:')
        period_label.setFont(QFont("Fixed", 10))
        period_label.move(self.maze_input.x(), self.maze_input.height() + self.maze_input.y() + 10)

        self.period_input = QSpinBox(parent=self)
        self.period_input.setValue(1)
        self.period_input.setFont(QFont("Fixed", 10))
        self.period_input.move(period_label.x() + period_label.width() + 15, period_label.y() - 2)

        period_label2 = QLabel(parent=self)
        period_label2.setText('*2')
        period_label2.setFont(QFont("Fixed", 10))
        period_label2.move(self.period_input.x() + self.period_input.width() - 40, self.period_input.y() + 2)

        maze_input_button = QPushButton(parent=self)
        maze_input_button.move(period_label.x() + period_label.width() + 15,
                               self.period_input.y() + self.period_input.height() + 10)
        maze_input_button.setText('Done')
        maze_input_button.setFont(QFont("Fixed", 10))
        maze_input_button.pressed.connect(self.pic_change)

        middle_x = self.maze_input.geometry().x() + self.maze_input.geometry().width() / 2

        train_epoch_label = QLabel(parent=self)
        train_epoch_label.setText('Training Count:')
        train_epoch_label.setFont(QFont("Fixed", 10))
        train_epoch_label.move(self.maze_input.x(), maze_input_button.height() + maze_input_button.y() + 40)

        self.epoch_input = QSpinBox(parent=self)
        self.epoch_input.move(train_epoch_label.x() + train_epoch_label.width() + 15, train_epoch_label.y() - 2)
        self.epoch_input.setValue(30)
        self.epoch_input.setFont(QFont("Fixed", 10))

        train_epoch_label2 = QLabel(parent=self)
        train_epoch_label2.setText('*1000')
        train_epoch_label2.setFont(QFont("Fixed", 10))
        train_epoch_label2.move(self.epoch_input.x() + self.epoch_input.width() - 40, self.epoch_input.y() + 2)

        self.solve_problem_button = QPushButton(parent=self)
        self.solve_problem_button.setText("Train Now")
        self.solve_problem_button.setFont(QFont("Fixed", 10))
        self.solve_problem_button.move(period_label.x() + period_label.width() + 15,
                                       train_epoch_label.y() + train_epoch_label.height() + 10)
        self.solve_problem_button.pressed.connect(self.solve_button_pressed)

        self.solve_test = QLabel(parent=self)  # 解答过程中的信息显示
        self.solve_test.setText("Training...")
        self.solve_test.setFont(QFont("Fixed", 10))
        self.solve_test.resize(250, self.solve_test.height())
        self.solve_test.move(middle_x - self.solve_test.geometry().width() / 2,
                             self.solve_problem_button.y() + self.solve_problem_button.height() + 10)
        self.solve_test.setHidden(True)

        speed_choose_label = QLabel(self)
        speed_choose_label.move(train_epoch_label.x(), self.solve_test.y() + self.solve_test.height() + 10)
        speed_choose_label.setText("Play Speed：")
        speed_choose_label.setFont(QFont("Fixed", 10))
        self.play_speed_combo = QComboBox(self)
        self.play_speed_combo.move(period_label.x() + period_label.width() + 15,
                                   speed_choose_label.geometry().y() - 2)
        self.play_speed_combo.addItems(["High", "Middle", "Low"])
        self.play_speed_combo.setFont(QFont("Fixed", 10))

        play_button = QPushButton(self)
        play_button.setText("Play Result Now!")
        play_button.setFont(QFont("Fixed", 10))
        play_button.move(period_label.x() + period_label.width() + 15,
                         self.play_speed_combo.geometry().y() + self.play_speed_combo.geometry().height() + 10)
        play_button.pressed.connect(self.play_button_pressed)

    def pic_change(self):
        self.timer.stop()
        current_text = self.maze_input.toPlainText()
        rows = current_text.split('\n')
        maze_map = []
        try:
            for row in rows:
                row_sp = row.split(',')
                row_list = []
                for c in row_sp:
                    c = c.strip()
                    if len(c) == 0:
                        continue
                    else:
                        row_list.append(int(c))
                maze_map.append(row_list)
        except:
            QMessageBox.information(self, "Warning", "Invalid Input.", QMessageBox.Ok | QMessageBox.Close,
                                    QMessageBox.Close)
            return

        maze_len = len(maze_map[0])
        for i in range(1, len(maze_map)):
            if len(maze_map[i]) != maze_len:
                QMessageBox.information(self, "Warning", "Error，each row should have the same number of columns.",
                                        QMessageBox.Ok | QMessageBox.Close,
                                        QMessageBox.Close)
                return

        my_maze = Maze(maze_map=np.array(maze_map), period=self.period_input.value() * 2)
        self.model = QTableModel(my_maze)

        # self.model.play_game((0, 0), 0)
        self.Plot.draw_root(self.model.my_maze, (0, 0), 1, 0, False)
        self.Plot.draw_qtable(qtable_model=self.model,
                              time_=self.model.my_maze.period - 1 if self.model.my_maze.period != 0 else 0,
                              fire_flag=True)

    def play_button_pressed(self):
        if self.model == None:
            QMessageBox.information(self, "Tip", "Please input the maze first.", QMessageBox.Ok | QMessageBox.Close,
                                    QMessageBox.Close)
            return

        self.model.play_game((0, 0), 0)
        speed_text = self.play_speed_combo.currentText()
        self.playing_index = 0
        if speed_text == "High":
            self.timer.start(100, self)
        elif speed_text == "Middle":
            self.timer.start(500, self)
        else:
            self.timer.start(1500, self)

    def timerEvent(self, event):
        if event.timerId() == self.timer.timerId():
            period = self.model.my_maze.period
            if period != 0 and (self.playing_index % period) >= period / 2:
                fire_flag = True
            else:
                fire_flag = False

            self.Plot.draw_qtable(self.model, self.playing_index % period if period != 0 else 0, fire_flag)
            self.Plot.draw_root(self.model.my_maze, (0, 0), self.playing_index, period, fire_flag)

            self.playing_index = self.playing_index + 1

            if self.playing_index >= len(self.model.my_maze.visited) + 2:
                self.playing_index = 0
                # print("up",self.playing_index)
        else:
            super(UIUserDefine, self).timerEvent(event)

    def solve_button_pressed(self):
        if self.problem_solving:
            return
        if type(self.model) == type(None):
            QMessageBox.information(self, "Tip", "Please input the maze first.", QMessageBox.Ok | QMessageBox.Close,
                                    QMessageBox.Close)
            return

        self.problem_solving = True
        self.playing_index = -1
        self.solve_test.setHidden(False)
        self.timer.stop()
        self.repaint()

        train_epoch = self.epoch_input.value() * 1000
        start_time = time.time()
        # path = "tangrams\\" + self.parent().pic_choose_combo.currentText() + ".png"
        self.model.train(output_line=self.solve_test, main_ui=self, epoch_N=train_epoch)
        end_time = time.time()

        QMessageBox.information(self, "Tip", "Training finished，spend：%.3f s" % (end_time - start_time),
                                QMessageBox.Ok | QMessageBox.Close, QMessageBox.Close)

        self.Plot.draw_qtable(qtable_model=self.model,
                              time_=self.model.my_maze.period - 1 if self.model.my_maze.period != 0 else 0,
                              fire_flag=True)
        self.problem_solving = False
        self.solve_test.setHidden(True)
