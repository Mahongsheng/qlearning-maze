from PyQt5.QtWidgets import QTabWidget, QMainWindow, QDesktopWidget, QApplication
import sys
from GUI.gui_basic import GUIBasic
from GUI.gui_userSelfDefine import UIUserDefine


# 这是一个GUI类
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(1200, 680)  # 设置界面大小
        self.center()
        self.setWindowTitle('Maze Map')

        self.tabW = QTabWidget(parent=self)
        ui_user_d = UIUserDefine()
        ui_basic = GUIBasic()

        self.tabW.addTab(ui_basic, "Existing Maze")  # 设置两个Tab框
        self.tabW.addTab(ui_user_d, "User Defined Maze")
        self.tabW.resize(1200, 680)
        ui_basic.init_ui()
        ui_user_d.init_ui()

        self.show()

    def center(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2,
                  (screen.height() - size.height()) / 10)


if __name__ == "__main__":
    app = QApplication([])
    ui = MainWindow()
    sys.exit(app.exec_())
