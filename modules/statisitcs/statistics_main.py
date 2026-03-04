from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget,
                               QPushButton, QFrame)
from .descriptives import DescriptiveStatsPage
from .estimations import EstimationsPage
from .testnormalite import TestsNormalitePage
from .test_independance import ChiSquareIndependancePage
from .test_homogeneite import ChiSquareHomoPage
from .test_adequation import ChiSquareAdequacyPage
from .test_correlation import CorrelationPearsonPage

class StatisticsModule(QWidget):
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

        self.btn_descriptive = self.create_tab_button("Statistiques Descriptives")
        self.btn_estimations = self.create_tab_button("Estimations")
        self.btn_test_norm = self.create_tab_button("Test Normalité")
        self.btn_test_inde = self.create_tab_button("Test indépendance")
        self.btn_test_homo = self.create_tab_button("Test homogénéité")
        self.btn_test_adequation = self.create_tab_button("Test adéquation")
        self.btn_test_correl = self.create_tab_button("Test corrélation")

        self.tab_layout.addWidget(self.btn_descriptive)
        self.tab_layout.addWidget(self.btn_estimations)
        self.tab_layout.addWidget(self.btn_test_norm)
        self.tab_layout.addWidget(self.btn_test_inde)
        self.tab_layout.addWidget(self.btn_test_homo)
        self.tab_layout.addWidget(self.btn_test_adequation)
        self.tab_layout.addWidget(self.btn_test_correl)
        self.tab_layout.addStretch()

        self.stack = QStackedWidget()

        self.page_descriptive = DescriptiveStatsPage()
        self.page_estimations = EstimationsPage()
        self.page_test_norm = TestsNormalitePage()
        self.page_test_inde = ChiSquareIndependancePage()
        self.page_test_homo = ChiSquareHomoPage()
        self.page_test_adequation = ChiSquareAdequacyPage()
        self.page_test_correl = CorrelationPearsonPage()

        self.stack.addWidget(self.page_descriptive)
        self.stack.addWidget(self.page_estimations)
        self.stack.addWidget(self.page_test_norm)
        self.stack.addWidget(self.page_test_inde)
        self.stack.addWidget(self.page_test_homo)
        self.stack.addWidget(self.page_test_adequation)
        self.stack.addWidget(self.page_test_correl)

        self.btn_descriptive.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        self.btn_estimations.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        self.btn_test_norm.clicked.connect(lambda: self.stack.setCurrentIndex(2))
        self.btn_test_inde.clicked.connect(lambda: self.stack.setCurrentIndex(3))
        self.btn_test_homo.clicked.connect(lambda: self.stack.setCurrentIndex(4))
        self.btn_test_adequation.clicked.connect(lambda: self.stack.setCurrentIndex(5))
        self.btn_test_correl.clicked.connect(lambda: self.stack.setCurrentIndex(6))

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