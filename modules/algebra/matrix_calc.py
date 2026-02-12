from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                               QTableWidgetItem, QPushButton, QHeaderView,
                               QSpinBox, QLabel, QFrame, QAbstractItemView, QMessageBox)
from PySide6.QtCore import Qt
from sympy import Matrix, simplify


class MatrixCalcPage(QWidget):
    def __init__(self):
        super().__init__()
        self.cell_size = 80
        self.init_ui()

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(15)

        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        self.matrices_layout = QHBoxLayout()
        self.matrices_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.matrices_layout.setSpacing(20)

        self.spin_rows_a = self.create_spinbox(3)
        self.spin_cols_a = self.create_spinbox(3)
        self.spin_rows_b = self.create_spinbox(3)
        self.spin_cols_b = self.create_spinbox(3)

        self.table_a = self.create_matrix_table(3, 3)
        self.table_b = self.create_matrix_table(3, 3)
        self.table_res = self.create_matrix_table(3, 3, readonly=True)

        self.matrices_layout.addWidget(
            self.create_matrix_control_group("MATRICE A", self.table_a, self.spin_rows_a, self.spin_cols_a))
        self.matrices_layout.addWidget(
            self.create_matrix_control_group("MATRICE B", self.table_b, self.spin_rows_b, self.spin_cols_b))
        self.matrices_layout.addWidget(
            self.create_matrix_control_group("RÉSULTAT", self.table_res))

        self.matrices_layout.addStretch()
        self.main_layout.addLayout(self.matrices_layout)

        buttons_layout = QHBoxLayout()
        buttons_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)  # Important
        self.setup_buttons(buttons_layout)

        self.main_layout.addLayout(buttons_layout)
        self.main_layout.addStretch()

        self.spin_rows_a.valueChanged.connect(lambda v: self.update_table(self.table_a, v, self.spin_cols_a.value()))
        self.spin_cols_a.valueChanged.connect(lambda v: self.update_table(self.table_a, self.spin_rows_a.value(), v))
        self.spin_rows_b.valueChanged.connect(lambda v: self.update_table(self.table_b, v, self.spin_cols_b.value()))
        self.spin_cols_b.valueChanged.connect(lambda v: self.update_table(self.table_b, self.spin_rows_b.value(), v))


    def create_matrix_control_group(self, title, table, spin_r=None, spin_c=None):
        group = QFrame()
        layout = QVBoxLayout(group)
        layout.setContentsMargins(0, 0, 0, 0)
        lbl = QLabel(title)
        lbl.setStyleSheet("font-weight: bold; color: #2f3640; font-size: 13px;")
        layout.addWidget(lbl, alignment=Qt.AlignmentFlag.AlignCenter)
        if spin_r and spin_c:
            ctrl = QHBoxLayout()
            lbl_l, lbl_c = QLabel("L:"), QLabel("C:")
            for l in [lbl_l, lbl_c]: l.setStyleSheet("color: #2f3640; font-weight: bold;")
            ctrl.addWidget(lbl_l)
            ctrl.addWidget(spin_r)
            ctrl.addWidget(lbl_c)
            ctrl.addWidget(spin_c)
            ctrl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addLayout(ctrl)
        layout.addWidget(table)
        return group

    def create_matrix_table(self, rows, cols, readonly=False):
        table = QTableWidget(rows, cols)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        table.horizontalHeader().setDefaultSectionSize(self.cell_size)
        table.verticalHeader().setDefaultSectionSize(self.cell_size)
        table.horizontalHeader().setVisible(False)
        table.verticalHeader().setVisible(False)
        table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        if readonly:
            table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        else:
            table.setEditTriggers(QAbstractItemView.EditTrigger.AllEditTriggers)
            table.itemChanged.connect(self.align_cell_text)

        table.setStyleSheet("""
            QTableWidget { 
                background-color: white; 
                color: black; 
                border: 2px solid #34495e; 
                font-size: 22px;
                font-weight: bold; 
            }
            QTableWidget QLineEdit {
                background-color: white;
                color: black;
                border: none;
            }
        """)
        self.adjust_size(table, rows, cols)
        return table

    def align_cell_text(self, item):
        table = item.tableWidget()
        table.blockSignals(True)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        table.blockSignals(False)

    def adjust_size(self, table, rows, cols):
        table.setFixedSize((cols * self.cell_size) + 4, (rows * self.cell_size) + 4)

    def update_table(self, table, rows, cols):
        table.setRowCount(rows)
        table.setColumnCount(cols)
        self.adjust_size(table, rows, cols)

    def create_spinbox(self, default):
        sb = QSpinBox()
        sb.setRange(1, 10)
        sb.setValue(default)
        sb.setFixedWidth(55)
        return sb

    def setup_buttons(self, layout):
        btn_style = """
            QPushButton { 
                background-color: #0097e6; color: white; border-radius: 4px; 
                padding: 10px; font-weight: bold; min-width: 80px; 
            } 
            QPushButton:hover { background-color: #00a8ff; }
        """
        operations = ["A + B", "A × B", "A⁻¹", "Aᵀ", "det(A)"]

        for txt in operations:
            btn = QPushButton(txt)
            btn.setStyleSheet(btn_style)
            btn.clicked.connect(lambda checked=False, t=txt: self.compute(t))
            layout.addWidget(btn)

        layout.addStretch()

    def get_matrix(self, table):
        rows = table.rowCount()
        cols = table.columnCount()
        data = []
        for r in range(rows):
            row_data = []
            for c in range(cols):
                item = table.item(r, c)
                val = item.text() if item and item.text() else "0"
                row_data.append(simplify(val))
            data.append(row_data)
        return Matrix(data)

    def display_result(self, res_matrix):
        rows, cols = res_matrix.shape
        self.update_table(self.table_res, rows, cols)

        for r in range(rows):
            for c in range(cols):
                val = str(res_matrix[r, c])
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table_res.setItem(r, c, item)

    def compute(self, operation):
        try:
            A = self.get_matrix(self.table_a)

            if operation == "A + B":
                B = self.get_matrix(self.table_b)
                self.display_result(A + B)
            elif operation == "A × B":
                B = self.get_matrix(self.table_b)
                self.display_result(A * B)
            elif operation == "A⁻¹":
                if A.det() == 0:
                    raise ValueError("Matrice non inversible (déterminant nul)")
                self.display_result(A.inv())
            elif operation == "Aᵀ":
                self.display_result(A.T)
            elif operation == "det(A)":
                d = A.det()
                QMessageBox.information(self, "Résultat", f"Le déterminant de A est : {d}")
            elif operation == "Aⁿ":
                self.display_result(A ** 2)

        except Exception as e:
            QMessageBox.critical(self, "Erreur de calcul", str(e))