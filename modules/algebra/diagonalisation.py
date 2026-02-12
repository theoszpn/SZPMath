from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                               QPushButton, QTextEdit, QLabel, QFrame,
                               QSpinBox, QLineEdit, QTableWidgetItem)
from PySide6.QtCore import Qt
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtCore import QRegularExpression
from sympy import symbols, Matrix, simplify, det, factor, Poly, solve, roots, factor_list

# Réutilisation du délégué pour la sécurité des saisies
from PySide6.QtWidgets import QStyledItemDelegate


class NumericDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        regex = QRegularExpression(r"^-?[0-9]*[/]?[0-9]*$")
        validator = QRegularExpressionValidator(regex, editor)
        editor.setValidator(validator)
        return editor


class DiagonalizationPage(QWidget):
    def __init__(self):
        super().__init__()
        self.cell_size = 60
        self.init_ui()

    def init_ui(self):
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        self.left_column = QVBoxLayout()
        self.left_column.setAlignment(Qt.AlignmentFlag.AlignTop)

        lbl_title = QLabel("Module : Diagonalisation")
        lbl_title.setStyleSheet("font-weight: bold; font-size: 18px; color: #2c3e50; border: none;")
        self.left_column.addWidget(lbl_title)

        dim_layout = QHBoxLayout()
        lbl_n = QLabel("Dimension n :")
        lbl_n.setStyleSheet("font-weight: bold; color: black; border: none;")
        self.spin_n = QSpinBox()
        self.spin_n.setRange(2, 4)
        self.spin_n.setValue(3)
        self.spin_n.setFixedWidth(50)
        dim_layout.addWidget(lbl_n)
        dim_layout.addWidget(self.spin_n)
        dim_layout.addStretch()
        self.left_column.addLayout(dim_layout)

        self.matrix_table = QTableWidget()
        self.left_column.addWidget(self.matrix_table)

        self.btn_study = QPushButton("➜ Étudier la diagonalisation")
        self.btn_study.setStyleSheet("""
            QPushButton { 
                background-color: #2980b9; color: white; padding: 12px; 
                font-weight: bold; border-radius: 5px; margin-top: 10px;
                text-align: left; padding-left: 20px; border: none;
            }
            QPushButton:hover { background-color: #3498db; border-left: 8px solid #1a5276; }
        """)
        self.btn_study.clicked.connect(self.study_diagonalization)

        self.btn_view_3d = QPushButton("🌐 Envoyer vers la Visualisation 3D")
        self.btn_view_3d.setStyleSheet("""
            QPushButton { 
                background-color: #8e44ad; color: white; padding: 12px; 
                font-weight: bold; border-radius: 5px; margin-top: 5px;
                text-align: left; padding-left: 20px; border: none;
            }
            QPushButton:hover { background-color: #9b59b6; border-left: 8px solid #4a235a; }
        """)

        self.left_column.addWidget(self.btn_view_3d)
        self.left_column.addWidget(self.btn_study)
        self.left_column.addStretch()

        self.right_column = QVBoxLayout()
        lbl_log = QLabel("Analyse et démonstrations")
        lbl_log.setStyleSheet("font-weight: bold; font-size: 16px; color: #000000; border: none;")
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setStyleSheet(
            "background-color: white; color: black; border: 2px solid #bdc3c7; border-radius: 5px; font-size: 18px; padding: 10px;")
        self.right_column.addWidget(lbl_log)
        self.right_column.addWidget(self.log_area)

        self.main_layout.addLayout(self.left_column, 1)
        self.main_layout.addLayout(self.right_column, 4)

        self.spin_n.valueChanged.connect(self.update_matrix)
        self.update_matrix()

    def update_matrix(self):
        n = self.spin_n.value()
        self.matrix_table.setRowCount(n)
        self.matrix_table.setColumnCount(n)
        self.matrix_table.setFixedSize(n * self.cell_size + 4, n * self.cell_size + 4)
        self.matrix_table.horizontalHeader().setVisible(False)
        self.matrix_table.verticalHeader().setVisible(False)
        self.matrix_table.horizontalHeader().setDefaultSectionSize(self.cell_size)
        self.matrix_table.verticalHeader().setDefaultSectionSize(self.cell_size)
        self.matrix_table.setStyleSheet("""
            QTableWidget { background-color: white; color: black; border: 2px solid #2c3e50; font-weight: bold; font-size: 20px; outline: 0; }
            QTableWidget::item { color: black; }
            QTableWidget::item:selected { background-color: #e8f4fd; color: black; }
        """)
        self.matrix_table.setItemDelegate(NumericDelegate())
        for r in range(n):
            for c in range(n):
                item = QTableWidgetItem("")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.matrix_table.setItem(r, c, item)

    def to_math_html(self, expr):
        import re
        s = str(expr)
        # Modification ici pour supporter 'n' et les variables dans les puissances
        s = re.sub(r"\*\*([a-zA-Z0-9]+)", r"<sup>\1</sup>", s)
        s = s.replace("*", "")
        s = s.replace("sqrt", "√")
        return s.replace(" ", "&nbsp;")

    def make_matrix_html(self, matrix, label=""):
        rows_html = ""
        for r in range(matrix.rows):
            cols_html = "".join([
                f"<td style='padding:5px 10px; text-align:center; white-space:nowrap;'>{self.to_math_html(matrix[r, c])}</td>"
                for c in range(matrix.cols)])
            rows_html += f"<tr>{cols_html}</tr>"
        return f"""<table border='0' cellspacing='0' cellpadding='0' style='display:inline-table; vertical-align:middle;'><tr><td style='vertical-align:middle; padding-right:5px;'><b>{label}</b></td><td style='border-left: 2px solid #2c3e50; border-top: 2px solid #2c3e50; border-bottom: 2px solid #2c3e50; width: 3px;'>&nbsp;</td><td><table border='0' cellspacing='0' cellpadding='0'>{rows_html}</table></td><td style='border-right: 2px solid #2c3e50; border-top: 2px solid #2c3e50; border-bottom: 2px solid #2c3e50; width: 3px;'>&nbsp;</td></tr></table>"""

    def study_diagonalization(self):
        try:
            from sympy import factor_list, sqrt, symbols, Matrix, simplify, factor, det, Poly, solve

            n = self.spin_n.value()
            data = []
            for r in range(n):
                row = []
                for c in range(n):
                    val = self.matrix_table.item(r, c).text()
                    row.append(simplify(val) if val else 0)
                data.append(row)

            A = Matrix(data)
            lam = symbols('λ')
            I = Matrix.eye(n)
            CharMat = A - lam * I

            self.log_area.clear()

            self.log_area.insertHtml(
                "<h2 style='color: #2c3e50;'>Étape 1 : Calcul du polynôme caractéristique</h2><br>")
            self.log_area.insertHtml(self.make_matrix_html(A, "A = "))
            self.log_area.insertHtml("<br><br><b>P(λ) = det(A - λI)</b> :<br>")
            self.log_area.insertHtml(self.make_matrix_html(CharMat))

            self.log_area.insertHtml("<br><br><b>Développement par la ligne 1 :</b><br>")

            line1_html = "<table border='0' cellspacing='0' cellpadding='0'><tr><td style='vertical-align: middle; font-size: 18px;'>P(λ) = </td>"
            expr_terms = []
            first_visible_term = True
            for j in range(n):
                coeff = CharMat[0, j]
                if coeff == 0: continue
                sign_val = 1 if (0 + j) % 2 == 0 else -1
                sub_mat = CharMat.minor_submatrix(0, j)
                sub_det = factor(simplify(det(sub_mat)))
                term_expr = sign_val * coeff * sub_det
                expr_terms.append(term_expr)
                display_sign = ("+" if sign_val == 1 else "-") if not first_visible_term else (
                    "" if sign_val == 1 else "-")
                first_visible_term = False
                prefix = f"{display_sign} ({self.to_math_html(coeff)}) × "
                line1_html += f"<td style='vertical-align: middle; font-size: 17px; padding-left: 10px; white-space: nowrap;'>{prefix} det </td><td style='vertical-align: middle;'>{self.make_matrix_html(sub_mat)}</td>"
            line1_html += "</tr></table>"
            self.log_area.insertHtml(line1_html)

            structured_parts = []
            for i, term in enumerate(expr_terms):
                t_str = self.to_math_html(term)
                structured_parts.append(f" + {t_str}" if i > 0 and not t_str.startswith("-") else f" {t_str}")
            self.log_area.insertHtml(
                f"<div style='margin-top:15px; margin-left:10px; font-size: 18px;'>P(λ) = {''.join(structured_parts)}</div>")

            poly_full = simplify(sum(expr_terms))
            poly_factored = factor(poly_full)

            self.log_area.insertHtml("<br><br><b style='font-size: 24px;'>Conclusion sur le polynôme :</b><br>")
            self.log_area.insertHtml(
                f"<div style='background-color: #fcf3cf; padding: 15px; border-left: 5px solid #f1c40f; margin-top:10px;'>")
            if poly_full != poly_factored:
                self.log_area.insertHtml(f"<br><b>Forme développée :</b> {self.to_math_html(poly_full)}<br>")
            self.log_area.insertHtml(
                f"<b>Forme factorisée finale :</b> <span style='color: #d35400; font-size: 20px;'><b>P(λ) = {self.to_math_html(poly_factored)}</b></span><br>")
            self.log_area.insertHtml("</div>")

            self.log_area.insertHtml(
                "<br><h2 style='color: #2c3e50; margin-top:30px;'>Étape 2 : Détermination du spectre de A</h2>")
            coeff_global, factors_data = factor_list(poly_full)
            real_roots_found = {}

            for f, exp in factors_data:
                p_factor = Poly(f, lam)
                deg = p_factor.degree()
                if deg == 1:
                    r = solve(f, lam)[0]
                    if r.is_real:
                        real_roots_found[r] = real_roots_found.get(r, 0) + exp
                        self.log_area.insertHtml(
                            f"<br>• Le membre <b>({self.to_math_html(f)})</b> donne la racine <b>λ = {r}</b>.")
                elif deg == 2:
                    a_v = p_factor.coeff_monomial(lam ** 2);
                    b_v = p_factor.coeff_monomial(lam ** 1);
                    c_v = p_factor.coeff_monomial(lam ** 0)
                    delta = b_v ** 2 - 4 * a_v * c_v
                    self.log_area.insertHtml(
                        f"<br>• Le membre <b>({self.to_math_html(f)})</b> est un polynôme du second degré :")
                    self.log_area.insertHtml(
                        f"<div style='margin-left:20px;'>Δ = {b_v}<sup>2</sup> - 4({a_v})({c_v}) = <b>{delta}</b><br>")
                    if delta > 0:
                        r1 = simplify((-b_v + sqrt(delta)) / (2 * a_v));
                        r2 = simplify((-b_v - sqrt(delta)) / (2 * a_v))
                        real_roots_found[r1] = real_roots_found.get(r1, 0) + exp;
                        real_roots_found[r2] = real_roots_found.get(r2, 0) + exp
                        self.log_area.insertHtml(
                            f"Δ > 0 : deux racines réelles distinctes : <b>λ₁ = {r1}</b> et <b>λ₂ = {r2}</b>.")
                    elif delta == 0:
                        r0 = simplify(-b_v / (2 * a_v));
                        real_roots_found[r0] = real_roots_found.get(r0, 0) + (exp * 2)
                        self.log_area.insertHtml(f"Δ = 0 : une racine double <b>λ = {r0}</b>.")
                    else:
                        self.log_area.insertHtml("<span style='color:red;'>Δ < 0 : pas de racines réelles.</span>")
                    self.log_area.insertHtml("</div>")

            if not real_roots_found:
                self.log_area.insertHtml("<br><b style='color:red;'>Le spectre réel est vide.</b>")
                return

            sorted_roots = sorted(list(real_roots_found.keys()), key=lambda x: float(x.evalf()))
            spec_str = " ; ".join([str(r) for r in sorted_roots])
            self.log_area.insertHtml(
                f"<br><div style='background-color: #FFFFFF; padding: 15px; border: 2px solid #1abc9c; border-radius: 5px; margin-top:20px;'><b style='font-size: 20px;'>Spec(A) = {{ {spec_str} }}</b><br><br>")
            for r in sorted_roots:
                m = real_roots_found[r]
                self.log_area.insertHtml(f"• Valeur propre <b>λ = {r}</b> : multiplicité algébrique <b>{m}</b><br>")
            self.log_area.insertHtml("</div>")

            self.log_area.insertHtml(
                "<br><h2 style='color: #2c3e50; margin-top:30px;'>Étape 3 : Détermination des sous-espaces propres</h2>")

            vars_list = symbols(f'x1:{n + 1}')
            X_vec = Matrix(vars_list)
            eigen_summary = []

            for val in sorted_roots:
                self.log_area.insertHtml(
                    f"<br><br><b style='color: #e67e22; font-size: 18px;'>Pour λ = {val} :</b><br>")
                self.log_area.insertHtml(f"E<sub>{val}</sub> = {{ X ∈ M<sub>{n},1</sub>(ℝ) | AX = {val}X }}<br>")

                sys_init_html = "<table border='0' cellspacing='0' cellpadding='0' style='margin: 15px;'><tr><td style='border-left: 3px solid black; padding-left: 10px; font-size: 17px;'>"
                eqs_init = [
                    f"{self.to_math_html(sum(A[i, j] * vars_list[j] for j in range(n)))} = {self.to_math_html(val * vars_list[i])}"
                    for i in range(n)]
                sys_init_html += "<br>".join(eqs_init) + "</td></tr></table>"
                self.log_area.insertHtml("<br><b>1. Système initial AX = λX :</b>" + sys_init_html)

                M_sub = A - val * Matrix.eye(n)
                sys_left_html = "<table border='0' cellspacing='0' cellpadding='0' style='margin: 15px;'><tr><td style='border-left: 3px solid black; padding-left: 10px; font-size: 17px;'>"
                eqs_left = [f"{self.to_math_html(sum(M_sub[i, j] * vars_list[j] for j in range(n)))} = 0" for i in
                            range(n)]
                sys_left_html += "<br>".join(eqs_left) + "</td></tr></table>"
                self.log_area.insertHtml("<b>2. Regroupement à gauche (A - λI)X = 0 :</b>" + sys_left_html)

                sol = solve(M_sub * X_vec, vars_list)
                free_vars = [v for v in vars_list if v not in sol.keys()]
                sys_res_html = "<table border='0' cellspacing='0' cellpadding='0' style='margin: 15px;'><tr><td style='border-left: 3px solid black; padding-left: 10px; font-size: 17px;'>"
                res_lines = [f"{v} = {self.to_math_html(sol[v])}" if v in sol else f"<b>{v}</b> est libre" for v in
                             vars_list]
                sys_res_html += "<br>".join(res_lines) + "</td></tr></table>"
                self.log_area.insertHtml("<b>3. Résolution et expression des variables :</b>" + sys_res_html)

                basis = M_sub.nullspace()
                eigen_summary.append({'val': val, 'dim': len(basis), 'mult': real_roots_found[val], 'basis': basis})

                if not basis: continue
                X_substituted = X_vec.subs(sol)
                decomp_html = "<table border='0' cellspacing='0' cellpadding='0' style='margin-top: 15px;'><tr>"
                decomp_html += f"<td style='vertical-align: middle;'>{self.make_matrix_html(X_vec, 'X = ')}</td>"
                decomp_html += "<td style='vertical-align: middle; padding: 0 10px; font-size: 20px;'>=</td>"
                decomp_html += f"<td style='vertical-align: middle;'>{self.make_matrix_html(X_substituted)}</td>"
                decomp_html += "<td style='vertical-align: middle; padding: 0 10px; font-size: 20px;'>=</td>"
                for i, f_var in enumerate(free_vars):
                    if i > 0: decomp_html += "<td style='vertical-align: middle; padding: 0 8px; font-size: 20px;'>+</td>"
                    decomp_html += f"<td style='vertical-align: middle; font-size: 18px; padding-right: 5px; white-space: nowrap;'>{f_var}</td>"
                    decomp_html += f"<td style='vertical-align: middle;'>{self.make_matrix_html(basis[i])}</td>"
                decomp_html += "</tr></table>"
                self.log_area.insertHtml(decomp_html)

                basis_tuples = [f"({', '.join([str(v_i) for v_i in v])})" for v in basis]
                cond = ", ".join([f"{v} ∈ ℝ" for v in free_vars])
                lin_comb_horiz = " + ".join([f"{free_vars[i]}{basis_tuples[i]}" for i in range(len(free_vars))])
                self.log_area.insertHtml(
                    f"<br><div style='font-size: 24px; margin-top:15px; background-color: #FFFFFF; padding: 10px; border: 1px solid #bdc3c7;'>E<sub>{val}</sub> = {{ {lin_comb_horiz} | {cond} }}</div>")

            self.log_area.insertHtml(
                "<br><h2 style='color: #2c3e50; margin-top:30px;'>Étape 4 : Vérification de la diagonalisabilité</h2>")
            self.log_area.insertHtml(
                "<br><p><i>A est diagonalisable si et seulement si, pour chaque valeur propre λᵢ, la dimension de son sous-espace vectoriel E<sub>λᵢ</sub> est égale à la multiplicité algébrique de la valeur propre.</i></p>")

            is_diag = True
            diag_checks_html = ""
            final_p_cols = []
            final_d_vals = []

            for item in eigen_summary:
                match = item['dim'] == item['mult']
                icon = "✅" if match else "❌"
                if not match: is_diag = False
                diag_checks_html += f"<br>• Valeur propre {item['val']} : dim(E<sub>{item['val']}</sub>) = {item['dim']} et multiplicité algébrique de {item['val']} = {item['mult']} {icon}<br>"
                for b_vec in item['basis']:
                    final_p_cols.append(b_vec)
                    final_d_vals.append(item['val'])

            self.log_area.insertHtml(
                f"<div style='background-color: #ebf5fb; padding: 15px; border-left: 5px solid #3498db; margin: 10px 0;'>{diag_checks_html}</div>")

            if is_diag:
                self.log_area.insertHtml(
                    "<br><p style='color: #27ae60; font-size: 18px;'><b>Conclusion : A est donc diagonalisable.</b></p>")
            else:
                self.log_area.insertHtml(
                    "<br><p style='color: #e74c3c; font-size: 18px;'><b>Conclusion : A n'est pas diagonalisable (les dimensions ne concordent pas).</b></p>")
                return

            self.log_area.insertHtml(
                "<br><h2 style='color: #2c3e50; margin-top:30px;'>Étape 5 : Construction de D et P</h2><br>")
            self.log_area.insertHtml(
                "<p>La matrice <b>D</b> est la matrice diagonale des valeurs propres. La matrice <b>P</b> est la matrice de passage dont les colonnes sont les vecteurs propres associés.</p>")

            mat_D = Matrix.diag(*final_d_vals)
            mat_P = Matrix.hstack(*final_p_cols)

            mats_display = f"<table border='0' cellspacing='20'><tr><td>{self.make_matrix_html(mat_D, 'D = ')}</td><td>{self.make_matrix_html(mat_P, 'P = ')}</td></tr></table>"
            self.log_area.insertHtml(mats_display)

            self.log_area.insertHtml(
                "<h2 style='color: #2c3e50; margin-top:30px;'>Étape 6 : Relation et Puissance n-ième</h2><br>")

            P_inv = mat_P.inv()
            self.log_area.insertHtml("<p>On calcule d'abord l'inverse de la matrice de passage <b>P⁻¹</b> :</p><br>")
            self.log_area.insertHtml(self.make_matrix_html(P_inv, "P⁻¹ = "))

            self.log_area.insertHtml("<br><p>D'après le cours, on a la relation de similitude : <b>A = PDP⁻¹</b></p>")
            self.log_area.insertHtml(
                "<br><p>On en déduit que pour tout entier naturel n : <span style='font-size: 20px; color: #d35400;'><b>Aⁿ = PDⁿP⁻¹</b></span></p>")

            self.log_area.insertHtml(
                "<br><p>Ceci simplifie grandement le calcul car <b>D<sup>n</sup></b> s'obtient en élevant chaque coefficient diagonal à la puissance <i>n</i>.</p>")

            n_sym = symbols('n', integer=True)
            mat_Dn = Matrix.diag(*[v ** n_sym for v in final_d_vals])
            mat_An = simplify(mat_P * mat_Dn * P_inv)

            self.log_area.insertHtml(
                "<br><p>En effectuant le produit matriciel, on obtient l'expression générale :</p><br>")
            self.log_area.insertHtml(
                "<div style='background-color: #fdf2e9; padding: 15px; border: 2px solid #e67e22; border-radius: 5px; margin-top:10px;'>")
            self.log_area.insertHtml(self.make_matrix_html(mat_An, "Aⁿ = "))
            self.log_area.insertHtml("</div>")

        except Exception as e:
            self.log_area.append(f"<br><b style='color:red;'>Erreur : {str(e)}</b>")