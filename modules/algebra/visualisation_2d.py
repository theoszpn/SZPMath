import numpy as np
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFrame,
                               QLabel, QPushButton, QCheckBox, QTableWidget,
                               QTableWidgetItem, QLineEdit, QStyledItemDelegate)
from PySide6.QtCore import Qt, QTimer, QRegularExpression
from PySide6.QtGui import QColor, QFont, QRegularExpressionValidator
import pyqtgraph as pg
from sympy import sympify, Matrix


class NumericDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        regex = QRegularExpression(r"^-?[0-9]*[/.]?[0-9]*$")
        editor.setValidator(QRegularExpressionValidator(regex, editor))
        editor.setStyleSheet("font-weight: bold; font-size: 18px; color: black;")
        editor.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return editor


class Visualisation2DPage(QWidget):
    def __init__(self):
        super().__init__()
        self.target_matrix = np.eye(2)
        self.animation_t = 1.0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.eigen_items = []

        self.init_ui()
        self.setup_connections()
        self.reset_everything()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)

        self.ctrl_panel = QFrame()
        self.ctrl_panel.setFixedWidth(300)
        self.ctrl_panel.setStyleSheet("""
            QFrame { background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 10px; }
            QLabel { color: #2c3e50; font-weight: bold; border: none; }
            QCheckBox { color: #2c3e50; font-weight: bold; border: none; }
            QPushButton { font-weight: bold; border-radius: 5px; padding: 12px; color: white; border: none; }
        """)
        cp_layout = QVBoxLayout(self.ctrl_panel)

        title = QLabel("GÉOMÉTRIE 2D")
        title.setStyleSheet("font-size: 20px; color: #1a5276; margin-bottom: 10px;")
        cp_layout.addWidget(title)

        cp_layout.addWidget(QLabel("Matrice de transformation A :"))
        self.matrix_input = QTableWidget(2, 2)
        self.setup_matrix_table()
        cp_layout.addWidget(self.matrix_input, alignment=Qt.AlignmentFlag.AlignCenter)

        self.chk_basis = QCheckBox("Colorer la base (i, j)")
        self.chk_basis.setChecked(True)
        self.chk_eigen = QCheckBox("Afficher vecteurs propres")
        cp_layout.addWidget(self.chk_basis)
        cp_layout.addWidget(self.chk_eigen)

        self.eigen_status = QLabel("")
        cp_layout.addWidget(self.eigen_status)

        cp_layout.addSpacing(10)

        self.btn_animate = QPushButton("▶ APPLIQUER LA MATRICE")
        self.btn_animate.setStyleSheet("""
                    QPushButton { 
                        background-color: #2980b9; color: white; padding: 12px; 
                        font-weight: bold; border-radius: 5px; margin-top: 10px;
                        text-align: left; padding-left: 20px; border: none;
                    }
                    QPushButton:hover { 
                        background-color: #3498db; 
                        border-left: 8px solid #1a5276;
                    }
                """)
        cp_layout.addWidget(self.btn_animate)

        self.btn_reset = QPushButton("↺ RÉINITIALISER CARRÉ")
        self.btn_reset.setStyleSheet("""
                    QPushButton { 
                        background-color: #2980b9; color: white; padding: 12px; 
                        font-weight: bold; border-radius: 5px; margin-top: 10px;
                        text-align: left; padding-left: 20px; border: none;
                    }
                    QPushButton:hover { 
                        background-color: #3498db; 
                        border-left: 8px solid #1a5276;
                    }
                """)
        cp_layout.addWidget(self.btn_reset)

        cp_layout.addStretch()
        layout.addWidget(self.ctrl_panel)

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('#1e1e23')
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.plot_widget.setAspectLocked(True)

        self.plot_widget.addItem(pg.InfiniteLine(pos=0, angle=0, pen=pg.mkPen('#444', width=1)))
        self.plot_widget.addItem(pg.InfiniteLine(pos=0, angle=90, pen=pg.mkPen('#444', width=1)))

        self.edge_i = pg.PlotCurveItem(pen=pg.mkPen('#e74c3c', width=5))
        self.edge_j = pg.PlotCurveItem(pen=pg.mkPen('#2ecc71', width=5))
        self.square_rest = pg.PlotCurveItem(pen=pg.mkPen('#3498db', width=2))

        self.label_i = pg.TextItem(html='<span style="color: #e74c3c; font-weight: bold; font-size: 14pt;">î</span>',
                                   anchor=(0.5, 1))
        self.label_j = pg.TextItem(html='<span style="color: #2ecc71; font-weight: bold; font-size: 14pt;">ĵ</span>',
                                   anchor=(0.5, 1))

        self.plot_widget.addItem(self.edge_i)
        self.plot_widget.addItem(self.edge_j)
        self.plot_widget.addItem(self.square_rest)
        self.plot_widget.addItem(self.label_i)
        self.plot_widget.addItem(self.label_j)

        layout.addWidget(self.plot_widget)
        self.reset_view()

    def setup_matrix_table(self):
        size = 65
        self.matrix_input.setFixedSize(size * 2 + 5, size * 2 + 5)
        self.matrix_input.horizontalHeader().setVisible(False)
        self.matrix_input.verticalHeader().setVisible(False)
        self.matrix_input.horizontalHeader().setDefaultSectionSize(size)
        self.matrix_input.verticalHeader().setDefaultSectionSize(size)
        self.matrix_input.setItemDelegate(NumericDelegate())
        self.matrix_input.setStyleSheet(
            "QTableWidget { background-color: white; color: black; border: 2px solid #2c3e50; font-weight: bold; font-size: 18px; }")

    def reset_matrix_ui(self):
        for r in range(2):
            for c in range(2):
                val = "1" if r == c else "0"
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if c == 0:
                    item.setForeground(QColor('#e74c3c'))  # Rouge pour colonne i
                else:
                    item.setForeground(QColor('#2ecc71'))  # Vert pour colonne j
                self.matrix_input.setItem(r, c, item)

    def reset_view(self):
        self.plot_widget.setXRange(-4, 4)
        self.plot_widget.setYRange(-4, 4)

    def reset_everything(self):
        self.timer.stop()
        self.animation_t = 1.0
        self.target_matrix = np.eye(2)
        self.reset_matrix_ui()
        self.update_plot_data(np.eye(2))
        self.calculate_and_draw_eigen()
        self.reset_view()

    def calculate_and_draw_eigen(self):
        for item in self.eigen_items:
            self.plot_widget.removeItem(item)
        self.eigen_items = []
        if not self.chk_eigen.isChecked():
            self.eigen_status.setText("")
            return

        try:
            A_np = self.get_matrix_a()
            evals, evecs = np.linalg.eig(A_np)
            colors = ['#f1c40f', '#e67e22']
            v_count = 0

            if any(np.iscomplex(evals)):
                self.eigen_status.setText("⚠️ Complexes")
                self.eigen_status.setStyleSheet("color: #e67e22; font-weight: bold;")
            else:
                self.eigen_status.setText("✓ Réels")
                self.eigen_status.setStyleSheet("color: #27ae60; font-weight: bold;")

            for i in range(len(evals)):
                if np.iscomplex(evals[i]): continue
                vx, vy = float(evecs[0, i].real), float(evecs[1, i].real)
                norm = np.sqrt(vx ** 2 + vy ** 2)
                if norm < 1e-4: continue
                v_dir = np.array([vx, vy]) / norm
                angle = np.degrees(np.arctan2(vy, vx))
                line = pg.InfiniteLine(pos=(0, 0), angle=angle,
                                       pen=pg.mkPen(colors[v_count % 2], width=2, style=Qt.PenStyle.DashLine))
                text = pg.TextItem(text=f"v{v_count + 1}: λ={evals[i].real:.1f}", color=colors[v_count % 2],
                                   anchor=(0.5, 0.5))
                text.setPos(float(3.2 * v_dir[0]), float(3.2 * v_dir[1]))
                self.plot_widget.addItem(line)
                self.plot_widget.addItem(text)
                self.eigen_items.append(line)
                self.eigen_items.append(text)
                v_count += 1
        except:
            pass

    def update_plot_data(self, matrix):
        p0 = np.array([0.0, 0.0])
        p1 = matrix @ np.array([1.0, 0.0])
        p3 = matrix @ np.array([0.0, 1.0])
        p2 = p1 + p3

        use_colors = self.chk_basis.isChecked()

        color_i = '#e74c3c' if use_colors else '#3498db'
        self.edge_i.setData([p0[0], p1[0]], [p0[1], p1[1]])
        self.edge_i.setPen(pg.mkPen(color_i, width=(5 if use_colors else 2)))

        color_j = '#2ecc71' if use_colors else '#3498db'
        self.edge_j.setData([p0[0], p3[0]], [p0[1], p3[1]])
        self.edge_j.setPen(pg.mkPen(color_j, width=(5 if use_colors else 2)))

        self.square_rest.setData([p1[0], p2[0], p3[0]], [p1[1], p2[1], p3[1]])

        self.label_i.setPos(float(p1[0] * 1.1), float(p1[1] * 1.1))
        self.label_j.setPos(float(p3[0] * 1.1), float(p3[1] * 1.1))

        self.label_i.setVisible(use_colors)
        self.label_j.setVisible(use_colors)

    def get_matrix_a(self):
        matrix = np.eye(2)
        for r in range(2):
            for c in range(2):
                try:
                    txt = self.matrix_input.item(r, c).text()
                    val = sympify(txt)
                    matrix[r, c] = float(val.evalf())
                except:
                    matrix[r, c] = 1.0 if r == c else 0.0
        return matrix

    def start_animation(self):
        self.target_matrix = self.get_matrix_a()
        self.animation_t = 0.0
        self.timer.start(20)

    def update_animation(self):
        self.animation_t += 0.05
        if self.animation_t >= 1.0:
            self.animation_t = 1.0
            self.timer.stop()
            self.calculate_and_draw_eigen()

        t = self.animation_t
        interp = (1 - t) * np.eye(2) + t * self.target_matrix
        self.update_plot_data(interp)

    def setup_connections(self):
        self.btn_animate.clicked.connect(self.start_animation)
        self.btn_reset.clicked.connect(self.reset_everything)
        self.chk_basis.stateChanged.connect(
            lambda: self.update_plot_data(self.target_matrix if self.animation_t >= 1.0 else np.eye(2)))
        self.chk_eigen.stateChanged.connect(self.calculate_and_draw_eigen)
        self.matrix_input.itemChanged.connect(self.calculate_and_draw_eigen)