from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                               QPushButton, QTextEdit, QLabel, QFrame, QHeaderView,
                               QSpinBox, QComboBox, QSizePolicy)
from PySide6.QtCore import Qt
from sympy import symbols, solve, simplify, Matrix, Rational, Symbol

class GaussSolverPage(QWidget):
    def __init__(self):
        super().__init__()
        self.cell_size = 60
        self.init_ui()

    def init_ui(self):
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        left_column = QVBoxLayout()
        left_column.setAlignment(Qt.AlignmentFlag.AlignTop)

        dims_layout = QHBoxLayout()
        self.spin_rows = self.create_spinbox(3)
        self.spin_cols = self.create_spinbox(3)

        dim_lbl_l, dim_lbl_c= QLabel("Lignes:"), QLabel("Colonnes:")
        for l in [dim_lbl_l, dim_lbl_c]: l.setStyleSheet("color: #2f3640; font-weight: bold;")
        dims_layout.addWidget(dim_lbl_l)
        dims_layout.addWidget(self.spin_rows)
        dims_layout.addWidget(dim_lbl_c)
        dims_layout.addWidget(self.spin_cols)
        dims_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        dims_layout.addStretch()
        left_column.addLayout(dims_layout)

        matrix_container = QHBoxLayout()
        matrix_container.setSpacing(0)

        self.table_a = self.create_table(3, 3)

        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setLineWidth(2)
        separator.setStyleSheet("color: #34495e; margin: 0 5px;")

        self.table_b = self.create_table(3, 1)

        matrix_container.addWidget(self.table_a)
        matrix_container.addWidget(separator)
        matrix_container.addWidget(self.table_b)
        matrix_container.addStretch()

        left_column.addLayout(matrix_container)

        lbl_method = QLabel("Méthode de résolution :")
        lbl_method.setStyleSheet("font-weight: bold; margin-top: 15px; color: black;")
        left_column.addWidget(lbl_method)

        self.combo_method = QComboBox()
        self.combo_method.addItems(["Pivot de Gauss (Triangulaire)", "Gauss-Jordan (Diagonale)"])
        self.combo_method.setStyleSheet("""
                    QComboBox { 
                        color: black;
                        padding: 8px; 
                        font-weight: bold; 
                        border: 2px solid #bdc3c7; 
                        border-radius: 5px;
                        background-color: white;
                    }
                """)
        left_column.addWidget(self.combo_method)

        self.btn_solve = QPushButton("Résoudre pas à pas")
        self.btn_solve.setStyleSheet("""
            QPushButton { 
                background-color: #27ae60; color: white; padding: 12px; 
                font-weight: bold; border-radius: 5px; margin-top: 20px;
                min-width: 200px;
            }
            QPushButton:hover { background-color: #2ecc71; }
        """)
        self.btn_solve.setFixedWidth(100)
        left_column.addWidget(self.btn_solve)
        left_column.addStretch()

        right_column = QVBoxLayout()
        lbl_steps = QLabel("Étapes de résolution")
        lbl_steps.setStyleSheet("font-weight: bold; font-size: 16px; color: black")

        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setStyleSheet("""
            QTextEdit {
                background-color: white;
                color: black; 
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 20px;
                selection-background-color: #3498db;
            }
        """)
        right_column.addWidget(lbl_steps)
        self.log_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        right_column.addWidget(self.log_area, 1)

        self.main_layout.addLayout(left_column, 1)
        self.main_layout.addLayout(right_column, 6)

        self.spin_rows.valueChanged.connect(self.update_dimensions)
        self.spin_cols.valueChanged.connect(self.update_dimensions)
        self.btn_solve.clicked.connect(self.solve_gauss)

    def create_table(self, r, c):
        table = QTableWidget(r, c)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        table.horizontalHeader().setDefaultSectionSize(self.cell_size)
        table.verticalHeader().setDefaultSectionSize(self.cell_size)
        table.horizontalHeader().setVisible(False)
        table.verticalHeader().setVisible(False)
        table.setStyleSheet("""
                    QTableWidget { 
                        background-color: white; 
                        color: black; 
                        border: 2px solid #34495e; 
                        gridline-color: #bdc3c7;
                        font-size: 18px; 
                        font-weight: bold; 
                    }
                    QTableWidget QLineEdit {
                        background-color: white;
                        color: black;
                        border: none;
                    }
                """)
        table.itemChanged.connect(self.align_cell_text)
        self.adjust_table_size(table)
        return table

    def align_cell_text(self, item):
        table = item.tableWidget()
        table.blockSignals(True)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        table.blockSignals(False)

    def create_spinbox(self, val):
        sb = QSpinBox()
        sb.setRange(1, 10)
        sb.setValue(val)
        sb.setFixedWidth(50)
        return sb

    def update_dimensions(self):
        r = self.spin_rows.value()
        c = self.spin_cols.value()

        self.table_a.setRowCount(r)
        self.table_a.setColumnCount(c)
        self.adjust_table_size(self.table_a)

        self.table_b.setRowCount(r)
        self.adjust_table_size(self.table_b)

    def adjust_table_size(self, table):
        w = (table.columnCount() * self.cell_size) + 4
        h = (table.rowCount() * self.cell_size) + 4
        table.setFixedSize(w, h)

    def matrix_to_html(self, M):
        html = '<table style="border-left: 2px solid black; border-right: 2px solid black; margin: 10px; border-collapse: collapse;">'

        html += '<tr>'
        for j in range(M.cols):
            label = self.stylize_var(f"x{j + 1}") if j < M.cols - 1 else "B"
            html += f'<td style="text-align: center; font-size: 12px; color: #7f8c8d; padding-bottom: 5px;">{label}</td>'
        html += '</tr>'

        for i in range(M.rows):
            html += '<tr>'
            for j in range(M.cols):
                style = "padding: 5px 10px; text-align: center; color: black; font-weight: bold;"
                if j == M.cols - 1:
                    style += "border-left: 1px dashed #7f8c8d;"
                html += f'<td style="{style}">{M[i, j]}</td>'
            html += '</tr>'
        html += '</table>'
        return html

    def stylize_var(self, symbol):
        s = str(symbol)
        if 'x' in s:
            num = s.replace('x', '')
            return f"<i style='font-family: serif; font-size: 18px;'>x</i><sub>{num}</sub>"
        if 'k' in s:
            num = s.replace('k', '')
            return f"<i style='font-family: serif; font-size: 18px;'>k</i><sub>{num}</sub>"
        return f"<i>{s}</i>"

    def solve_gauss(self):
        try:
            r_count = self.table_a.rowCount()
            c_count = self.table_a.columnCount()
            x_symbols = symbols(f'x1:{c_count + 1}')

            full_data = []
            for r in range(r_count):
                row = [simplify(self.table_a.item(r, c).text() if self.table_a.item(r, c) else "0") for c in
                       range(c_count)]
                val_b = self.table_b.item(r, 0).text() if self.table_b.item(r, 0) else "0"
                row.append(simplify(val_b))
                full_data.append(row)

            M = Matrix(full_data)
            self.log_area.clear()
            self.log_area.setTextColor(Qt.GlobalColor.black)

            method = self.combo_method.currentText()
            is_jordan = "Gauss-Jordan" in method

            self.log_area.append(f"<h2 style='color: #2c3e50;'>Résolution : {method}</h2>")
            self.log_area.append("<b>Système initial [A|B] :</b>")
            self.log_area.insertHtml(self.matrix_to_html(M))

            h, k = 0, 0
            rows, cols = M.shape

            while h < rows and k < cols - 1:
                candidates = [i for i in range(h, rows) if M[i, k] != 0]
                if not candidates:
                    k += 1
                    continue

                pivot_idx = min(candidates, key=lambda i: abs(M[i, k])) if not is_jordan else max(candidates,
                                                                                                  key=lambda i: abs(
                                                                                                      M[i, k]))
                if pivot_idx != h:
                    M.row_swap(h, pivot_idx)
                    explication_perm = f"""
                    <div style='margin-top: 10px; padding: 10px; border-left: 4px solid #2980b9; background-color: #ebf5fb;'>
                        <b style='color: #2980b9;'>➜ STRATÉGIE : Échange de lignes (L{h + 1} ↔ L{pivot_idx + 1})</b><br>
                        <i style='color: black;'>Pourquoi ?</i> """
                    explication_perm += f"On choisit le pivot le plus petit (<b>{abs(M[h, k])}</b>) (valeur absolue) pour simplifier les calculs." if not is_jordan else "On prend le pivot max pour la stabilité."
                    explication_perm += "</div>"
                    self.log_area.insertHtml(explication_perm)
                    self.log_area.insertHtml(self.matrix_to_html(M))

                pivot_val = M[h, k]

                if is_jordan and pivot_val != 1:
                    M.row_op(h, lambda v, j: v / pivot_val)
                    self.log_area.append(
                        f"<p style='color: #27ae60;'><b>➜ Normalisation L{h + 1} (Division par {pivot_val})</b></p>")
                    pivot_val = 1

                for i in range(rows):
                    should_eliminate = (i != h) if is_jordan else (i > h)
                    if should_eliminate and M[i, k] != 0:
                        target_val = M[i, k]
                        if not is_jordan:
                            M.row_op(i, lambda v, j: pivot_val * v - target_val * M[h, j])
                            op_text = f"L{i + 1} ← ({pivot_val})L{i + 1} - ({target_val})L{h + 1}"
                            if pivot_val == 1:
                                raison = f"On soustrait {target_val}L{h + 1} à L{i + 1} pour annuler le coefficient."
                            elif pivot_val != 1:
                                raison = f"On multiplie L{i + 1} par {pivot_val} pour faciliter l'opération puis on soustrait {target_val}L{h + 1} pour annuler le coefficient."
                        else:
                            M.row_op(i, lambda v, j: v - target_val * M[h, j])
                            op_text = f"L{i + 1} ← L{i + 1} - ({target_val})L{h + 1}"
                            raison = f"On utilise le pivot 1 pour annuler {target_val}."

                        self.log_area.append(
                            f"<p style='margin-left: 20px; color: #450700;'><b style='color: #870e00;'>➜ Élimination en L{i + 1} :</b> {raison}<br><i>{op_text}</i></p>")
                        self.log_area.insertHtml(self.matrix_to_html(M))
                h += 1
                k += 1

            self.log_area.append(f"<h3 style='color: #12b335;'>✓ Système échelonné</h3>")
            self.log_area.insertHtml(self.matrix_to_html(M))

            self.log_area.append("<h2 style='color: #6e05a3; font-size: 30px;'>Phase de Remontée</h2>")

            pivot_positions = {}
            for r in range(rows):
                for c in range(cols - 1):
                    if M[r, c] != 0:
                        pivot_positions[r] = c
                        break

            pivot_cols = set(pivot_positions.values())
            free_vars = [j for j in range(cols - 1) if j not in pivot_cols]
            known_solutions = {}
            param_idx = 1

            for f_idx in free_vars:
                p_name = f"k{param_idx}"
                known_solutions[x_symbols[f_idx]] = symbols(p_name)
                s_var = self.stylize_var(x_symbols[f_idx])
                s_param = self.stylize_var(p_name)
                self.log_area.append(
                    f"<p>➜ {s_var} est une variable libre. On pose <b>{s_var} = {s_param}</b> (réel quelconque).</p>")
                param_idx += 1

            for r in reversed(range(rows)):
                is_zero_row = all(M[r, j] == 0 for j in range(cols - 1))
                if is_zero_row:
                    if M[r, cols - 1] != 0:
                        self.log_area.append(
                            "<div style='color: red; padding: 10px; border: 2px solid red;'><b>ERREUR : Système Incompatible.</b> 0 = " + str(
                                M[r, cols - 1]) + " est impossible.</div>")
                        return
                    continue

                p_col = pivot_positions[r]
                p_var = x_symbols[p_col]
                p_val = M[r, p_col]

                eq_parts = []
                for j in range(p_col, cols - 1):
                    if M[r, j] != 0:
                        term = f"{M[r, j]}{self.stylize_var(x_symbols[j])}"
                        eq_parts.append(term)
                self.log_area.append(
                    f"<div style='margin-bottom: 10px; padding: 10px; border-left: 4px solid #7f8c8d; background: #f9f9f9;'>")
                self.log_area.append(f"<b>Ligne {r + 1} :</b> {' + '.join(eq_parts)} = {M[r, cols - 1]}<br>")

                others_expr = []
                others_html = []
                for j in range(p_col + 1, cols - 1):
                    if M[r, j] != 0:
                        others_expr.append(M[r, j] * x_symbols[j])
                        others_html.append(f"({M[r, j]}){self.stylize_var(x_symbols[j])}")
                sum_others_html = " + ".join(others_html) if others_html else "0"

                current_expr = (M[r, cols - 1] - sum(others_expr)) / p_val
                final_res_expr = simplify(current_expr.subs(known_solutions))
                known_solutions[p_var] = final_res_expr

                res_html = str(final_res_expr)
                for j in range(1, 11):
                    res_html = res_html.replace(f"k{j}", self.stylize_var(f"k{j}"))
                    res_html = res_html.replace(f"x{j}", self.stylize_var(f"x{j}"))

                s_pvar = self.stylize_var(p_var)
                self.log_area.append(
                    f"➜ On isole {s_pvar} : {s_pvar} = ({M[r, cols - 1]} - [{sum_others_html}]) / {p_val}<br>")
                self.log_area.append(f"➜ <b>{s_pvar} = {res_html}</b></div>")

            self.log_area.append(
                "<div style='background-color: #f1f2f6; padding: 15px; border-radius: 10px; border: 2px solid #2f3640; margin-top: 20px;'>")
            self.log_area.append("<b style='font-size: 30px; color: #12b335;'>CONCLUSION FINALE</b><br><br>")
            for i in range(c_count):
                var = x_symbols[i]
                res = known_solutions.get(var, "Inconnu")

                res_str = str(res)
                for original, stylized in [(f"k{j}", self.stylize_var(f"k{j}")) for j in range(1, 10)]:
                    res_str = res_str.replace(original, stylized)
                for original, stylized in [(f"x{j}", self.stylize_var(f"x{j}")) for j in range(1, 10)]:
                    res_str = res_str.replace(original, stylized)

                self.log_area.append(f"<b>{self.stylize_var(var)} = {res_str}</b><br>")

        except Exception as e:
            self.log_area.append(f"<p style='color: red;'><b>Erreur :</b> {str(e)}</p>")