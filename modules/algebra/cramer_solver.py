from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                               QPushButton, QTextEdit, QLabel, QFrame, QHeaderView,
                               QSpinBox, QSizePolicy)
from PySide6.QtCore import Qt
from sympy import simplify, Matrix, Rational


class CramerSolverPage(QWidget):
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
        self.spin_n = QSpinBox()
        self.spin_n.setRange(1, 10)
        self.spin_n.setValue(3)
        self.spin_n.setFixedWidth(60)

        dim_lbl = QLabel("Dimension n (Matrice carrée):")
        dim_lbl.setStyleSheet("color: #2f3640; font-weight: bold;")
        dims_layout.addWidget(dim_lbl)
        dims_layout.addWidget(self.spin_n)
        dims_layout.addStretch()
        left_column.addLayout(dims_layout)

        # 2. Zone des Matrices [A | B]
        matrix_container = QHBoxLayout()
        matrix_container.setSpacing(0)

        self.table_a = self.create_table(3, 3)

        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setLineWidth(2)
        separator.setStyleSheet("color: #34495e; margin: 0 5px;")

        self.table_b = self.create_table(3, 1, color="#0984e3")

        matrix_container.addWidget(self.table_a)
        matrix_container.addWidget(separator)
        matrix_container.addWidget(self.table_b)
        matrix_container.addStretch()
        left_column.addLayout(matrix_container)

        btn_style = """
            QPushButton { 
                background-color: #34495e; color: white; padding: 12px; 
                font-weight: bold; border-radius: 5px; margin-top: 10px;
                min-width: 250px; text-align: left; padding-left: 20px;
            }
            QPushButton:hover { background-color: #2c3e50; }
        """
        self.btn_det = QPushButton("➜ Calculer le Déterminant det(A)")
        self.btn_inv = QPushButton("➜ Calculer l'Inverse A⁻¹ (Cramer)")
        self.btn_solve = QPushButton("➜ Résoudre le Système (Cramer)")

        for b in [self.btn_det, self.btn_inv, self.btn_solve]:
            b.setStyleSheet(btn_style)
            left_column.addWidget(b)

        self.btn_solve.setStyleSheet(btn_style.replace("#34495e", "#2980b9"))  # Bleu pour l'action principale

        left_column.addStretch()

        right_column = QVBoxLayout()
        lbl_steps = QLabel("Etapes de résolution")
        lbl_steps.setStyleSheet("font-weight: bold; font-size: 16px; color: black")

        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setStyleSheet("""
            QTextEdit {
                background-color: white; color: black; border: 2px solid #bdc3c7;
                border-radius: 5px; font-size: 18px;
            }
        """)
        self.log_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        right_column.addWidget(lbl_steps)
        right_column.addWidget(self.log_area, 1)

        self.main_layout.addLayout(left_column, 1)
        self.main_layout.addLayout(right_column, 5)

        self.spin_n.valueChanged.connect(self.update_dimensions)
        self.btn_det.clicked.connect(self.solve_determinant)
        self.btn_inv.clicked.connect(self.solve_inverse)
        self.btn_solve.clicked.connect(self.solve_system_cramer)

    def create_table(self, r, c, color="black"):
        table = QTableWidget(r, c)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        table.horizontalHeader().setDefaultSectionSize(self.cell_size)
        table.verticalHeader().setDefaultSectionSize(self.cell_size)
        table.horizontalHeader().setVisible(False)
        table.verticalHeader().setVisible(False)

        table.setStyleSheet(f"""
                    QTableWidget {{ 
                        background-color: white; 
                        color: {color}; 
                        border: 2px solid #34495e; 
                        gridline-color: #bdc3c7;
                        font-size: 18px; 
                        font-weight: bold; 
                    }}
                    QTableWidget QLineEdit {{
                        background-color: white;
                        color: black;
                        border: none;
                    }}
                """)
        table.itemChanged.connect(self.align_cell_text)
        self.adjust_table_size(table)
        return table

    def align_cell_text(self, item):
        table = item.tableWidget()
        table.blockSignals(True)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        table.blockSignals(False)

    def update_dimensions(self):
        n = self.spin_n.value()
        self.table_a.setRowCount(n)
        self.table_a.setColumnCount(n)
        self.table_b.setRowCount(n)
        self.adjust_table_size(self.table_a)
        self.adjust_table_size(self.table_b)

    def adjust_table_size(self, table):
        w = (table.columnCount() * self.cell_size) + 4
        h = (table.rowCount() * self.cell_size) + 4
        table.setFixedSize(w, h)

    def stylize_var(self, symbol):
        s = str(symbol)
        if 'x' in s:
            num = s.replace('x', '')
            return f"<i style='font-family: serif; font-size: 18px;'>x</i><sub>{num}</sub>"
        return f"<i>{s}</i>"

    def matrix_to_html(self, M, title="", highlight_col=-1):
        html = f"<b>{title}</b><br>" if title else ""
        html += '<table style="border-left: 2px solid black; border-right: 2px solid black; margin: 10px; border-collapse: collapse;">'
        for i in range(M.rows):
            html += '<tr>'
            for j in range(M.cols):
                bg_color = "#e3f2fd" if j == highlight_col else "white"

                style = f"padding: 5px 10px; text-align: center; color: black; font-weight: bold; font-size: 16px; background-color: {bg_color};"
                html += f'<td style="{style}">{M[i, j]}</td>'
            html += '</tr>'
        html += '</table>'
        return html

    def get_matrices(self):
        n = self.spin_n.value()
        a_data = [[simplify(self.table_a.item(r, c).text() if self.table_a.item(r, c) else "0") for c in range(n)] for r
                  in range(n)]
        b_data = [[simplify(self.table_b.item(r, 0).text() if self.table_b.item(r, 0) else "0")] for r in range(n)]
        return Matrix(a_data), Matrix(b_data)

    def solve_determinant(self):
        try:
            A, _ = self.get_matrices()
            n = A.rows
            self.log_area.clear()
            self.log_area.append("<h2>Calcul détaillé du Déterminant det(A)</h2><br>")
            self.log_area.insertHtml(self.matrix_to_html(A, "Matrice A :"))

            self.log_area.append(
                "<div style='background-color: #f8f9fa; padding: 10px; border-left: 4px solid #34495e;'>")
            self.log_area.append(
                "<b>Rappel :</b> Le déterminant se calcule par le développement suivant une ligne ou une colonne :<br>")
            self.log_area.append(
                "<i style='font-size: 20px;'>det(A) = Σ (-1)<sup>i+j</sup> × a<sub>i,j</sub> × Δ<sub>i,j</sub></i><br>")

            if n == 1:
                self.log_area.append(f"Matrice 1x1 : det(A) = {A[0, 0]}")
                return

            best_type, best_idx, max_zeros = self.find_best_path(A)
            type_str = "la ligne" if best_type == "row" else "la colonne"
            raison = f"car elle contient <b>{max_zeros} zéro(s)</b>." if max_zeros > 0 else "par défaut (pas de zéros)."

            self.log_area.append(
                f"<b style='color: #2980b9;'>➜ STRATÉGIE :</b> On développe suivant <b>{type_str} {best_idx + 1}</b> {raison}<br>")

            total_det = 0
            elements = []
            if best_type == "row":
                for j in range(n): elements.append((A[best_idx, j], best_idx, j))
            else:
                for i in range(n): elements.append((A[i, best_idx], i, best_idx))

            formula_parts = []

            for val, r, c in elements:
                sign = (-1) ** (r + c)
                sign_str = "+" if sign > 0 else "-"

                if val == 0:
                    formula_parts.append(
                        f"<span style='color: #7f8c8d; font-size: 20px;'>{sign_str}(0 × Δ<sub>{r + 1},{c + 1}</sub>)</span>")
                    continue

                M_sub = A.minor_submatrix(r, c)
                det_sub = M_sub.det()

                formula_parts.append(f"<b>{sign_str}({val}) × detΔ<sub>{r + 1},{c + 1}</sub></b>")

                self.log_area.append(
                    f"<hr>Élément <b>a<sub>{r + 1},{c + 1}</sub> = {val}</b> (Signe : (-1)<sup>{r + 1}+{c + 1}</sup> = {sign_str}1)<br>")
                self.log_area.insertHtml(self.matrix_to_html(M_sub, f"<br>Sous-matrice Δ<sub>{r + 1},{c + 1}</sub> :"))
                self.log_area.append(f"➜ detΔ<sub>{r + 1},{c + 1}</sub> = {det_sub}")

                total_det += sign * val * det_sub

            self.log_area.append("<hr>")
            self.log_area.append(f"<b style='font-size: 25px; color: #27ae60'>Calcul final :</b><br>")

            full_formula = " ".join(formula_parts).replace("+ -", "- ").replace("- -", "+ ").replace("+ +", "+ ")
            full_formula = full_formula.strip()

            if full_formula.startswith("+"):
                full_formula = full_formula[1:].strip()

            self.log_area.append(f"<p style='font-size: 20px; color: black;'>det(A) = {full_formula}</p>")
            self.log_area.append(f"<p style='font-size: 22px; color: black;'><br><b>➜ det(A) = {total_det}</b></p>")

        except Exception as e:
            self.log_area.append(f"<b style='color: red;'>Erreur : {str(e)}</b>")

    def find_best_path(self, M):
        n = M.rows
        best_type = "row"
        best_idx = 0
        max_zeros = -1

        for i in range(n):
            zeros = list(M.row(i)).count(0)
            if zeros > max_zeros:
                max_zeros = zeros
                best_idx = i
                best_type = "row"

        for j in range(n):
            zeros = list(M.col(j)).count(0)
            if zeros > max_zeros:
                max_zeros = zeros
                best_idx = j
                best_type = "col"

        return best_type, best_idx, max_zeros

    def solve_inverse(self):
        try:
            A, _ = self.get_matrices()
            n = A.rows
            self.log_area.clear()
            self.log_area.append("<h2 style='color: #2c3e50;'>Inversion de la matrice A⁻¹</h2>")
            self.log_area.insertHtml(self.matrix_to_html(A, "<br>Matrice A :"))

            self.log_area.append(
                "<div style='background-color: #f8f9fa; padding: 15px; border-left: 5px solid #34495e; border-radius: 5px;'>")
            self.log_area.append("<b>Formule de l'inverse :</b><br>")
            self.log_area.append(
                "<center><i style='font-size: 20px;'>A⁻¹ = (1 / det(A)) × <sup>t</sup>com(A)</i></center><br>")

            det_a = A.det()
            self.log_area.append("<h3>1. Calcul du déterminant det(A)</h3><br>")
            self.log_area.append(f"det(A) = Σ (-1)<sup>i+j</sup> × a<sub>i,j</sub> × Δ<sub>i,j</sub><br>")

            best_type, best_idx, _ = self.find_best_path(A)
            terms = []
            if best_type == "row":
                for j in range(n):
                    val = A[best_idx, j]
                    if val != 0:
                        sign = "+" if ((-1) ** (best_idx + j)) > 0 else "-"
                        m_det = A.minor_submatrix(best_idx, j).det()
                        terms.append(f"{sign}({val} × {m_det})")
            else:
                for i in range(n):
                    val = A[i, best_idx]
                    if val != 0:
                        sign = "+" if ((-1) ** (i + best_idx)) > 0 else "-"
                        m_det = A.minor_submatrix(i, best_idx).det()
                        terms.append(f"{sign}({val} × {m_det})")

            calc_str = " ".join(terms).replace("+ -", "- ").replace("- -", "+ ")
            if calc_str.startswith("+"): calc_str = calc_str[1:]

            self.log_area.append(f"➜ det(A) = {calc_str} = <b>{det_a}</b>")

            if det_a == 0:
                self.log_area.append(
                    "<p style='color: red;'><b>Erreur : det(A) = 0. La matrice n'est pas inversible.</b></p>")
                return

            self.log_area.append("<hr><h3>2. Construction de la Comatrice com(A)</h3>")

            symbol_table = '<table style="border: 1px solid black; border-collapse: collapse; margin: 10px;">'
            for i in range(n):
                symbol_table += '<tr>'
                for j in range(n):
                    sign = "+" if (i + j) % 2 == 0 else "-"
                    symbol_table += f'<td style="border: 1px solid #bdc3c7; padding: 10px;">{sign}Δ<sub>{i + 1},{j + 1}</sub></td>'
                symbol_table += '</tr>'
            symbol_table += '</table>'
            self.log_area.append("<b>A. Structure des cofacteurs :</b>")
            self.log_area.insertHtml(symbol_table)

            sub_matrix_table = '<table style="border: 1px solid black; border-collapse: collapse; margin: 10px;">'
            for i in range(n):
                sub_matrix_table += '<tr>'
                for j in range(n):
                    sign = "+" if (i + j) % 2 == 0 else "-"
                    M_sub = A.minor_submatrix(i, j)
                    sub_matrix_table += f'<td style="border: 1px solid #bdc3c7; padding: 5px;">{sign}{self.matrix_to_html(M_sub)}</td>'
                sub_matrix_table += '</tr>'
            sub_matrix_table += '</table>'
            self.log_area.append("<br><b>B. Remplacement par les sous-matrices Δ<sub>i,j</sub> :</b>")
            self.log_area.insertHtml(sub_matrix_table)

            comatrice = Matrix(n, n, lambda i, j: ((-1) ** (i + j)) * A.minor_submatrix(i, j).det())
            self.log_area.append("<br><b>C. Comatrice calculée com(A) :</b>")
            self.log_area.insertHtml(self.matrix_to_html(comatrice))

            adjugate = comatrice.transpose()
            self.log_area.append("<hr><h3>3. Transposition de la comatrice <sup>t</sup>com(A)</h3>")
            self.log_area.append("On échange les lignes et les colonnes :")
            self.log_area.insertHtml(self.matrix_to_html(adjugate))

            inverse = A.inv()
            self.log_area.append(
                "<hr><div style='background-color: #f1f9f5; padding: 15px; border: 2px solid #27ae60; border-radius: 10px;'>")
            self.log_area.append("<b style='font-size: 20px; color: #27ae60;'>4. Résultat Final A⁻¹</b><br>")
            self.log_area.append(f"A⁻¹ = (1 / {det_a}) × <sup>t</sup>com(A)<br>")
            self.log_area.insertHtml(self.matrix_to_html(inverse))

        except Exception as e:
            self.log_area.append(f"<b style='color: red;'>Erreur : {str(e)}</b>")

    def solve_system_cramer(self):
        try:
            A, B = self.get_matrices()
            n = A.rows
            self.log_area.clear()
            self.log_area.append("<h2 style='color: #2c3e50;'>Résolution par la méthode de Cramer</h2>")

            det_a = A.det()
            self.log_area.append(
                "<div style='background-color: #f8f9fa; padding: 15px; border-left: 5px solid #34495e; border-radius: 5px;'>")
            self.log_area.append("<b>Condition de résolution :</b><br>")
            self.log_area.append(
                "Un système est dit 'de Cramer' si la matrice A est carrée et si son déterminant est non nul (det(A) ≠ 0).")

            self.log_area.append("<h3>1. Calcul du déterminant principal Δ</h3>")
            best_type, best_idx, _ = self.find_best_path(A)

            self.log_area.append(f"Formule : det(A) = Σ (-1)<sup>i+j</sup> × a<sub>i,j</sub> × Δ<sub>i,j</sub>")

            terms = []
            elements = []
            if best_type == "row":
                for j in range(n): elements.append((A[best_idx, j], best_idx, j))
            else:
                for i in range(n): elements.append((A[i, best_idx], i, best_idx))

            for val, r, c in elements:
                if val != 0:
                    sign = "+" if ((-1) ** (r + c)) > 0 else "-"
                    sub_det = A.minor_submatrix(r, c).det()
                    terms.append(f"{sign}({val} × {sub_det})")

            calc_str = " ".join(terms).replace("+ -", "- ").replace("- -", "+ ")
            if calc_str.startswith("+"): calc_str = calc_str[1:]
            self.log_area.append(f"<br>Calcul : {calc_str}")

            self.log_area.append(f"<br>Résultat : <b>det(A) = {det_a}</b>")

            if det_a == 0:
                self.log_area.append(
                    "<p style='color: red; margin-top: 10px;'><b>Erreur : det(A) = 0. Le système n'est pas de Cramer.</b></p>")
                return

            self.log_area.append("<hr><h3>2. Calcul des inconnues</h3>")
            self.log_area.append(f"On remplace successivement chaque colonne de A par le vecteur B :")

            results = []
            for i in range(n):
                Ai = A.copy()
                for row_idx in range(n):
                    Ai[row_idx, i] = B[row_idx]

                det_ai = Ai.det()
                xi_sym = self.stylize_var(f"x{i + 1}")

                self.log_area.append(
                    f"<div style='margin-top: 20px; padding: 10px; border: 1px solid #bdc3c7; border-radius: 5px;'>")
                self.log_area.append(f"<b>Recherche de {xi_sym} :</b><br>")

                fraction_html = f"""
                <table style='margin: 10px; border-collapse: collapse;'>
                    <tr>
                        <td rowspan='2' style='vertical-align: middle; padding-right: 10px; font-size: 20px;'>
                            {xi_sym} = 
                        </td>
                        <td style='border-bottom: 2px solid black; padding: 5px; text-align: center;'>
                            {self.matrix_to_html(Ai, highlight_col=i)}  </td>
                    </tr>
                    <tr>
                        <td style='text-align: center; padding-top: 5px; font-size: 18px;'>{det_a}</td>
                    </tr>
                </table>
                """
                self.log_area.insertHtml(fraction_html)

                best_t_i, best_idx_i, _ = self.find_best_path(Ai)
                terms_i = []
                elements_i = []
                if best_t_i == "row":
                    for j in range(n): elements_i.append((Ai[best_idx_i, j], best_idx_i, j))
                else:
                    for j in range(n): elements_i.append((Ai[j, best_idx_i], j, best_idx_i))

                for v, r, c in elements_i:
                    if v != 0:
                        s = "+" if ((-1) ** (r + c)) > 0 else "-"
                        sd = Ai.minor_submatrix(r, c).det()
                        terms_i.append(f"{s}({v} × {sd})")

                calc_ai_str = " ".join(terms_i).replace("+ -", "- ").replace("- -", "+ ")
                if calc_ai_str.startswith("+"): calc_ai_str = calc_ai_str[1:]

                sub_calc_html = f"""
                                <table style='margin: 10px; border-collapse: collapse;'>
                                    <tr>
                                        <td rowspan='2' style='vertical-align: middle; padding-right: 10px; font-size: 20px;'>
                                            {xi_sym} = 
                                        </td>
                                        <td style='border-bottom: 2px solid black; padding: 5px; text-align: center;'>{calc_ai_str}</td>
                                        <td rowspan='2' style='vertical-align: middle; padding: 0 10px; font-size: 20px;'> = </td>
                                        <td style='border-bottom: 2px solid black; padding: 5px; text-align: center;'>{det_ai}</td>
                                    </tr>
                                    <tr>
                                        <td style='text-align: center; padding-top: 5px; font-size: 18px;'>{det_a}</td>
                                        <td style='text-align: center; padding-top: 5px; font-size: 18px;'>{det_a}</td>
                                    </tr>
                                </table>
                                """
                self.log_area.insertHtml(sub_calc_html)

                val_final = Rational(det_ai, det_a)
                results.append(val_final)
                self.log_area.append(f"<p style='font-size: 18px;'>➜ <b>{xi_sym} = {val_final}</b></p>")

            self.log_area.append(
                "<div style='background-color: #f1f9f5; padding: 15px; border: 2px solid #27ae60; border-radius: 10px; margin-top: 25px;'>")
            self.log_area.append("<b style='font-size: 28px; color: #27ae60;'>CONCLUSION FINALE</b><br>")
            for i, res in enumerate(results):
                self.log_area.append(f"<b style='font-size: 20px;'>{self.stylize_var(f'x{i + 1}')} = {res}   </b>")

        except Exception as e:
            self.log_area.append(f"<b style='color: red;'>Erreur : {str(e)}</b>")