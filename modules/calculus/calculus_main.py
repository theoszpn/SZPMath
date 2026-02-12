from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget,
                               QPushButton, QFrame)

from .function_plotter import FunctionPlotterPage
from .limits_continuity import LimitsPage
from .derivatives import DerivativesPage
from .integrals import IntegralsPage

class CalculusModule(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.tab_bar = QFrame()
        self.tab_bar.setStyleSheet("background-color: #ecf0f1; border-bottom: 1px solid #bdc3c7;")
        self.tab_layout = QHBoxLayout(self.tab_bar)
        self.tab_layout.setContentsMargins(10, 5, 10, 5)

        self.btn_plot = self.create_tab_button("Tracé de Courbes")
        self.btn_limits = self.create_tab_button("Limites & Continuité")
        self.btn_derivatives = self.create_tab_button("Dérivées & Études")
        self.btn_integrals = self.create_tab_button("Intégrales")

        self.tab_layout.addWidget(self.btn_plot)
        self.tab_layout.addWidget(self.btn_limits)
        self.tab_layout.addWidget(self.btn_derivatives)
        self.tab_layout.addWidget(self.btn_integrals)
        self.tab_layout.addStretch()

        self.stack = QStackedWidget()

        self.page_plot = FunctionPlotterPage()
        self.page_limits = LimitsPage()
        self.page_derivatives = DerivativesPage()
        self.page_integrals = IntegralsPage()


        self.stack.addWidget(self.page_plot)
        self.stack.addWidget(self.page_limits)
        self.stack.addWidget(self.page_derivatives)
        self.stack.addWidget(self.page_integrals)

        self.btn_plot.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        self.btn_limits.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        self.btn_derivatives.clicked.connect(lambda: self.stack.setCurrentIndex(2))
        self.btn_integrals.clicked.connect(lambda: self.stack.setCurrentIndex(3))

        self.layout.addWidget(self.tab_bar)
        self.layout.addWidget(self.stack, 1)

    def create_tab_button(self, text):
        btn = QPushButton(text)
        btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-bottom: 3px solid transparent;
                padding: 10px 20px;
                font-weight: bold;
                color: #2c3e50;
            }
            QPushButton:hover { background-color: #dcdde1; }
            QPushButton:focus { border-bottom: 3px solid #e74c3c; color: #e74c3c; }
        """)
        return btn