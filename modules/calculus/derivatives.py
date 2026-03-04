import numpy as np
import pyqtgraph as pg
import sympy as sp
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFrame,
                               QLabel, QLineEdit, QPushButton, QSlider,
                               QTextEdit, QTableWidget, QTableWidgetItem, QHeaderView)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont


class DerivativesPage(QWidget):
    def __init__(self):
        super().__init__()
        self.x_sym = sp.Symbol('x')
        self.init_ui()

    def init_ui(self):
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        self.main_layout.setSpacing(20)

        self.setStyleSheet("""
            QWidget { background-color: #ffffff; color: #2c3e50; font-family: 'Segoe UI', sans-serif; }
            QLabel#Title { font-size: 18px; font-weight: bold; color: #2c3e50; border-bottom: 2px solid #3498db; margin-bottom: 5px; }
            QLineEdit { border: 2px solid #bdc3c7; border-radius: 5px; padding: 10px; font-size: 16px; }
            QTextEdit { border: 1px solid #dee2e6; border-radius: 8px; background: #fdfdfd; font-size: 14px; }
            QFrame#Panel { background-color: #f8f9fa; border-radius: 12px; border: 1px solid #dee2e6; }
            QTableWidget { background-color: white; border: 2px solid black; gridline-color: transparent; }
            QPushButton#ActionBtn { background-color: #3498db; color: white; font-weight: bold; padding: 12px; border-radius: 6px; border: none; font-size: 13px;}
            QPushButton#ActionBtn:hover { background-color: #2980b9; }
            QPushButton#ConcavityBtn { background-color: #9b59b6; color: white; font-weight: bold; padding: 12px; border-radius: 6px; border: none; font-size: 13px;}
            QPushButton#ConcavityBtn:hover { background-color: #8e44ad; }
        """)

        self.left_panel = QFrame()
        self.left_panel.setFixedWidth(450)
        self.left_panel.setObjectName("Panel")
        self.left_layout = QVBoxLayout(self.left_panel)

        self.left_layout.addWidget(QLabel("DÉRIVÉES FORMULES", objectName="Title"))
        self.memo_box = QTextEdit()
        self.memo_box.setReadOnly(True)
        self.memo_box.setHtml(self.get_full_memo_html())
        self.memo_box.setFixedHeight(300)
        self.left_layout.addWidget(self.memo_box)

        self.left_layout.addWidget(QLabel("FONCTION f(x)", objectName="Title"))
        self.input_func = QLineEdit()
        self.input_func.setPlaceholderText("Ex: e(x) + ln(x) ou (x^2+1)/(x-1)")
        self.left_layout.addWidget(self.input_func)

        self.analysis_btns_layout = QHBoxLayout()

        self.btn_derive = QPushButton("ANALYSER LA DÉRIVÉE\n(croissance/décroissance)", objectName="ActionBtn")
        self.btn_derive.clicked.connect(self.calculate_all)

        self.btn_concavity = QPushButton("ANALYSE DÉRIVÉE SECONDE\n(concavité/convexité)", objectName="ConcavityBtn")
        self.btn_concavity.clicked.connect(self.calculate_concavity)  # Méthode à définir

        self.analysis_btns_layout.addWidget(self.btn_derive)
        self.analysis_btns_layout.addWidget(self.btn_concavity)
        self.left_layout.addLayout(self.analysis_btns_layout)

        self.explanation_box = QTextEdit()
        self.explanation_box.setReadOnly(True)
        self.left_layout.addWidget(self.explanation_box)

        self.right_container = QFrame()
        self.right_layout = QVBoxLayout(self.right_container)

        self.right_layout.addWidget(QLabel("TABLEAU DE VARIATIONS", objectName="Title"))
        self.variation_table = QTableWidget(4, 1)
        self.variation_table.setFixedHeight(240)
        self.variation_table.horizontalHeader().hide()
        self.variation_table.verticalHeader().hide()
        self.variation_table.setShowGrid(False)
        self.variation_table.setStyleSheet(
            "QTableWidget::item { border-bottom: 1px solid black; background-color: white; }")
        self.right_layout.addWidget(self.variation_table)

        self.graph_frame = QFrame()
        self.graph_frame.setObjectName("Panel")
        self.graph_layout = QVBoxLayout(self.graph_frame)

        self.tangent_info = QLabel("Tangente de f au point a : y = f'(a)(x - a) + f(a)  ➜  ...")
        self.tangent_info.setStyleSheet(
            "color: #d35400; font-weight: bold; background: #fff3e0; padding: 12px; border-radius: 5px; border: 1px solid #ffcc80; font-size: 14px;")
        self.graph_layout.addWidget(self.tangent_info)

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')
        self.plot_widget.setMouseEnabled(x=True, y=True)
        self.graph_layout.addWidget(self.plot_widget)

        self.slider_a = QSlider(Qt.Orientation.Horizontal)
        self.slider_a.setRange(-100, 100)
        self.slider_a.setValue(20)
        self.slider_a.valueChanged.connect(self.update_tangent)
        self.graph_layout.addWidget(self.slider_a)

        self.right_layout.addWidget(self.graph_frame)
        self.main_layout.addWidget(self.left_panel)
        self.main_layout.addWidget(self.right_container, 1)

    def calculate_concavity(self):
        try:
            raw = self.input_func.text().replace(',', '.')
            raw = raw.replace('e(', 'exp(').replace('e^', 'exp(').replace('ln', 'log')

            self.f = sp.sympify(raw)
            self.df = sp.diff(self.f, self.x_sym)
            self.d2f = sp.diff(self.df, self.x_sym)

            msg = "<div style='font-size: 15px; font-family: Segoe UI, sans-serif;'>"
            msg += "<h2 style='color: #9b59b6; border-bottom: 2px solid #9b59b6; padding-bottom: 5px;'>Étude de la Concavité (Dérivée Seconde)</h2>"

            msg += f"<b>Fonction étudiée :</b> <span style='color: #2980b9;'>f(x) = {self.clean_math_display(self.f)}</span><br>"

            msg += "<div style='background-color: #f4f6f7; padding: 10px; border-left: 5px solid #3498db; margin-bottom: 15px;'>"
            msg += "<b style='color: #3498db;'>ÉTAPE A : Détermination de la dérivée première f'(x)</b><br>"

            msg += self._analyze_structure_logic(self.f, self.df, "f")

            msg += f"<br><b>Résultat de la première dérivation :</b>"
            msg += f"<div style='color: #3498db; font-size:18px; background-color: #e6f5ff; font-size:16px; font-weight:bold;'>f'(x) = {self.clean_math_display(self.df)}</div>"
            msg += "</div>"
            msg += "<br>"
            msg += "<div style='background-color: #f4f6f7; padding: 10px; border-left: 5px solid #9b59b6; margin-bottom: 15px;'>"
            msg += "<b style='color: #9b59b6;'>ÉTAPE B : Détermination de la dérivée seconde f''(x)</b><br>"
            msg += f"On dérive la fonction <i style='color:#3498db;'>f'(x)</i> pour obtenir la dérivée seconde.<br><br>"

            msg += self._analyze_structure_logic(self.df, self.d2f, "f'")

            msg += f"<br><b>Résultat de la seconde dérivation :</b>"
            msg += f"<div style='color:#9b59b6; font-size:18px; font-weight:bold; background:#f4ebf7; padding:10px; border-radius:5px; border: 1px solid #9b59b6; margin-top:5px;'>"
            msg += f"f''(x) = {self.clean_math_display(self.d2f)}</div>"
            msg += "</div>"

            msg += "<br><b>Interprétation :</b> Le signe de f''(x) déterminera si la courbe est concave ou convexe."
            msg += "</div>"

            self.explanation_box.setHtml(msg)
            self.update_concavity_table()
            self.update_graph(first_load=True)

        except Exception as e:
            self.explanation_box.setText(f"Erreur d'analyse de concavité : {e}")

    def _analyze_structure_logic(self, function_to_derive, result_derivative, name):
        detail = ""
        f_to_d = function_to_derive
        n = name

        if f_to_d.is_Add:
            detail += f"<b>1. Structure identifiée :</b> <span style='color: #e67e22;'>Somme de fonctions</span><br>"
            detail += f"• Règle : <b>(u + v)' = u' + v'</b><br>"
            detail += "• Calcul des dérivées terme à terme :<br>"
            for term in f_to_d.args:
                detail += f"&nbsp;&nbsp;&nbsp;&nbsp;➜ ({self.clean_math_display(term)})' = <span style='color: #27ae60;'>{self.clean_math_display(sp.diff(term, self.x_sym))}</span><br>"

        elif f_to_d.is_Pow and f_to_d.exp.is_negative or (
                f_to_d.is_Mul and any(isinstance(arg, sp.Pow) and arg.exp.is_negative for arg in f_to_d.args)):
            num, den = sp.fraction(f_to_d)
            if den != 1:
                u, v = num, den
                up, vp = sp.diff(u), sp.diff(v)
                detail += f"<b>1. Structure identifiée :</b> <span style='color: #e67e22;'>Quotient (u / v)</span><br>"
                detail += f"• On pose : <b>u = {self.clean_math_display(u)}</b> et <b>v = {self.clean_math_display(v)}</b><br>"
                detail += f"• On calcule : <b>u' = {self.clean_math_display(up)}</b> et <b>v' = {self.clean_math_display(vp)}</b><br>"
                detail += f"• Règle : <b>(u / v)' = (u'v - uv') / v²</b><br>"

        elif f_to_d.is_Mul:
            args = f_to_d.args
            if any(arg.is_Number for arg in args):
                k = [a for a in args if a.is_Number][0]
                u = sp.Mul(*[a for a in args if not a.is_Number])
                detail += f"<b>1. Structure identifiée :</b> <span style='color: #e67e22;'>Produit par une constante (ku)</span><br>"
                detail += f"• Règle : <b>(ku)' = ku'</b> avec k = {k}<br>"
                detail += f"• On dérive u = {self.clean_math_display(u)} → <b>u' = {self.clean_math_display(sp.diff(u))}</b><br>"
            else:
                u, v = args[0], sp.Mul(*args[1:])
                up, vp = sp.diff(u), sp.diff(v)
                detail += f"<b>1. Structure identifiée :</b> <span style='color: #e67e22;'>Produit (u × v)</span><br>"
                detail += f"• u = {self.clean_math_display(u)} ; v = {self.clean_math_display(v)}<br>"
                detail += f"• u' = {self.clean_math_display(up)} ; v' = {self.clean_math_display(vp)}<br>"
                detail += f"• Règle : <b>(u × v)' = u'v + uv'</b><br>"

        elif any(isinstance(f_to_d, cls) for cls in [sp.exp, sp.log, sp.sin, sp.cos, sp.tan]) or f_to_d.is_Pow:
            if f_to_d.is_Pow:
                u, n_exp = f_to_d.base, f_to_d.exp
                detail += f"<b>1. Structure identifiée :</b> <span style='color: #e67e22;'>Puissance (u<sup>n</sup>)</span><br>"
                detail += f"• Règle : <b>(u<sup>n</sup>)' = nu'u<sup>n-1</sup></b> avec u = {self.clean_math_display(u)} et n = {n_exp}<br>"
            else:
                u = f_to_d.args[0]
                up = sp.diff(u)
                func_name = f_to_d.func.__name__
                rules = {
                    'exp': ("e<sup>u</sup>", "u'e<sup>u</sup>"),
                    'log': ("ln(u)", "u'/u"),
                    'sin': ("sin(u)", "u'cos(u)"),
                    'cos': ("cos(u)", "-u'sin(u)")
                }
                rule = rules.get(func_name, ("f(u)", "u'f'(u)"))
                detail += f"<b>1. Structure identifiée :</b> <span style='color: #e67e22;'>Composée {rule[0]}</span><br>"
                detail += f"• Règle : <b>({rule[0]})' = {rule[1]}</b> avec u = {self.clean_math_display(u)} et u' = {self.clean_math_display(up)}<br>"

        else:
            detail += f"<b>1. Structure identifiée :</b> <span style='color: #e67e22;'>Fonction usuelle</span><br>"
            detail += "• Application directe d'une formule de base du tableau de référence.<br>"

        return detail

    def format_math_light(self, expr):
        return str(expr).replace("**", "^").replace("*", "&nbsp;").replace("exp", "e").replace("log", "ln")

    def update_concavity_table(self):
        try:
            # 1. Recherche des points critiques (f''(x)=0) et singularités (valeurs interdites)
            roots = [float(r.evalf()) for r in sp.solve(self.d2f, self.x_sym) if r.is_real]
            singularities = []
            _, den = sp.fraction(self.f)
            if den != 1:
                singularities = [float(s.evalf()) for s in sp.solve(den, self.x_sym) if s.is_real]

            # On fusionne et on trie les points pour créer les colonnes
            all_pts = sorted(list(set(roots + singularities)))
        except:
            all_pts = []

        # Construction des points d'échantillonnage pour le tableau
        pts = [("-∞", None, False)]
        for p in all_pts:
            pts.append(("interval", p - 0.1, False))  # Point pour tester le signe dans l'intervalle
            is_sing = any(abs(p - s) < 1e-5 for s in singularities)
            pts.append((f"{p:.1f}", p, is_sing))
        pts.append(("interval", (all_pts[-1] + 1 if all_pts else 0), False))
        pts.append(("+∞", None, False))

        self.variation_table.setColumnCount(len(pts) + 1)
        self.variation_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # On fixe les hauteurs de ligne pour que la 4ème soit bien visible
        self.variation_table.setRowHeight(0, 35)  # Ligne x
        self.variation_table.setRowHeight(1, 35)  # Ligne f''(x)
        self.variation_table.setRowHeight(2, 80)  # Ligne f'(x) (flèches)
        self.variation_table.setRowHeight(3, 110)  # Ligne f(x) (concavité)

        def set_item(r, c, text, bold=False, arrow=False, color="#000000"):
            txt = (text + "  │") if c == 0 else text
            item = QTableWidgetItem(txt)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setForeground(QColor(color))
            font = QFont("Segoe UI", 10)  # Respect de ta police
            if bold: font.setBold(True)
            if arrow: font.setPointSize(30); font.setBold(True)
            item.setFont(font)
            if c == 0: item.setBackground(QColor("#f2f2f2"))
            self.variation_table.setItem(r, c, item)

        # En-têtes de lignes
        set_item(0, 0, "x", True)
        set_item(1, 0, "f''(x)", True)
        set_item(2, 0, "f'(x)", True)
        set_item(3, 0, "f(x)", True)

        for i, (label, val, is_sing) in enumerate(pts):
            col = i + 1
            if label == "interval":
                try:
                    val_d2f = self.d2f.subs(self.x_sym, val)
                    sign = "+" if val_d2f > 0 else "-"
                    set_item(1, col, sign, bold=True)

                    set_item(2, col, "↗" if sign == "+" else "↘", arrow=True, color="#3498db")

                    if sign == "+":
                        set_item(3, col, "CONVEXE\n(∪)", color="#27ae60", bold=True)
                    else:
                        set_item(3, col, "CONCAVE\n(∩)", color="#e67e22", bold=True)
                except:
                    set_item(1, col, "?")
            else:
                set_item(0, col, label, bold=True)
                if is_sing:
                    for row in range(1, 4):
                        set_item(row, col, "||", color="red", bold=True)
                elif label not in ["-∞", "+∞"]:
                    set_item(1, col, "0")  # f''(x) s'annule
                    set_item(2, col, "|")
                    set_item(3, col, "Point\nd'inflexion", color="#9b59b6", bold=True)

    def get_full_memo_html(self):
        return """
        <table width="100%" border="1" style="border-collapse: collapse; text-align: center; background-color: white; font-size: 14px;">
            <tr style="background-color: #2c3e50; color: white;">
                <th width="50%"><b>Fonction f(x)</b></th>
                <th width="50%"><b>Dérivée f'(x)</b></th>
            </tr>
            <tr style="background-color: #f2f2f2;"><td colspan="2"><b>Usuelles et Puissances</b></td></tr>
            <tr><td>k (constante)</td><td style="color: #e67e22; font-weight: bold;">0</td></tr>
            <tr><td>x</td><td style="color: #e67e22; font-weight: bold;">1</td></tr>
            <tr><td>kx</td><td style="color: #e67e22; font-weight: bold;">k</td></tr>
            <tr><td>x<sup>n</sup></td><td style="color: #e67e22; font-weight: bold;">nx<sup>n-1</sup></td></tr>
            <tr><td>1/x</td><td style="color: #e67e22; font-weight: bold;">-1/x<sup>2</sup></td></tr>
            <tr><td>1/x<sup>n</sup></td><td style="color: #e67e22; font-weight: bold;">-n/x<sup>n+1</sup></td></tr>
            <tr><td>√x</td><td style="color: #e67e22; font-weight: bold;">1/(2√x)</td></tr>

            <tr style="background-color: #f2f2f2;"><td colspan="2"><b>Exponentielles / Logarithmes</b></td></tr>
            <tr><td>e<sup>x</sup></td><td style="color: #e67e22; font-weight: bold;">e<sup>x</sup></td></tr>
            <tr><td>e<sup>u(x)</sup></td><td style="color: #e67e22; font-weight: bold;">u'(x)e<sup>u(x)</sup></td></tr>
            <tr><td>ln(x)</td><td style="color: #e67e22; font-weight: bold;">1/x</td></tr>
            <tr><td>ln(u(x))</td><td style="color: #e67e22; font-weight: bold;">u'(x)/u(x)</td></tr>

            <tr style="background-color: #f2f2f2;"><td colspan="2"><b>Trigonométrie</b></td></tr>
            <tr><td>sin(x)</td><td style="color: #e67e22; font-weight: bold;">cos(x)</td></tr>
            <tr><td>cos(x)</td><td style="color: #e67e22; font-weight: bold;">-sin(x)</td></tr>
            <tr><td>tan(x)</td><td style="color: #e67e22; font-weight: bold;">1 + tan<sup>2</sup>(x)</td></tr>

            <tr style="background-color: #f2f2f2;"><td colspan="2"><b>Opérations (u, v fonctions)</b></td></tr>
            <tr><td>ku</td><td style="color: #e67e22; font-weight: bold;">ku'</td></tr>
            <tr><td>u + v</td><td style="color: #e67e22; font-weight: bold;">u' + v'</td></tr>
            <tr><td>u × v</td><td style="color: #e67e22; font-weight: bold;">u'v + uv'</td></tr>
            <tr><td>1/u</td><td style="color: #e67e22; font-weight: bold;">-u'/u<sup>2</sup></td></tr>
            <tr><td>u / v</td><td style="color: #e67e22; font-weight: bold;">(u'v - uv') / v<sup>2</sup></td></tr>
            <tr><td>u<sup>n</sup></td><td style="color: #e67e22; font-weight: bold;">nu'u<sup>n-1</sup></td></tr>
            <tr><td>√u</td><td style="color: #e67e22; font-weight: bold;">u' / (2√u)</td></tr>
            <tr><td>f(g(x))</td><td style="color: #e67e22; font-weight: bold;">g'(x) × f'(g(x))</td></tr>
        </table>
        """

    def clean_math_display(self, expr):
        return str(expr).replace("**", "^").replace("*", "").replace("exp", "e").replace("log", "ln")

    def calculate_all(self):
        try:
            # 1. Prétraitement de l'entrée
            raw = self.input_func.text().replace(',', '.')
            raw = raw.replace('e(', 'exp(').replace('e^', 'exp(')
            raw = raw.replace('ln', 'log')

            self.f = sp.sympify(raw)
            self.df = sp.diff(self.f, self.x_sym)

            msg = "<h2 style='color: #9b59b6; border-bottom: 2px solid #9b59b6; padding-bottom: 5px;'>Étude de la Variation</h2>"
            msg += f"<div style='font-size: 15px;'><b>Analyse de la fonction :</b> <span style='color: #2980b9;'>f(x) = {self.clean_math_display(self.f)}</span><br><br>"

            # 2. Détection de la structure et détail des étapes
            # --- CAS : SOMME u + v + ... ---
            if self.f.is_Add:
                msg += "<b>1. Structure identifiée :</b> <span style='color: #e67e22;'>Somme de fonctions</span><br>"
                msg += "• Règle : La dérivée d'une somme est la somme des dérivées : <i>(u + v)' = u' + v'</i><br>"
                msg += "• On dérive chaque terme séparément :<br>"
                for term in self.f.args:
                    msg += f"&nbsp;&nbsp;&nbsp;&nbsp;➜ Dérivée de {self.clean_math_display(term)} = <span style='color: #27ae60;'>{self.clean_math_display(sp.diff(term, self.x_sym))}</span><br>"

            # --- CAS : QUOTIENT u / v ---
            elif self.f.is_Pow and self.f.exp.is_negative or (
                    self.f.is_Mul and any(isinstance(arg, sp.Pow) and arg.exp.is_negative for arg in self.f.args)):
                # Note: Sympy représente souvent u/v comme u * v^-1
                num, den = sp.fraction(self.f)
                if den != 1:
                    u, v = num, den
                    up, vp = sp.diff(u), sp.diff(v)
                    msg += "<b>1. Structure identifiée :</b> <span style='color: #e67e22;'>Quotient (u / v)</span><br>"
                    msg += f"• On pose : <b>u(x) = {self.clean_math_display(u)}</b> et <b>v(x) = {self.clean_math_display(v)}</b><br>"
                    msg += f"• On calcule les dérivées : <b>u'(x) = {self.clean_math_display(up)}</b> et <b>v'(x) = {self.clean_math_display(vp)}</b><br><br>"
                    msg += "<b>2. Application de la formule :</b><br>"
                    msg += "<div style='background: #fdf2e9; padding: 5px;'><i>f'(x) = (u'v - uv') / v²</i></div><br>"
                    msg += f"• f'(x) = [ ({self.clean_math_display(up)})({self.clean_math_display(v)}) - ({self.clean_math_display(u)})({self.clean_math_display(vp)}) ] / ({self.clean_math_display(v)})²<br>"

            # --- CAS : PRODUIT u * v ---
            elif self.f.is_Mul:
                # Séparation constante et fonction (ex: 5x^2 -> 5 * x^2)
                args = self.f.args
                if any(arg.is_Number for arg in args):
                    const = [a for a in args if a.is_Number][0]
                    rest = sp.Mul(*[a for a in args if not a.is_Number])
                    msg += "<b>1. Structure identifiée :</b> <span style='color: #e67e22;'>Produit par une constante (k × u)</span><br>"
                    msg += f"• Règle : <i>(k × u)' = k × u'</i> avec k = {const}<br>"
                    msg += f"• On dérive u(x) = {self.clean_math_display(rest)} → u'(x) = {self.clean_math_display(sp.diff(rest))}<br>"
                else:
                    u, v = args[0], sp.Mul(*args[1:])
                    up, vp = sp.diff(u), sp.diff(v)
                    msg += "<b>1. Structure identifiée :</b> <span style='color: #e67e22;'>Produit (u × v)</span><br>"
                    msg += f"• On pose : <b>u(x) = {self.clean_math_display(u)}</b> et <b>v(x) = {self.clean_math_display(v)}</b><br>"
                    msg += f"• On calcule les dérivées : <b>u'(x) = {self.clean_math_display(up)}</b> et <b>v'(x) = {self.clean_math_display(vp)}</b><br><br>"
                    msg += "<b>2. Application de la formule :</b><br>"
                    msg += "<div style='background: #fdf2e9; padding: 5px;'><i>f'(x) = u'v + uv'</i></div><br>"
                    msg += f"• f'(x) = ({self.clean_math_display(up)})({self.clean_math_display(v)}) + ({self.clean_math_display(u)})({self.clean_math_display(vp)})<br>"

            # --- CAS : COMPOSÉES (exp, log, sqrt, pow) ---
            elif any(isinstance(self.f, cls) for cls in [sp.exp, sp.log, sp.sin, sp.cos, sp.tan]) or self.f.is_Pow:
                if self.f.is_Pow:
                    base, exp = self.f.base, self.f.exp
                    if exp == 0.5:  # Racine carrée
                        u = base
                        up = sp.diff(u)
                        msg += "<b>1. Structure identifiée :</b> <span style='color: #e67e22;'>Racine carrée (√u)</span><br>"
                        msg += f"• Formule : <i>f'(x) = u' / (2√u)</i> avec u = {self.clean_math_display(u)}<br>"
                        msg += f"• u'(x) = {self.clean_math_display(up)}<br>"
                    else:  # Puissance u^n
                        u = base
                        up = sp.diff(u)
                        msg += f"<b>1. Structure identifiée :</b> <span style='color: #e67e22;'>Puissance (u<sup>{exp}</sup>)</span><br>"
                        msg += f"• Formule : <i>f'(x) = n · u' · u<sup>n-1</sup></i> avec n = {exp} et u = {self.clean_math_display(u)}<br>"
                        msg += f"• u'(x) = {self.clean_math_display(up)}<br>"
                else:  # Fonctions type e^u, ln(u), sin(u)...
                    u = self.f.args[0]
                    up = sp.diff(u)
                    func_name = self.f.func.__name__
                    formulas = {
                        'exp': ("e^u", "u' · e^u"),
                        'log': ("ln(u)", "u' / u"),
                        'sin': ("sin(u)", "u' · cos(u)"),
                        'cos': ("cos(u)", "u' · (-sin(u))")
                    }
                    form = formulas.get(func_name, ("f(u)", "u' · f'(u)"))
                    msg += f"<b>1. Structure identifiée :</b> <span style='color: #e67e22;'>Composée {form[0]}</span><br>"
                    msg += f"• Formule : <i>f'(x) = {form[1]}</i> avec u(x) = {self.clean_math_display(u)}<br>"
                    msg += f"• u'(x) = {self.clean_math_display(up)}<br>"

            # --- CAS : FONCTION USUELLE SIMPLE (x, x^2, sin(x)...) ---
            else:
                msg += "<b>1. Structure identifiée :</b> <span style='color: #e67e22;'>Fonction usuelle directe</span><br>"
                # Citation de la formule précise
                if self.f == self.x_sym:
                    msg += "• Formule : x ➜ 1"
                elif self.f.is_Number:
                    msg += "• Formule : k (constante) ➜ 0"
                else:
                    msg += "• Application directe d'une formule du tableau de référence."

            # 3. Résultat final
            msg += "<br><b>3. Résultat final après simplification :</b>"
            msg += f"<div style='color:#3498db; font-size:20px; font-weight:bold; background:#e8f4fd; padding:10px; border-radius:5px; border: 1px solid #3498db; margin-top:5px;'>"
            msg += f"f'(x) = {self.clean_math_display(self.df)}</div></div>"

            self.explanation_box.setHtml(msg)
            self.update_variation_table()
            self.update_graph(first_load=True)
            self.update_tangent()

        except Exception as e:
            self.explanation_box.setText(f"Erreur d'analyse détaillée : {e}")

    def update_variation_table(self):
        try:
            roots = [float(r.evalf()) for r in sp.solve(self.df, self.x_sym) if r.is_real]
            singularities = []
            _, den = sp.fraction(self.f)
            if den != 1: singularities = [float(s.evalf()) for s in sp.solve(den, self.x_sym) if s.is_real]
            if self.f.has(sp.log):
                for l in self.f.atoms(sp.log):
                    singularities += [float(s.evalf()) for s in sp.solve(l.args[0], self.x_sym) if s.is_real]
            all_pts = sorted(list(set(roots + singularities)))
        except:
            all_pts = []

        pts = [("-∞", None, False)]
        for p in all_pts:
            pts.append(("interval", p - 0.1, False))
            is_sing = any(abs(p - s) < 1e-5 for s in singularities)
            pts.append((f"{p:.1f}", p, is_sing))
        pts.append(("interval", (all_pts[-1] + 1 if all_pts else 0), False))
        pts.append(("+∞", None, False))

        self.variation_table.setColumnCount(len(pts) + 1)
        self.variation_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.variation_table.setRowHeight(2, 100)

        def set_item(r, c, text, bold=False, arrow=False, color="#000000"):
            txt = (text + "  │") if c == 0 else text
            item = QTableWidgetItem(txt)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setForeground(QColor(color))
            font = QFont("Arial", 11)
            if bold: font.setBold(True)
            if arrow: font.setPointSize(35); font.setBold(True)
            item.setFont(font)
            if c == 0: item.setBackground(QColor("#f2f2f2"))
            self.variation_table.setItem(r, c, item)

        set_item(0, 0, "x", True)
        set_item(1, 0, "f'(x)", True)
        set_item(2, 0, "f(x)", True)

        for i, (label, val, is_sing) in enumerate(pts):
            col = i + 1
            if label == "interval":
                try:
                    sign = "+" if self.df.subs(self.x_sym, val) > 0 else "-"
                    set_item(1, col, sign)
                    set_item(2, col, "↗" if sign == "+" else "↘", arrow=True)
                except:
                    set_item(1, col, "?")
            else:
                set_item(0, col, label, bold=True)
                if is_sing:
                    set_item(1, col, "||", color="red", bold=True)
                    set_item(2, col, "||", color="red", bold=True)
                elif label not in ["-∞", "+∞"]:
                    set_item(1, col, "0")
                    set_item(2, col, "|")

    def update_graph(self, first_load=False):
        self.plot_widget.clear()
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        x_np = np.linspace(-100, 100, 3000)
        try:
            f_func = sp.lambdify(self.x_sym, self.f, modules=['numpy', {'exp': np.exp, 'log': np.log}])
            y_np = f_func(x_np)
            y_np[np.abs(y_np) > 200] = np.nan
            if self.f.has(sp.log): y_np[x_np <= 0] = np.nan

            self.plot_widget.plot(x_np, y_np, pen=pg.mkPen('#3498db', width=3))
            if first_load:
                self.plot_widget.setXRange(-10, 10)
                self.plot_widget.setYRange(-10, 10)
                self.plot_widget.enableAutoRange(axis='x', enable=False)
                self.plot_widget.enableAutoRange(axis='y', enable=False)
        except:
            pass

    def update_tangent(self):
        if not hasattr(self, 'f'): return
        a = self.slider_a.value() / 10.0
        try:
            fa_val = self.f.subs(self.x_sym, a)
            dfa_val = self.df.subs(self.x_sym, a)
            if not fa_val.is_real: return
            fa, dfa = float(fa_val), float(dfa_val)
            x_t = np.array([-100, 100])
            y_t = dfa * (x_t - a) + fa
            if hasattr(self, 't_line'): self.plot_widget.removeItem(self.t_line)
            self.t_line = self.plot_widget.plot(x_t, y_t, pen=pg.mkPen('#e67e22', width=2, style=Qt.PenStyle.DashLine))
            b = fa - dfa * a
            self.tangent_info.setText(f"y = f'(a)(x - a) + f(a)  ➜  y = {dfa:.2f}x {'+' if b >= 0 else ''} {b:.2f}")
        except:
            pass