import numpy as np
from sympy import sympify
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFrame,
                               QLabel, QPushButton, QComboBox, QCheckBox,
                               QTableWidget, QTableWidgetItem, QHeaderView,
                               QLineEdit, QStyledItemDelegate, QScrollArea)
from PySide6.QtCore import Qt, QRegularExpression, QTimer
from PySide6.QtGui import QColor, QRegularExpressionValidator, QFont
import pyqtgraph.opengl as gl

VECTOR_COLORS = [
    (231, 76, 60, 255),  # Rouge
    (46, 204, 113, 255),  # Vert
    (52, 152, 219, 255),  # Bleu
    (241, 196, 15, 255),  # Jaune
    (155, 89, 182, 255),  # Violet
    (230, 126, 34, 255)  # Orange
]


class NumericDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        regex = QRegularExpression(r"^-?[0-9]*[/.]?[0-9]*$")
        validator = QRegularExpressionValidator(regex, editor)
        editor.setValidator(validator)
        editor.setAlignment(Qt.AlignmentFlag.AlignCenter)

        color = index.data(Qt.ItemDataRole.ForegroundRole)
        hex_color = color.name() if isinstance(color, QColor) else "#000000"

        editor.setStyleSheet(f"""
            QLineEdit {{ 
                font-weight: bold; 
                font-size: 16px; 
                color: {hex_color} !important; 
                background-color: white !important; 
                border: none;
                selection-background-color: #d1d1d1; /* Couleur de sélection du texte interne */
                selection-color: black;
            }}
        """)
        return editor


