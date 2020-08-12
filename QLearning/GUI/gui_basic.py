from PyQt5.QtWidgets import QLabel, QComboBox, QPushButton, QMessageBox, QWidget, QGroupBox, QGridLayout
from PyQt5.QtCore import QBasicTimer, QRect
from PyQt5.QtGui import QFont
import numpy as np
from MAP.maze_map import Mazes
from MAP.maze import Maze
from train_qtable import QTableModel
import time

from GUI.draw_ui import DrawUI


# GUI“已有界面”Tab
class GUIBasic(QWidget):
    def __init__(self):
        super().__init__()
        self.model = None

    def init_ui(self):
        self.resize(1200, 680)

        self.pic_list = ['maze7_1', 'maze7_2', 'maze7_3', 'maze10_1', 'maze10_2', 'maze10_3', 'maze11_1']
        self.timer = QBasicTimer()
        widget1 = QWidget(parent=self)
        widget1.setGeometry(QRect(30, 50, 800, 500))
        table_area = QGroupBox(parent=widget1)  # 图形显示区域
        table_area.setGeometry(QRect(widget1.x(), widget1.y(), widget1.width(), widget1.height()))

        self.Plot = DrawUI(width=3, height=3, dpi=100)
        gridlayout1 = QGridLayout(table_area)  # 继承容器groupBox
        gridlayout1.addWidget(self.Plot, 0, 1)

        pic_choose_label = QLabel(self)
        pic_choose_label.move(table_area.x() + table_area.width(), table_area.y() + 80)
        pic_choose_label.setText("Choose Maze：")
        pic_choose_label.setFont(QFont("Fixed", 10))
        self.pic_choose_combo = QComboBox(self)
        self.pic_choose_combo.move(pic_choose_label.geometry().x() + pic_choose_label.geometry().width() + 30,
                                   pic_choose_label.geometry().y() - 8)
        self.pic_choose_combo.resize(100, self.pic_choose_combo.geometry().height())
        self.pic_choose_combo.addItems(self.pic_list)
        self.pic_choose_combo.currentIndexChanged.connect(self.pic_change)
        self.pic_choose_combo.setFont(QFont("Fixed", 10))
        self.pic_change()

        middle_x = (
                           pic_choose_label.geometry().x() + self.pic_choose_combo.geometry().x() + self.pic_choose_combo.geometry().width()) / 2

        self.playing_index = -1
        self.problem_solving = False

        self.solve_problem_button = QPushButton(parent=self)
        self.solve_problem_button.setText("Train Now")
        self.solve_problem_button.move(pic_choose_label.geometry().x() + pic_choose_label.geometry().width() + 30,
                                       self.pic_choose_combo.y() + self.pic_choose_combo.height() + 100)
        self.solve_problem_button.pressed.connect(self.solve_button_pressed)
        self.solve_problem_button.setFont(QFont("Fixed", 10))

        self.solve_test = QLabel(parent=self)  # 解答过程中的信息显示
        self.solve_test.setText("Training...")
        self.solve_test.resize(400, self.solve_test.height())
        self.solve_test.setFont(QFont("Fixed", 9))
        self.solve_test.move(table_area.x() + table_area.width() - 20,
                             self.solve_problem_button.geometry().y() + self.solve_problem_button.geometry().height() + 20)
        self.solve_test.setHidden(True)

        speed_choose_label = QLabel(self)
        speed_choose_label.move(table_area.x() + table_area.width(), self.solve_test.geometry().y() + 40)
        speed_choose_label.setText("Play Speed：")
        speed_choose_label.setFont(QFont("Fixed", 10))
        self.play_speed_combo = QComboBox(self)
        self.play_speed_combo.move(speed_choose_label.geometry().x() + speed_choose_label.geometry().width() + 30,
                                   speed_choose_label.geometry().y() - 2)
        self.play_speed_combo.addItems(["High", "Middle", "Low"])
        self.play_speed_combo.setFont(QFont("Fixed", 10))

        play_button = QPushButton(self)
        play_button.setText("Play Result Now!")
        play_button.move(pic_choose_label.geometry().x() + pic_choose_label.geometry().width() + 30,
                         self.play_speed_combo.geometry().y() + self.play_speed_combo.geometry().height() + 40)
        play_button.pressed.connect(self.play_button_pressed)
        play_button.setFont(QFont("Fixed", 10))

    def pic_change(self):
        self.timer.stop()
        current_text = self.pic_choose_combo.currentText()
        maze = Mazes[current_text]
        my_maze = Maze(maze_map=np.array(maze), period=2)
        self.model = QTableModel(my_maze)

        # try:
        #     self.model.load_table('./Saved_QTable/' + current_text + '.npy')
        # except:
        #     QMessageBox.information(self, "提示", "没找到Q表保存文件", QMessageBox.Ok | QMessageBox.Close,
        #                             QMessageBox.Close)

        self.model.play_game((0, 0), 0)
        self.Plot.draw_root(self.model.my_maze, (0, 0), 1, 0, False)
        self.Plot.draw_qtable(qtable_model=self.model,
                              time_=self.model.my_maze.period - 1 if self.model.my_maze.period != 0 else 0,
                              fire_flag=True)

    def play_button_pressed(self):
        if self.model == None:
            QMessageBox.information(self, "Tip", "Please choose the Maze first.", QMessageBox.Ok | QMessageBox.Close,
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
            super(GUIBasic, self).timerEvent(event)

    def solve_button_pressed(self):
        if self.problem_solving:
            return
        if type(self.model) == type(None):
            QMessageBox.information(self, "Tip", "Please choose the Maze first.", QMessageBox.Ok | QMessageBox.Close,
                                    QMessageBox.Close)
            return

        self.problem_solving = True
        self.playing_index = -1
        self.solve_test.setHidden(False)
        self.timer.stop()
        self.repaint()

        start_time = time.time()
        # path = "tangrams\\" + self.parent().pic_choose_combo.currentText() + ".png"
        self.model.train(output_line=self.solve_test, main_ui=self)
        end_time = time.time()

        QMessageBox.information(self, "Tip", "Training finished，spend：%.3f s" % (end_time - start_time),
                                QMessageBox.Ok | QMessageBox.Close, QMessageBox.Close)

        self.Plot.draw_qtable(qtable_model=self.model,
                              time_=self.model.my_maze.period - 1 if self.model.my_maze.period != 0 else 0,
                              fire_flag=True)
        self.problem_solving = False
        self.solve_test.setHidden(True)
