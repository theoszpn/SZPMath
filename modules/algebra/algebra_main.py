from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget,
                               QPushButton, QFrame, QLabel)
from PySide6.QtCore import Qt

from .matrix_calc import MatrixCalcPage
from .system_gauss import GaussSolverPage
from .cramer_solver import CramerSolverPage
from .vector_spaces import VectorSpacesPage
from .diagonalisation import DiagonalizationPage
from .visualisation_2d import Visualisation2DPage
from .visualisation_3d import Visualisation3DPage

class AlgebraModule(QWidget):
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

        self.btn_calc = self.create_tab_button("Calcul Matriciel")
        self.btn_gauss = self.create_tab_button("Systèmes Gauss")
        self.btn_cramer = self.create_tab_button("Systémes/formules Cramer")
        self.btn_vector = self.create_tab_button("Espaces Vectoriels")
        self.btn_diago = self.create_tab_button("Diagonalisation")
        self.btn_visualisation_2d = self.create_tab_button("Visualisation 2D")
        self.btn_visualisation_3d = self.create_tab_button("Visualisation 3D")

        self.tab_layout.addWidget(self.btn_calc)
        self.tab_layout.addWidget(self.btn_gauss)
        self.tab_layout.addWidget(self.btn_cramer)
        self.tab_layout.addWidget(self.btn_vector)
        self.tab_layout.addWidget(self.btn_diago)
        self.tab_layout.addWidget(self.btn_visualisation_2d)
        self.tab_layout.addWidget(self.btn_visualisation_3d)
        self.tab_layout.addStretch()

        self.stack = QStackedWidget()

        self.page_matrix = MatrixCalcPage()
        self.page_gauss = GaussSolverPage()
        self.page_cramer = CramerSolverPage()
        self.page_vector = VectorSpacesPage()
        self.page_diago = DiagonalizationPage()
        self.page_visualisation_2d = Visualisation2DPage()
        self.page_visualisation_3d = Visualisation3DPage()

        temp_layout = QVBoxLayout(self.page_gauss)
        temp_layout.addWidget(QLabel("Interface Pivot de Gauss (En développement)"),
                              alignment=Qt.AlignmentFlag.AlignCenter)

        self.stack.addWidget(self.page_matrix)
        self.stack.addWidget(self.page_gauss)
        self.stack.addWidget(self.page_cramer)
        self.stack.addWidget(self.page_vector)
        self.stack.addWidget(self.page_diago)
        self.stack.addWidget(self.page_visualisation_2d)
        self.stack.addWidget(self.page_visualisation_3d)

        self.btn_calc.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        self.btn_gauss.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        self.btn_cramer.clicked.connect(lambda : self.stack.setCurrentIndex(2))
        self.btn_vector.clicked.connect(lambda : self.stack.setCurrentIndex(3))
        self.btn_diago.clicked.connect(lambda : self.stack.setCurrentIndex(4))
        self.btn_visualisation_2d.clicked.connect(lambda : self.stack.setCurrentIndex(5))
        self.btn_visualisation_3d.clicked.connect(lambda : self.stack.setCurrentIndex(6))
        self.page_diago.btn_view_3d.clicked.connect(lambda : self.bridge_diag_to_3d())

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

    def bridge_diag_to_3d(self):
        try:
            n = self.page_diago.spin_n.value()

            for r in range(3):
                for c in range(3):
                    if r < n and c < n:
                        item = self.page_diago.matrix_table.item(r, c)
                        val = item.text() if item and item.text() else "0"
                    else:
                        val = "1" if r == c else "0"

                    self.page_visualisation_3d.matrix_input.item(r, c).setText(val)

            self.stack.setCurrentWidget(self.page_visualisation_3d)

            self.page_visualisation_3d.calculate_and_draw_eigen()

        except Exception as e:
            print(f"Erreur de transfert : {e}")