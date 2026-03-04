import sys
import os

basedir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(basedir)

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget,
                               QVBoxLayout, QHBoxLayout, QPushButton,
                               QLabel, QStackedWidget, QFrame)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, QSize


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


from modules.algebra.algebra_main import AlgebraModule
from modules.statisitcs.statistics_main import StatisticsModule
from modules.probas.probabilities_main import ProbabilitiesModule
from modules.calculus.calculus_main import CalculusModule
from modules.dashboard import DashboardPage

class SZPMath(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SZPMath")

        icon_p = resource_path(os.path.join("assets", "SZPMath_icon.ico"))
        if os.path.exists(icon_p):
            self.setWindowIcon(QIcon(icon_p))

        self.setStyleSheet("""
            QMainWindow { background-color: #f5f6fa; }
            #Sidebar { background-color: #2f3640; border-right: 1px solid #dcdde1; }
            QPushButton {
                background-color: transparent; color: #f5f6fa;
                border: none; padding: 15px; text-align: left;
                font-size: 14px; border-radius: 5px; outline: none;
            }
            QPushButton:hover { background-color: #353b48; }
            #ActiveBtn { background-color: #0097e6; font-weight: bold; }
        """)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        self.layout = QHBoxLayout(main_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.sidebar = QFrame()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFixedWidth(220)
        self.sidebar.setVisible(False)
        sidebar_layout = QVBoxLayout(self.sidebar)


        self.lbl_logo = QLabel("∑ SZPMath")
        self.lbl_logo.setStyleSheet(
            "color: white; font-size: 22px; margin: 20px 0; font-weight: bold; padding-left: 15px;")
        sidebar_layout.addWidget(self.lbl_logo)


        self.btn_alg = QPushButton("  Algèbre Linéaire")
        self.btn_stat = QPushButton("  Statistiques")
        self.btn_proba = QPushButton("  Probabilités")
        self.btn_calc = QPushButton("  Calculus")

        for btn in [self.btn_alg, self.btn_stat, self.btn_proba, self.btn_calc]:
            sidebar_layout.addWidget(btn)

        sidebar_layout.addStretch()

        self.btn_back_home = QPushButton()
        icon_path = resource_path(os.path.join("assets", "icon_home.png"))
        if os.path.exists(icon_path):
            self.btn_back_home.setIcon(QIcon(icon_path))
            self.btn_back_home.setIconSize(QSize(28, 28))

        self.btn_back_home.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_back_home.setFixedSize(45, 45)
        self.btn_back_home.setStyleSheet("""
            QPushButton {
                color: white;
                border: none;
                padding: 0px;
                text-align: center;
                font-size: 14px;
                font-weight: bold;
                border-radius: 10px;
                margin-left: 2px;
            }
            QPushButton:hover {
                background-color: #353b48;
            }
        """)

        sidebar_layout.addWidget(self.btn_back_home)

        self.content = QStackedWidget()

        self.dashboard = DashboardPage()
        self.content.addWidget(self.dashboard)

        self.module_algebra = AlgebraModule()
        self.module_stat = StatisticsModule()
        self.module_probas = ProbabilitiesModule()
        self.module_calculus = CalculusModule()

        self.content.addWidget(self.module_algebra)
        self.content.addWidget(self.module_stat)
        self.content.addWidget(self.module_probas)
        self.content.addWidget(self.module_calculus)

        self.layout.addWidget(self.sidebar, 0)
        self.layout.addWidget(self.content, 1)

        self.dashboard.module_selected.connect(self.switch_to_module)
        self.btn_back_home.clicked.connect(self.show_dashboard)

        self.btn_alg.clicked.connect(lambda: self.switch_to_module(1))
        self.btn_stat.clicked.connect(lambda: self.switch_to_module(2))
        self.btn_proba.clicked.connect(lambda: self.switch_to_module(3))
        self.btn_calc.clicked.connect(lambda: self.switch_to_module(4))

    def switch_to_module(self, index):
        self.content.setCurrentIndex(index)
        self.sidebar.setVisible(True)

    def show_dashboard(self):
        self.content.setCurrentIndex(0)
        self.sidebar.setVisible(False)

if __name__ == "__main__":
    if sys.platform == 'win32':
        import ctypes
        try:
            app_id = u'szp.math.software.alpha.1'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
        except Exception as e:
            print(f"Erreur ctypes : {e}")

    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
    app = QApplication(sys.argv)
    app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)
    path_to_ico = resource_path(os.path.join("assets", "SZPMath_icon.ico"))

    if os.path.exists(path_to_ico):
        app_icon = QIcon(path_to_ico)
        app.setWindowIcon(app_icon)

    window = SZPMath()
    window.setWindowState(Qt.WindowState.WindowMaximized)
    window.show()
    sys.exit(app.exec())