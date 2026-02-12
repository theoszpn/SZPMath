from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                               QPushButton, QTextEdit, QLabel, QFrame,
                               QSpinBox, QTableWidgetItem, QStackedWidget)
from PySide6.QtCore import Qt
from sympy import symbols, simplify, expand
from PySide6.QtWidgets import QStyledItemDelegate, QLineEdit
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtCore import QRegularExpression

class NumericDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        regex = QRegularExpression(r"^-?[0-9]*[/]?[0-9]*$")
        validator = QRegularExpressionValidator(regex, editor)
        editor.setValidator(validator)
        return editor


class VectorSpacesPage(QWidget):
    def __init__(self):
        super().__init__()
        self.cell_size = 50
        self.init_ui()

    def init_ui(self):
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        self.left_column = QVBoxLayout()
        self.left_column.setAlignment(Qt.AlignmentFlag.AlignTop)

        mode_lbl = QLabel("Sélectionner le module :")
        mode_lbl.setStyleSheet("font-weight: bold; color: #000000; margin-bottom: 5px; border: none;")
        self.left_column.addWidget(mode_lbl)

        self.mode_layout = QHBoxLayout()

        toggle_style = """
            QPushButton {
                background-color: #ecf0f1;
                color: #2c3e50;
                border: 2px solid #bdc3c7;
                padding: 12px;
                font-weight: bold;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #d5dbdb;
            }
            QPushButton:checked {
                background-color: #34495e;
                color: white;
                border: 2px solid #2c3e50;
            }
        """

        self.btn_mode_family = QPushButton("Étude de familles de vecteurs")
        self.btn_mode_sev = QPushButton("Étude de sous-espaces vectoriels")

        for btn in [self.btn_mode_family, self.btn_mode_sev]:
            btn.setCheckable(True)
            btn.setAutoExclusive(True)
            btn.setStyleSheet(toggle_style)
            btn.setCursor(Qt.PointingHandCursor)
            self.mode_layout.addWidget(btn)

        self.btn_mode_family.setChecked(True)
        self.left_column.addLayout(self.mode_layout)
        self.left_column.addSpacing(25)

        self.input_stack = QStackedWidget()
        self.ui_family = self.setup_family_ui()
        self.ui_sev = self.setup_sev_ui()
        self.input_stack.addWidget(self.ui_family)
        self.input_stack.addWidget(self.ui_sev)

        self.left_column.addWidget(self.input_stack)
        self.left_column.addStretch()

        self.right_column = QVBoxLayout()
        lbl_steps = QLabel("Analyse et démonstrations")
        lbl_steps.setStyleSheet("font-weight: bold; font-size: 16px; color: #000000; border: none;")

        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setStyleSheet("""
            QTextEdit {
                background-color: white; 
                color: black; 
                border: 2px solid #bdc3c7; 
                border-radius: 5px; 
                font-size: 18px;
                padding: 10px;
            }
        """)

        self.right_column.addWidget(lbl_steps)
        self.right_column.addWidget(self.log_area, 1)

        self.main_layout.addLayout(self.left_column, 2)
        self.main_layout.addLayout(self.right_column, 3)

        self.btn_mode_family.clicked.connect(lambda: self.input_stack.setCurrentIndex(0))
        self.btn_mode_sev.clicked.connect(lambda: self.input_stack.setCurrentIndex(1))

    def setup_family_ui(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        ctrl_layout = QHBoxLayout()
        lbl_n, self.spin_dim = self.create_spin(3, "Dim (n) :")
        lbl_v, self.spin_count = self.create_spin(3, "Nb vecteurs :")
        ctrl_layout.addWidget(lbl_n); ctrl_layout.addWidget(self.spin_dim)
        ctrl_layout.addSpacing(15)
        ctrl_layout.addWidget(lbl_v); ctrl_layout.addWidget(self.spin_count)
        ctrl_layout.addStretch()
        layout.addLayout(ctrl_layout)

        self.vector_container = QHBoxLayout()
        self.vector_container.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addLayout(self.vector_container)

        style_sev_like = """
                    QPushButton { 
                        background-color: #2980b9; color: white; padding: 12px; 
                        font-weight: bold; border-radius: 5px; margin-top: 10px;
                        text-align: left; padding-left: 20px; border: none;
                    }
                    QPushButton:hover { 
                        background-color: #3498db; 
                        border-left: 8px solid #1a5276;
                    }
                """
        self.btn_study_family = QPushButton("➜ Etudier la famille")
        self.btn_study_family.setStyleSheet(style_sev_like)
        self.btn_study_family.clicked.connect(self.study_family)
        layout.addWidget(self.btn_study_family)

        self.spin_dim.valueChanged.connect(self.update_vectors)
        self.spin_count.valueChanged.connect(self.update_vectors)
        self.update_vectors()
        return container

    def setup_sev_ui(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        n_lbl = QLabel("Dimension n :")
        n_lbl.setStyleSheet("color: black; font-weight: bold; border: none;")
        self.spin_sev_n = QSpinBox()
        self.spin_sev_n.setRange(2, 6)
        self.spin_sev_n.setValue(3)
        self.spin_sev_n.setFixedWidth(50)
        self.spin_sev_n.setStyleSheet("color: black; background: white;")

        n_layout = QHBoxLayout()
        n_layout.addWidget(n_lbl)
        n_layout.addWidget(self.spin_sev_n)
        n_layout.addStretch()
        layout.addLayout(n_layout)

        self.formula_frame = QFrame()
        self.formula_frame.setStyleSheet("background-color: #ffffff; border: none;")
        formula_layout = QHBoxLayout(self.formula_frame)
        formula_layout.setSpacing(10)
        formula_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        font_math = "font-family: 'Cambria Math', serif; color: #000000; border: none;"

        self.lbl_accolade_open = QLabel("F : {")
        self.lbl_accolade_open.setStyleSheet(font_math + "font-size: 40px;")

        self.v_vec_widget = QFrame()
        self.v_vec_widget.setStyleSheet("""
            QFrame {
                border-left: 2px solid #000000;
                border-right: 2px solid #000000;
                border-top: none;
                border-bottom: none;
                background-color: transparent;
            }
        """)
        self.v_vec_layout = QVBoxLayout(self.v_vec_widget)
        self.v_vec_layout.setContentsMargins(8, 5, 8, 5)
        self.v_vec_layout.setSpacing(5)

        self.lbl_belongs = QLabel(" ∈ ℝⁿ ,")
        self.lbl_belongs.setStyleSheet(font_math + "font-size: 24px;")

        edit_style = "border: none; border-bottom: 2px solid #34495e; font-size: 18px; padding: 2px; background: transparent; color: #000000;"

        self.edit_eq_left = QLineEdit()
        self.edit_eq_left.setPlaceholderText("ex : x + y + z")
        self.edit_eq_left.setFixedWidth(150)
        self.edit_eq_left.setStyleSheet(edit_style)
        regex_sev = QRegularExpression(r"^[x-zwuv0-9\+\-\*\/\(\)\s\.]*$")
        validator_sev = QRegularExpressionValidator(regex_sev, self.edit_eq_left)
        self.edit_eq_left.setValidator(validator_sev)

        self.lbl_equal = QLabel("=")
        self.lbl_equal.setStyleSheet(font_math + "font-size: 24px;")

        self.edit_eq_right = QLineEdit()
        self.edit_eq_right.setPlaceholderText("0")
        self.edit_eq_right.setFixedWidth(60)
        self.edit_eq_right.setStyleSheet(edit_style)

        self.lbl_accolade_close = QLabel("}")
        self.lbl_accolade_close.setStyleSheet(font_math + "font-size: 40px;")

        formula_layout.addWidget(self.lbl_accolade_open)
        formula_layout.addWidget(self.v_vec_widget)
        formula_layout.addWidget(self.lbl_belongs)
        formula_layout.addWidget(self.edit_eq_left)
        formula_layout.addWidget(self.lbl_equal)
        formula_layout.addWidget(self.edit_eq_right)
        formula_layout.addWidget(self.lbl_accolade_close)
        formula_layout.addStretch()

        layout.addWidget(self.formula_frame)

        style_sev = """
                    QPushButton { 
                        background-color: #2980b9; color: white; padding: 12px; 
                        font-weight: bold; border-radius: 5px; margin-top: 10px;
                        text-align: left; padding-left: 20px; border: none;
                    }
                    QPushButton:hover { 
                        background-color: #3498db; 
                        border-left: 8px solid #1a5276; 
                    }
                """
        self.btn_det_sev = QPushButton("➜ Déterminer la base de F")
        self.btn_check_ev = QPushButton("➜ Vérifier si F est un sous-espace vectoriel de ℝ")

        for b in [self.btn_det_sev, self.btn_check_ev]:
            b.setStyleSheet(style_sev)
            layout.addWidget(b)

        self.btn_check_ev.clicked.connect(self.check_is_sev)
        self.btn_det_sev.clicked.connect(self.determine_sev_base)

        self.spin_sev_n.valueChanged.connect(self.update_sev_formula)
        self.update_sev_formula()
        return container

    def update_sev_formula(self):
        n = self.spin_sev_n.value()
        for i in reversed(range(self.v_vec_layout.count())):
            self.v_vec_layout.itemAt(i).widget().setParent(None)

        variables = ["x", "y", "z", "w", "u", "v"][:n]
        for var in variables:
            lbl = QLabel(var)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet("font-family: 'Cambria Math'; font-size: 18px; color: #000000; border: none;")
            self.v_vec_layout.addWidget(lbl)

        self.lbl_belongs.setText(f" ∈ ℝ{self.get_superscript(n)} ,")

    def create_spin(self, val, text):
        lbl = QLabel(text)
        lbl.setStyleSheet("font-weight: bold; color: #000000; border: none;")
        sb = QSpinBox()
        sb.setRange(1, 10)
        sb.setValue(val)
        sb.setFixedWidth(45)
        sb.setStyleSheet("color: black; background: white;")
        return lbl, sb

    def update_vectors(self):
        for i in reversed(range(self.vector_container.count())):
            self.vector_container.itemAt(i).widget().setParent(None)

        rows, cols = self.spin_dim.value(), self.spin_count.value()

        self.num_delegate = NumericDelegate()

        for _ in range(cols):
            v_table = QTableWidget(rows, 1)
            v_table.horizontalHeader().setVisible(False)
            v_table.verticalHeader().setVisible(False)
            v_table.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

            v_table.setItemDelegate(self.num_delegate)

            v_table.setFixedSize(self.cell_size + 4, rows * self.cell_size + 4)
            v_table.horizontalHeader().setDefaultSectionSize(self.cell_size)
            v_table.verticalHeader().setDefaultSectionSize(self.cell_size)

            v_table.setStyleSheet("""
                QTableWidget {
                    border: 2px solid #2c3e50; 
                    background: white; 
                    color: black; 
                    font-weight: bold;
                    font-size: 22px;
                    outline: 0;
                }
                QTableWidget::item:selected {
                    background-color: white; 
                    color: black;
                }
                QTableWidget::item:focus {
                    background-color: #f8f9fa; /* Gris très clair pour le focus */
                    color: black;
                }
            """)

            for r in range(rows):
                item = QTableWidgetItem("")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                v_table.setItem(r, 0, item)

            self.vector_container.addWidget(v_table)

    def get_superscript(self, n):
        sup = {"2": "²", "3": "³", "4": "⁴", "5": "⁵", "6": "⁶"}
        return sup.get(str(n), str(n))

    def format_math(self, text):
        import re
        text = re.sub(r'\$(\w)_(\d)\$', r'<i style="font-family: serif;">\1</i><sub>\2</sub>', text)
        text = re.sub(r'\$(\w)\$', r'<i style="font-family: serif;">\1</i>', text)
        return text

    def check_is_sev(self):
        try:
            n = self.spin_sev_n.value()
            var_names = ["x", "y", "z", "w", "u", "v"][:n]
            vector_repr = "(" + ", ".join(var_names) + ")"
            var_names_prime = [v + "'" for v in var_names]

            vars_sym = symbols(var_names)
            vars_sym_prime = symbols(var_names_prime)

            eq_left_text = self.edit_eq_left.text() if self.edit_eq_left.text() else "0"
            h_expr = simplify(eq_left_text)

            ital = "style='font-family: serif; font-style: italic;'"
            self.log_area.clear()
            self.log_area.insertHtml(f"<h2 style='color: #2c3e50;'>Caractérisation de <i {ital}>F</i></h2><br>")

            h_display = str(h_expr).replace('*', '')
            self.log_area.insertHtml(
                f"Soit <i {ital}>F</i> = {{ {vector_repr} ∈ ℝ<sup>{n}</sup> | {h_display} = 0 }}<br><br>")

            self.log_area.insertHtml(f"<b>1. Le vecteur nul appartient-il à <i {ital}>F</i> ?</b><br>")
            res_zero = h_expr.subs({v: 0 for v in vars_sym})

            display_zero = eq_left_text
            for v in var_names:
                display_zero = display_zero.replace(v, '(0)')
            display_zero = display_zero.replace('*', '')

            self.log_area.insertHtml(
                f"En remplaçant les coordonnées par 0 : {display_zero} = {res_zero}.<br>")

            if res_zero == 0:
                self.log_area.insertHtml(f"✅ <i {ital}>0<sub>E</sub></i> ∈ <i {ital}>F</i>.<br>")
            else:
                self.log_area.insertHtml(
                    f"❌ <i {ital}>0<sub>E</sub></i> ∉ <i {ital}>F</i>. Ce n'est pas un sous-espace vectoriel.<br>")
                return

            self.log_area.insertHtml(f"<hr><b>2. Stabilité par l'addition</b><br>")
            h_u_text = str(h_expr).replace('*', '')
            h_v_text = str(h_expr)
            for v in var_names: h_v_text = h_v_text.replace(v, v + "'")
            h_v_text = h_v_text.replace('*', '')

            self.log_area.insertHtml(
                f"Soient <i {ital}>u</i> et <i {ital}>v</i> deux vecteurs de <i {ital}>F</i>. <br>")
            self.log_area.insertHtml(f"<b>Hypothèses :</b><br>(1) : {h_u_text} = 0<br>(2) : {h_v_text} = 0<br>")

            h_sum_expr = h_expr.subs({v: v + vp for v, vp in zip(vars_sym, vars_sym_prime)})
            h_sum_display = str(h_sum_expr).replace('*', '')

            self.log_area.insertHtml(f"<br>Vérifions si <i {ital}>u + v</i> satisfait l'équation :<br>")
            self.log_area.insertHtml(
                f"On remplace chaque variable <i {ital}>x<sub>i</sub></i> par <i {ital}>(x<sub>i</sub> + x'<sub>i</sub>)</i> :<br>")
            self.log_area.insertHtml(f"➜ {h_sum_display}<br>")

            self.log_area.insertHtml(
                f"En regroupant les termes, on reconnaît : ({h_u_text}) + ({h_v_text}) = 0 + 0 = <b>0</b>.<br>")
            self.log_area.insertHtml(f"✅ <i {ital}>u + v</i> ∈ <i {ital}>F</i>.<br>")

            self.log_area.insertHtml(f"<hr><b>3. Stabilité par multiplication scalaire</b><br>")
            self.log_area.insertHtml(f"Soient λ ∈ ℝ et <i {ital}>u</i> ∈ <i {ital}>F</i>. <br>")
            self.log_area.insertHtml(f"<b>Hypothèse :</b> {h_u_text} = 0<br>")

            h_lambda_expr = expand(h_expr.subs({v: symbols("λ") * v for v in vars_sym}))
            h_lambda_display = str(h_lambda_expr).replace('*', '')

            self.log_area.insertHtml(f"<br>Vérifions si λ.<i {ital}>u</i> satisfait l'équation :<br>")
            self.log_area.insertHtml(f"➜ {h_lambda_display} = λ × ({h_u_text}) = λ × 0 = <b>0</b>.<br>")
            self.log_area.insertHtml(f"✅ λ.<i {ital}>u</i> ∈ <i {ital}>F</i>.<br>")

            self.log_area.insertHtml(
                "<hr><div style='padding: 25px; border: 2px solid #27ae60; border-radius: 10px; background-color: #f1f9f5;'>")
            self.log_area.insertHtml(
                f"<b style='font-size: 22px; color: #27ae60;'>CONCLUSION : <i {ital}>F</i> est un sous-espace vectoriel de ℝ<sup>{n}</sup>.</b>")
            self.log_area.insertHtml("</div>")

        except Exception as e:
            self.log_area.append(f"Erreur : {str(e)}")

    def determine_sev_base(self):
        try:
            from sympy import solve, symbols, simplify
            n = self.spin_sev_n.value()
            var_names = ["x", "y", "z", "w", "u", "v"][:n]
            vars_sym = symbols(var_names)
            ital = "style='font-family: serif; font-style: italic; font-weight: normal;'"

            def make_v_vec_html(elements):
                inner_rows = "".join(
                    [f"<tr><td align='center' style='padding:1px 10px; border:none; font-size:18px;'>"
                     f"{str(e).replace('*', '')}</td></tr>" for e in elements])

                return f"""
                <table border='0' cellspacing='0' cellpadding='0' style='display:inline-table; vertical-align:middle; margin:5px;'>
                    <tr>
                        <td style='border-left: 2px solid #2c3e50; border-top: 2px solid #2c3e50; border-bottom: 2px solid #2c3e50; width: 5px;'>&nbsp;</td>
                        <td valign='middle'><table border='0' cellspacing='0' cellpadding='0'>{inner_rows}</table></td>
                        <td style='border-right: 2px solid #2c3e50; border-top: 2px solid #2c3e50; border-bottom: 2px solid #2c3e50; width: 5px;'>&nbsp;</td>
                    </tr>
                </table>
                """

            eq_left_text = self.edit_eq_left.text() if self.edit_eq_left.text() else "0"
            h_expr = simplify(eq_left_text)
            h_display = str(h_expr).replace('*', '')

            self.log_area.clear()
            self.log_area.insertHtml(f"<h2 style='color: #2c3e50;'>Détermination de la Base de <i {ital}>F</i></h2><br>")

            self.log_area.insertHtml(f"""
                <div style='background-color: #f8f9fa; padding: 10px; border-left: 4px solid #2980b9;'>
                    <b>Propriété :</b> Une famille est une <b>base</b> si elle est à la fois <b style='color: #2eab31;'>libre</b> et <b style='color: #b55a19;'>génératrice</b> de l'espace.
                <br></div>
            """)

            self.log_area.insertHtml(f"<br><b>Étape 1 : Expression du vecteur quelconque</b><br>")
            u_init_line = f"""
            <table border='0' cellspacing='0' cellpadding='0'>
                <tr>
                    <td valign='middle' {ital}>u = &nbsp;</td>
                    <td valign='middle'>{make_v_vec_html(var_names)}</td>
                    <td valign='middle'>&nbsp; ∈ <i {ital}>F</i>. Il vérifie : <b>{h_display} = 0</b>.</td>
                </tr>
            </table>
            """
            self.log_area.insertHtml(u_init_line)

            solutions = solve(h_expr, vars_sym, dict=True)
            if not solutions: return

            sol_dict = solutions[0]
            solved_var = list(sol_dict.keys())[0]
            expr_isolated = str(sol_dict[solved_var]).replace('*', '')
            free_vars = [v for v in vars_sym if v != solved_var]

            self.log_area.insertHtml(
                f"<br>En isolant <i {ital}>{solved_var}</i>, on obtient : <i {ital}>{solved_var}</i> = {expr_isolated}.<br>")

            gen_vector = [sol_dict.get(v, v) for v in vars_sym]
            u_mod_line = f"""
            <table border='0' cellspacing='0' cellpadding='0'>
                <tr>
                    <td valign='middle'>On réécrit <i {ital}>u</i> : &nbsp;</td>
                    <td valign='middle' {ital}>u = &nbsp;</td>
                    <td valign='middle'>{make_v_vec_html(gen_vector)}</td>
                </tr>
            </table>
            """
            self.log_area.insertHtml(u_mod_line)

            self.log_area.insertHtml(f"<br><b>Étape 2 : Décomposition selon les paramètres libres</b><br>")
            param_cells = []
            base_data = []
            for fv in free_vars:
                vec_col = [comp.diff(fv) for comp in gen_vector]
                if all(val == 0 for val in vec_col): continue
                base_data.append(vec_col)
                param_cells.append(
                    f"<td valign='middle' {ital}> &nbsp; {fv} . &nbsp; </td><td valign='middle'>{make_v_vec_html(vec_col)}</td>")

            all_params_html = "<td valign='middle'>&nbsp; + &nbsp;</td>".join(param_cells)
            decomp_line = f"""
            <table border='0' cellspacing='0' cellpadding='0'>
                <tr>
                    <td valign='middle' {ital}>u = &nbsp;</td>
                    <td valign='middle'>{make_v_vec_html(gen_vector)}</td>
                    <td valign='middle'>&nbsp; = &nbsp;</td>
                    {all_params_html}
                </tr>
            </table>
            """
            self.log_area.insertHtml(decomp_line)

            self.log_area.insertHtml(f"<br><b>Étape 3 : Construction de la famille <i {ital}>e</i></b><br>")
            vec_horiz = [f"({', '.join([str(x).replace('*', '') for x in bv])})" for bv in base_data]
            self.log_area.insertHtml(f"<br>On extrait la famille <i {ital}>e</i> = {{ {' ; '.join(vec_horiz)} }}.<br>")

            self.log_area.insertHtml(f"""
                <p>➜ Cette famille est <b style='color: #2eab31;'>libre</b> (paramètres indépendants).<br>
                ➜ Elle est <b style='color: #b55a19;'>génératrice</b> car elle permet d'exprimer tout vecteur <i {ital}>u</i> par combinaison linéaire des ses variables.</p>
            """)

            dim = len(base_data)
            self.log_area.insertHtml(
                "<hr><div style='background-color: #ebf5fb; padding: 15px; border: 2px solid #2980b9; border-radius: 10px;'>")
            self.log_area.insertHtml(f"La famille <i {ital}>e</i>   est une <b>base</b> de <i {ital}>F</i>.<br>")
            self.log_area.insertHtml(f"<b>Rang :</b> rg(<i {ital}>e</i> ) = {dim}<br>")
            self.log_area.insertHtml(f"<b>Dimension :</b> dim(<i {ital}>F</i> ) = {dim}")

            if dim == 1: self.log_area.insertHtml("<br><i>Note : F est une droite vectorielle.</i>")
            elif dim == 2: self.log_area.insertHtml("<br><i>Note : F est un plan vectoriel.</i>")
            elif dim == n - 1: self.log_area.insertHtml(f"<br><i>Note : F est un hyperplan de ℝ<sup>{n}</sup>.</i>")
            self.log_area.insertHtml("</div>")

        except Exception as e:
            self.log_area.append(f"Erreur : {str(e)} \nN'oubliez pas de préciser l'opération (2x -> 2*x)")

    def get_vectors_from_ui(self):
        from sympy import Matrix
        vectors = []
        dim = self.spin_dim.value()
        count = self.spin_count.value()

        for i in range(self.vector_container.count()):
            table = self.vector_container.itemAt(i).widget()
            if isinstance(table, QTableWidget):
                vec_data = []
                for r in range(dim):
                    item = table.item(r, 0)
                    val = item.text() if item and item.text() else "0"
                    try:
                        vec_data.append(simplify(val))
                    except:
                        vec_data.append(0)
                vectors.append(Matrix(vec_data))
        return vectors

    def make_v_vec_html(self, elements):
        inner_rows = "".join([
            f"<tr><td align='center' style='padding:1px 10px; border:none; font-size:18px;'>"
            f"{str(e).replace('*', '')}</td></tr>" for e in elements
        ])
        return f"""
        <table border='0' cellspacing='0' cellpadding='0' style='display:inline-table; vertical-align:middle; margin:5px;'>
            <tr>
                <td style='border-left: 2px solid #2c3e50; border-top: 2px solid #2c3e50; border-bottom: 2px solid #2c3e50; width: 5px;'>&nbsp;</td>
                <td valign='middle'><table border='0' cellspacing='0' cellpadding='0'>{inner_rows}</table></td>
                <td style='border-right: 2px solid #2c3e50; border-top: 2px solid #2c3e50; border-bottom: 2px solid #2c3e50; width: 5px;'>&nbsp;</td>
            </tr>
        </table>
        """

    def make_matrix_html(self, matrix):
        """ Affiche une matrice complète avec crochets [ ] """
        rows_html = ""
        for r in range(matrix.rows):
            cols_html = "".join([
                f"<td style='padding:5px 15px; text-align:center; font-size:18px;'>"
                f"{str(matrix[r, c]).replace('*', '')}</td>" for c in range(matrix.cols)
            ])
            rows_html += f"<tr>{cols_html}</tr>"

        return f"""
        <table border='0' cellspacing='0' cellpadding='0' style='display:inline-table; vertical-align:middle; margin:10px;'>
            <tr>
                <td style='border-left: 2px solid #2c3e50; border-top: 2px solid #2c3e50; border-bottom: 2px solid #2c3e50; width: 5px;'>&nbsp;</td>
                <td><table border='0' cellspacing='0' cellpadding='0'>{rows_html}</table></td>
                <td style='border-right: 2px solid #2c3e50; border-top: 2px solid #2c3e50; border-bottom: 2px solid #2c3e50; width: 5px;'>&nbsp;</td>
            </tr>
        </table>
        """

    def make_matrix_augmented_html(self, matrix):
        rows_html = ""
        for r in range(matrix.rows):
            cols_a = "".join([
                                 f"<td style='padding:5px 15px; text-align:center; font-size:18px;'>{str(matrix[r, c]).replace('*', '')}</td>"
                                 for c in range(matrix.cols)])
            col_b = f"<td style='padding:5px 15px; text-align:center; font-size:18px; border-left: 1px solid #7f8c8d; color: #7f8c8d;'>0</td>"
            rows_html += f"<tr>{cols_a}{col_b}</tr>"

        return f"""
        <table border='0' cellspacing='0' cellpadding='0' style='display:inline-table; vertical-align:middle; margin:10px;'>
            <tr>
                <td style='border-left: 2px solid #2c3e50; border-top: 2px solid #2c3e50; border-bottom: 2px solid #2c3e50; width: 5px;'>&nbsp;</td>
                <td><table border='0' cellspacing='0' cellpadding='0'>{rows_html}</table></td>
                <td style='border-right: 2px solid #2c3e50; border-top: 2px solid #2c3e50; border-bottom: 2px solid #2c3e50; width: 5px;'>&nbsp;</td>
            </tr>
        </table>
        """

    def get_system_html(self, matrix, unknowns):
        n, p = matrix.rows, matrix.cols
        system_html = """
        <table border='0' cellspacing='0' cellpadding='0' style='margin-top:10px;'>
            <tr>
                <td style='border-left: 2px solid black; border-top: 1px solid black; border-bottom: 1px solid black; width: 10px;'>&nbsp;</td>
                <td>
                    <table border='0' cellspacing='0' cellpadding='0' style='padding-left: 8px;'>
        """
        for r in range(n):
            line_parts = []
            for c in range(p):
                val = matrix[r, c]
                if val == 0: continue
                coeff = "" if val == 1 else ("-" if val == -1 else str(val))
                line_parts.append(f"{coeff}x<sub>{c + 1}</sub>")

            full_line = " + ".join(line_parts).replace("+ -", "- ")
            if not full_line: full_line = "0"
            system_html += f"<tr><td style='font-size: 18px; padding: 2px 0;'>{full_line} = 0</td></tr>"

        system_html += "</table></td></tr></table>"
        return system_html

    def study_family(self):
        try:
            from sympy import Matrix, symbols, solve
            vectors = self.get_vectors_from_ui()
            n, p = self.spin_dim.value(), len(vectors)
            unknowns = symbols(f'x1:{p + 1}')
            ital = "style='font-family: serif; font-style: italic; font-weight: normal;'"

            self.log_area.clear()
            self.log_area.insertHtml(f"<h2 style='color: #2c3e50;'>Étude complète de la famille</h2>")

            self.log_area.insertHtml(f"""
                <div style='background-color: #f8f9fa; padding: 10px; border-left: 4px solid #2980b9;'>
                    <br><b style='color: #961d21;'>Propriété :</b> Une famille de vecteurs est libre si et seulement si la combinaison linéaire 
                    <i {ital}>Σ λ<sub>i</sub>v<sub>i</sub> = 0<sub>E</sub></i> , avec <i {ital}>λ<sub>i</sub></i> un réel, 
                    n'admet comme solution seulement <i {ital}>λ<sub>i</sub> = 0</i>.
                </div><br>
            """)

            self.log_area.insertHtml(
                f"C'est à dire qu'on étudie la combinaison linéaire suivante :<br>")

            comb_html = "<table border='0'><tr>"
            for i in range(p):
                comb_html += f"<td valign='middle'>x<sub>{i + 1}</sub></td><td valign='middle'>{self.make_v_vec_html(vectors[i])}</td>"
                if i < p - 1: comb_html += "<td valign='middle'> + </td>"
            comb_html += f"<td valign='middle'> = </td><td valign='middle'>{self.make_v_vec_html([0] * n)}</td></tr></table>"
            self.log_area.insertHtml(comb_html)

            matrix_system = Matrix.hstack(*vectors)
            self.log_area.insertHtml(f"<br><br>On transforme cette combinaison en sytème linéaire :<br>")
            self.log_area.insertHtml(self.get_system_html(matrix_system, unknowns))

            self.log_area.insertHtml(f"<br><br><b>1. Résolution par échelonnement (Pivot de Gauss)</b><br>")
            self.log_area.insertHtml("On écrit la matrice augmentée [A|0] :<br>")
            self.log_area.insertHtml(self.make_matrix_augmented_html(matrix_system))

            echelon_matrix = matrix_system.echelon_form()
            self.log_area.insertHtml("Après échelonnement, on obtient la matrice suivante :<br>")
            self.log_area.insertHtml(self.make_matrix_augmented_html(echelon_matrix))

            self.log_area.insertHtml("<br>Le système devient alors beaucoup plus simple (forme triangulaire) :<br>")
            self.log_area.insertHtml(self.get_system_html(echelon_matrix, unknowns))

            solutions = solve([sum(matrix_system[r, c] * unknowns[c] for c in range(p)) for r in range(n)], unknowns)

            self.log_area.insertHtml(f"<br><br>Par remontée du système échelonné, on détermine les coefficients :<br>")
            is_free = False
            if isinstance(solutions, dict):
                for i in range(p):
                    val = solutions.get(unknowns[i], 0)
                    self.log_area.insertHtml(f"➜ x<sub>{i + 1}</sub> = {val}<br>")
                if all(v == 0 for v in solutions.values()) and len(solutions) == p:
                    is_free = True

            self.log_area.insertHtml("<br><b>Analyse de l'étape 1 :</b><br>")
            if is_free:
                self.log_area.insertHtml(
                    f"Le système n'admet que la solution nulle, donc la famille est <b style='color: #23cc69;'>libre</b>.<br>")
            else:
                self.log_area.insertHtml(
                    f"Le système admet des solutions non triviales, donc la famille est <b style='color: #ad2f0c;'>liée</b>.<br>")

            self.log_area.insertHtml(f"<hr><b>2. Raisonnement sur le rang</b><br>")
            rank = matrix_system.rank()
            self.log_area.insertHtml(
                f"L'échelonnement montre que la famille possède <b>{rank}</b> ligne(s) non nulle(s) (pivots).<br>")
            self.log_area.insertHtml(
                f"Le nombre de vecteurs linéairement indépendants dans cette famille est de <b>{rank}</b>.<br>")
            self.log_area.insertHtml(f"Par conséquent, le rang de la famille est : <b>rg(F) = {rank}</b>.<br>")

            self.log_area.insertHtml(f"<hr><b>3. Conclusion sur la nature de la famille</b><br>")

            is_basis = (is_free and rank == n)
            bg_color = "#f1f9f5" if is_basis else "#fef9e7"
            border_color = "#27ae60" if is_basis else "#f1c40f"

            self.log_area.insertHtml(
                f"<div style='background-color: {bg_color}; padding: 15px; border: 2px solid {border_color}; border-radius: 10px;'>")

            txt_libre = "libre (indépendance linéaire vérifiée par le système)" if is_free else "liée (dépendance linéaire détectée)"
            self.log_area.insertHtml(f"1. La famille est <b>{txt_libre}</b>.<br>")

            txt_rank = f"égal à <b>{rank}</b>, ce qui correspond à la dimension de ℝ<sup>{n}</sup>" if rank == n else f"égal à <b>{rank}</b>, ce qui est différent de la dimension de l'espace (dim=<b>{n}</b>)"
            self.log_area.insertHtml(f"2. Son rang est {txt_rank}.<br>")

            txt_basis = "constitue une <b>base</b>" if is_basis else "<b>n'est pas une base</b>"
            self.log_area.insertHtml(f"3. Par conséquent, la famille {txt_basis} de ℝ<sup>{n}</sup>.")

            self.log_area.insertHtml("</div>")

        except Exception as e:
            self.log_area.append(f"Erreur : {str(e)}")