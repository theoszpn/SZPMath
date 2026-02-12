from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget,
                               QPushButton, QFrame)

from .anal_combinaison import CombinatoricsPage
from .discrete_laws import DiscreteLawsPage
from .continuous_laws import ContinuousLawsPage

class ProbabilitiesModule(QWidget):
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

        self.btn_comb = self.create_tab_button("Analyse Combinatoire")
        self.btn_discrete = self.create_tab_button("Lois Discrètes")
        self.btn_continue = self.create_tab_button("Lois Continues")

        self.tab_layout.addWidget(self.btn_comb)
        self.tab_layout.addWidget(self.btn_discrete)
        self.tab_layout.addWidget(self.btn_continue)
        self.tab_layout.addStretch()

        self.stack = QStackedWidget()

        self.page_combinaison = CombinatoricsPage()
        self.page_discrete = DiscreteLawsPage()
        self.page_continue = ContinuousLawsPage()

        self.stack.addWidget(self.page_combinaison)
        self.stack.addWidget(self.page_discrete)
        self.stack.addWidget(self.page_continue)

        self.btn_comb.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        self.btn_discrete.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        self.btn_continue.clicked.connect(lambda: self.stack.setCurrentIndex(2))

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
            QPushButton:focus { border-bottom: 3px solid #3498db; color: #3498db; }
        """)
        return btn