class Visualisation3DPage(QWidget):
    def __init__(self):
        super().__init__()
        self.cell_size = 60
        self.animation_t = 0.0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)

        self.eigen_items = []
        self.combo_items = []
        self.vector_rows = []

        self.base_vertices = np.array([
            [0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0],
            [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]
        ], dtype=float)

        self.cube_faces = np.array([
            [0, 1, 2], [0, 2, 3], [4, 5, 6], [4, 6, 7],
            [0, 1, 5], [0, 5, 4], [2, 3, 7], [2, 7, 6],
            [0, 3, 7], [0, 7, 4], [1, 2, 6], [1, 6, 5]
        ])

        self.edge_indices = np.array([
            0, 1, 1, 2, 2, 3, 3, 0, 4, 5, 5, 6, 6, 7, 7, 4, 0, 4, 1, 5, 2, 6, 3, 7
        ])

        self.init_ui()
        self.setup_connections()
        self.toggle_mode()

    def setup_connections(self):
        self.btn_animate.clicked.connect(self.start_animation)
        self.btn_reset.clicked.connect(self.reset_transformation)
        self.mode_selector.currentIndexChanged.connect(self.toggle_mode)
        self.chk_eigen.stateChanged.connect(self.calculate_and_draw_eigen)
        self.matrix_input.itemChanged.connect(self.calculate_and_draw_eigen)
        self.matrix_input.itemChanged.connect(self.update_target_on_change)
        self.chk_grid.stateChanged.connect(lambda s: self.grid.setVisible(s))
        self.chk_axes.stateChanged.connect(self.toggle_axes)
        self.chk_cube.stateChanged.connect(lambda s: (self.mesh_item.setVisible(s), self.edge_item.setVisible(s)))

    def init_ui(self):
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        self.control_panel = QFrame()
        self.control_panel.setFixedWidth(340)
        self.control_panel.setStyleSheet("""
            QFrame { background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 8px; }
            QLabel { border: none; font-weight: bold; color: #2c3e50; }
            QComboBox { color: white; background-color: #34495e; border: 1px solid #2c3e50; border-radius: 4px; padding: 5px; font-weight: bold; }
            QComboBox QAbstractItemView { background-color: #34495e; color: white; selection-background-color: #2980b9; border: none; outline: none; }
            QCheckBox { color: #2c3e50; border: none; font-weight: normal; }
            QPushButton { background-color: #2980b9; color: white; border-radius: 5px; padding: 10px; font-weight: bold; border: none; }
            QPushButton:hover { background-color: #3498db; }
        """)

        self.cp_layout = QVBoxLayout(self.control_panel)
        self.cp_layout.setContentsMargins(20, 20, 20, 20)
        self.cp_layout.setSpacing(12)
        self.cp_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        title = QLabel("CONTRÔLES GÉOMÉTRIQUES")
        title.setStyleSheet("font-size: 16px; margin-bottom: 5px; color: #1a5276;")
        self.cp_layout.addWidget(title)

        self.cp_layout.addWidget(QLabel("Mode d'affichage :"))
        self.mode_selector = QComboBox()
        self.mode_selector.addItems(["Transformations Linéaires", "Combinaison Linéaire"])
        self.cp_layout.addWidget(self.mode_selector)

        self.cp_layout.addSpacing(10)

        self.matrix_container = QWidget()
        matrix_vbox = QVBoxLayout(self.matrix_container)
        matrix_vbox.setContentsMargins(0, 0, 0, 0)
        self.label_matrix = QLabel("Matrice de transformation (A) :")
        matrix_vbox.addWidget(self.label_matrix)
        self.matrix_input = QTableWidget(3, 3)
        self.setup_matrix_input()
        matrix_vbox.addWidget(self.matrix_input, alignment=Qt.AlignmentFlag.AlignCenter)
        self.cp_layout.addWidget(self.matrix_container)

        self.combo_container = QWidget()
        self.combo_vbox = QVBoxLayout(self.combo_container)
        self.combo_vbox.setContentsMargins(0, 0, 0, 0)
        self.combo_vbox.addWidget(QLabel("Vecteurs & Scalaires :"))

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
                    QScrollArea { 
                        background-color: white; 
                        border: 1px solid #dee2e6; 
                        border-radius: 5px; 
                    }
                """)
        self.scroll_widget = QWidget()
        self.scroll_widget.setStyleSheet("background-color: white;")
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_area.setWidget(self.scroll_widget)
        self.combo_vbox.addWidget(self.scroll_area)

        self.btn_add_vec = QPushButton("+ Ajouter un vecteur")
        self.btn_add_vec.setStyleSheet("background-color: #27ae60; padding: 5px; font-size: 11px;")
        self.btn_add_vec.clicked.connect(self.add_vector_row)
        self.combo_vbox.addWidget(self.btn_add_vec)

        self.result_label = QLabel("Somme : (0, 0, 0)")
        self.result_label.setStyleSheet("color: #2980b9; font-family: monospace; font-size: 13px; margin-top: 5px;")
        self.combo_vbox.addWidget(self.result_label)

        self.cp_layout.addWidget(self.combo_container)

        self.cp_layout.addSpacing(10)
        self.cp_layout.addWidget(QLabel("Options visuelles :"))
        self.chk_grid = QCheckBox("Afficher la grille")
        self.chk_grid.setChecked(True)
        self.chk_axes = QCheckBox("Afficher les axes (X, Y, Z)")
        self.chk_axes.setChecked(True)
        self.chk_cube = QCheckBox("Cube unité")
        self.chk_cube.setChecked(True)
        self.chk_eigen = QCheckBox("Vecteurs propres")

        for chk in [self.chk_grid, self.chk_axes, self.chk_cube, self.chk_eigen]:
            self.cp_layout.addWidget(chk)

        self.btn_animate = QPushButton("▶ LANCER L'ANIMATION")
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
        self.btn_reset = QPushButton("↺ RÉINITIALISER")
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

        self.cp_layout.addWidget(self.btn_animate)
        self.cp_layout.addWidget(self.btn_reset)
        self.cp_layout.addStretch()

        self.view_3d = gl.GLViewWidget()
        self.view_3d.setBackgroundColor(QColor(30, 30, 35))
        self.view_3d.setCameraPosition(distance=15, elevation=30, azimuth=45)
        self.grid = gl.GLGridItem()
        self.grid.setSize(20, 20)
        self.grid.setSpacing(1, 1)
        self.grid.setColor((100, 100, 100, 100))
        self.view_3d.addItem(self.grid)
        self.create_thick_axes()

        self.main_layout.addWidget(self.control_panel)
        self.main_layout.addWidget(self.view_3d, 1)

        self.mesh_item = gl.GLMeshItem(vertexes=self.base_vertices, faces=self.cube_faces,
                                       color=(52 / 255, 152 / 255, 219 / 255, 0.6), shader='shaded')
        self.edge_item = gl.GLLinePlotItem(pos=self.base_vertices[self.edge_indices],
                                           color=(52 / 255, 152 / 255, 219 / 255, 1.0), width=2, mode='lines',
                                           antialias=True)
        self.view_3d.addItem(self.mesh_item)
        self.view_3d.addItem(self.edge_item)

        for _ in range(3): self.add_vector_row()

    def add_vector_row(self):
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 2, 0, 2)
        layout.setSpacing(4)

        color_idx = len(self.vector_rows) % len(VECTOR_COLORS)
        rgba = VECTOR_COLORS[color_idx]
        hex_color = QColor(*rgba).name()

        input_style = f"font-weight: bold; color: {hex_color}; border: 1px solid #dee2e6; border-radius: 3px; background: white;"

        scalar_edit = QLineEdit("1")
        scalar_edit.setFixedWidth(35)
        scalar_edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scalar_edit.setStyleSheet(input_style)

        layout.addWidget(scalar_edit)
        layout.addWidget(QLabel("×"))

        coords_edits = []
        for i in range(3):
            val = "1" if i == color_idx else "0"
            edit = QLineEdit(val)
            edit.setFixedWidth(35)
            edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
            edit.setStyleSheet(input_style)
            layout.addWidget(edit)
            coords_edits.append(edit)

        btn_del = QPushButton("✕")
        btn_del.setFixedSize(20, 20)
        btn_del.setStyleSheet("""
                    QPushButton { 
                        background-color: #e62410; 
                        color: #FFFFFF;          
                        font-size: 16px; 
                        font-weight: bold; 
                        border: none; 
                        text-align: center; padding: 0px 0px 4px 0px; 
                    } 
                    QPushButton:hover { 
                        background-color: #ffeeee;
                        border-radius: 12px;
                    }
                """)
        btn_del.clicked.connect(lambda: self.remove_vector_row(row))
        layout.addWidget(btn_del)

        self.scroll_layout.addWidget(row)
        self.vector_rows.append({'widget': row, 'scalar': scalar_edit, 'coords': coords_edits, 'color': rgba})
        self.draw_linear_combination()

    def remove_vector_row(self, widget):
        if len(self.vector_rows) > 1:
            for i, data in enumerate(self.vector_rows):
                if data['widget'] == widget:
                    self.vector_rows.pop(i)
                    widget.setParent(None)
                    break
            self.draw_linear_combination()

    def toggle_mode(self):
        is_combo = (self.mode_selector.currentIndex() == 1)
        self.matrix_container.setVisible(not is_combo)
        self.combo_container.setVisible(is_combo)
        self.chk_cube.setVisible(not is_combo)
        self.chk_eigen.setVisible(not is_combo)

        self.mesh_item.setVisible(not is_combo and self.chk_cube.isChecked())
        self.edge_item.setVisible(not is_combo and self.chk_cube.isChecked())

        if is_combo:
            self.clear_eigenvectors()
            self.draw_linear_combination()
        else:
            self.clear_combination()

    def create_thick_axes(self):
        pos_x = np.array([[0, 0, 0], [5, 0, 0]])
        pos_y = np.array([[0, 0, 0], [0, 5, 0]])
        pos_z = np.array([[0, 0, 0], [0, 0, 5]])

        self.ax_x = gl.GLLinePlotItem(pos=pos_x, color=(255, 0, 0, 255), width=3, antialias=True)
        self.ax_y = gl.GLLinePlotItem(pos=pos_y, color=(0, 255, 0, 255), width=3, antialias=True)
        self.ax_z = gl.GLLinePlotItem(pos=pos_z, color=(0, 0, 255, 255), width=3, antialias=True)

        self.label_x = gl.GLTextItem(pos=np.array([5.2, 0, 0]), text='X', color=(255, 0, 0, 255))
        self.label_y = gl.GLTextItem(pos=np.array([0, 5.2, 0]), text='Y', color=(0, 255, 0, 255))
        self.label_z = gl.GLTextItem(pos=np.array([0, 0, 5.2]), text='Z', color=(0, 0, 255, 255))

        for item in [self.ax_x, self.ax_y, self.ax_z, self.label_x, self.label_y, self.label_z]:
            self.view_3d.addItem(item)

    def toggle_axes(self, state):
        visible = bool(state)
        for item in [self.ax_x, self.ax_y, self.ax_z, self.label_x, self.label_y, self.label_z]:
            item.setVisible(visible)

    def setup_matrix_input(self):
        n = 3
        self.matrix_input.setRowCount(n)
        self.matrix_input.setColumnCount(n)
        self.matrix_input.setFixedSize(n * self.cell_size + 5, n * self.cell_size + 5)
        self.matrix_input.horizontalHeader().setVisible(False)
        self.matrix_input.verticalHeader().setVisible(False)
        self.matrix_input.horizontalHeader().setDefaultSectionSize(self.cell_size)
        self.matrix_input.verticalHeader().setDefaultSectionSize(self.cell_size)
        self.matrix_input.setStyleSheet("""
                    QTableWidget { 
                        background-color: white; 
                        color: black; 
                        border: 2px solid #2c3e50; 
                        font-weight: bold; 
                        font-size: 20px; 
                        gridline-color: #bdc3c7;
                        outline: 0; 
                    }
                    QTableWidget::item:selected {
                        background-color: white; /* Pas de fond bleu ! */
                        color: inherit;           /* On garde la couleur du texte (Rouge/Vert/Bleu) */
                    }
                """)
        self.matrix_input.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.matrix_input.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.matrix_input.setItemDelegate(NumericDelegate())

        col_colors = ['#e74c3c', '#2ecc71', '#3498db']
        for r in range(n):
            for c in range(n):
                val = "1" if r == c else "0"
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setForeground(QColor(col_colors[c]))
                self.matrix_input.setItem(r, c, item)

    def clear_combination(self):
        for item in self.combo_items: self.view_3d.removeItem(item)
        self.combo_items = []

    def draw_linear_combination(self, animation_progress=1.0):
        self.clear_combination()
        curr_pos = np.array([0.0, 0.0, 0.0])
        total_vec = np.array([0.0, 0.0, 0.0])

        try:
            for row_data in self.vector_rows:
                s = float(sympify(row_data['scalar'].text() or "0").evalf())
                v = np.array([float(sympify(e.text() or "0").evalf()) for e in row_data['coords']])
                scaled_v = s * v
                next_pos = curr_pos + scaled_v

                c = row_data['color']
                norm_color = (c[0]/255.0, c[1]/255.0, c[2]/255.0, c[3]/255.0)

                line = gl.GLLinePlotItem(
                    pos=np.array([curr_pos, next_pos]),
                    color=norm_color,
                    width=5,
                    antialias=True
                )
                self.view_3d.addItem(line)
                self.combo_items.append(line)

                curr_pos = next_pos
                total_vec += scaled_v

            animated_tip = total_vec * animation_progress

            res_line = gl.GLLinePlotItem(
                pos=np.array([[0, 0, 0], animated_tip]),
                color=(1.0, 1.0, 1.0, 1.0),
                width=3,
                antialias=True
            )

            sphere = gl.GLScatterPlotItem(
                pos=np.array([animated_tip]),
                size=0.4,
                color=(1.0, 1.0, 1.0, 1.0),
                pxMode=False
            )

            self.view_3d.addItem(res_line)
            self.view_3d.addItem(sphere)
            self.combo_items.extend([res_line, sphere])

            self.result_label.setText(f"Somme : ({total_vec[0]:.2f}, {total_vec[1]:.2f}, {total_vec[2]:.2f})")

        except Exception as e:
            print(f"Erreur rendu combinaison: {e}")

    def get_matrix_a(self):
        matrix = np.eye(3)
        for r in range(3):
            for c in range(3):
                try:
                    val_str = self.matrix_input.item(r, c).text().strip()
                    matrix[r, c] = float(sympify(val_str or "0").evalf())
                except:
                    matrix[r, c] = 1.0 if r == c else 0.0
        return matrix

    def start_animation(self):
        self.animation_t = 0.0
        if self.mode_selector.currentIndex() == 0:
            self.target_matrix = self.get_matrix_a()
            self.calculate_and_draw_eigen()
        else:
            pass

        self.timer.start(20)

    def update_animation(self):
        self.animation_t += 0.02
        if self.animation_t >= 1.0:
            self.animation_t = 1.0
            self.timer.stop()

        t = self.animation_t

        if self.mode_selector.currentIndex() == 0:
            interp = (1 - t) * np.eye(3) + t * self.target_matrix
            v = np.dot(self.base_vertices, interp.T)
            self.mesh_item.setMeshData(vertexes=v, faces=self.cube_faces)
            self.edge_item.setData(pos=v[self.edge_indices])
        else:
            self.draw_linear_combination(animation_progress=t)

    def update_target_on_change(self):
        if self.mode_selector.currentIndex() == 0: self.target_matrix = self.get_matrix_a()

    def reset_transformation(self):
        self.timer.stop()
        self.animation_t = 0.0
        self.mesh_item.setMeshData(vertexes=self.base_vertices, faces=self.cube_faces)
        self.edge_item.setData(pos=self.base_vertices[self.edge_indices])
        self.clear_eigenvectors()
        self.clear_combination()

    def clear_eigenvectors(self):
        for item in self.eigen_items: self.view_3d.removeItem(item)
        self.eigen_items = []

    def calculate_and_draw_eigen(self):
        self.clear_eigenvectors()
        if not self.chk_eigen.isChecked() or self.mode_selector.currentIndex() == 1: return
        try:
            from sympy import Matrix as SymMatrix
            A_sym = SymMatrix(self.get_matrix_a())
            eigen_data = A_sym.eigenvects()
            colors, v_count, idx_color = [(255, 255, 0), (255, 0, 255), (0, 255, 255)], 1, 0
            for val, mult, vecs in eigen_data:
                for v in vecs:
                    v_np = np.array([float(v[0]), float(v[1]), float(v[2])])
                    norm = np.linalg.norm(v_np)
                    if norm < 1e-6: continue
                    v_dir = v_np / norm
                    color = colors[idx_color % len(colors)]
                    line = gl.GLLinePlotItem(pos=np.array([-10 * v_dir, 10 * v_dir]), color=color + (180,), width=3)
                    text = gl.GLTextItem(pos=np.array(7 * v_dir), text=f"v{v_count}", color=color + (255,))
                    self.view_3d.addItem(line)
                    self.view_3d.addItem(text)
                    self.eigen_items.extend([line, text])
                    v_count += 1
                idx_color += 1
        except:
            pass