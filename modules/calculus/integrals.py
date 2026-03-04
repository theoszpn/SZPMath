import numpy as np
import pyqtgraph as pg
import sympy as sp
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFrame,
                               QLabel, QLineEdit, QPushButton, QSlider,
                               QTextEdit)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont


class IntegralsPage(QWidget):
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
            QLabel#Title { font-size: 18px; font-weight: bold; color: #2c3e50; border-bottom: 2px solid #27ae60; margin-bottom: 5px; }

            QLabel#MathSymbol { 
                font-size: 40px; 
                font-family: 'Cambria Math', 'serif'; 
                color: #2c3e50; 
                background-color: #f8f9fa; 
                padding: 0 10px;
            }

            QLineEdit { border: 2px solid #bdc3c7; border-radius: 5px; padding: 10px; font-size: 16px; background-color: white; }
            QTextEdit { border: 1px solid #dee2e6; border-radius: 8px; background: #fdfdfd; font-size: 14px; line-height: 150%; }
            QFrame#Panel { background-color: #f8f9fa; border-radius: 12px; border: 1px solid #dee2e6; }
            QPushButton#ActionBtn { background-color: #27ae60; color: white; font-weight: bold; padding: 15px; border-radius: 6px; border: none; font-size: 16px;}
            QPushButton#ActionBtn:hover { background-color: #219150; }
        """)

        self.left_panel = QFrame()
        self.left_panel.setFixedWidth(480)
        self.left_panel.setObjectName("Panel")
        self.left_layout = QVBoxLayout(self.left_panel)

        self.left_layout.addWidget(QLabel("FORMULES PRIMITIVES", objectName="Title"))
        self.memo_box = QTextEdit()
        self.memo_box.setReadOnly(True)
        self.memo_box.setHtml(self.get_integrals_memo_html())
        self.memo_box.setFixedHeight(280)
        self.left_layout.addWidget(self.memo_box)

        self.left_layout.addWidget(QLabel("CALCUL INTÉGRAL ÉDITEUR", objectName="Title"))
        input_container = QHBoxLayout()
        input_container.setSpacing(0)

        integral_label = QLabel("∫", objectName="MathSymbol")
        dx_label = QLabel("dx", objectName="MathSymbol")
        dx_label.setStyleSheet("font-size: 28px; background-color: #f8f9fa; padding-top: 15px;")

        self.input_func = QLineEdit()
        self.input_func.setPlaceholderText("Saisir f(x)...")

        input_container.addWidget(integral_label)
        input_container.addWidget(self.input_func)
        input_container.addWidget(dx_label)
        self.left_layout.addLayout(input_container)

        bornes_layout = QHBoxLayout()
        self.borne_a = QLineEdit("0")
        self.borne_b = QLineEdit("2")
        bornes_layout.addWidget(QLabel("Borne inf (a) :"))
        bornes_layout.addWidget(self.borne_a)
        bornes_layout.addWidget(QLabel("Borne sup (b) :"))
        bornes_layout.addWidget(self.borne_b)
        self.left_layout.addLayout(bornes_layout)

        self.btn_calculate = QPushButton("CALCULER ET ANALYSER", objectName="ActionBtn")
        self.btn_calculate.clicked.connect(self.calculate_all)
        self.left_layout.addWidget(self.btn_calculate)

        self.explanation_box = QTextEdit()
        self.explanation_box.setReadOnly(True)
        self.left_layout.addWidget(self.explanation_box)

        self.right_container = QFrame()
        self.right_layout = QVBoxLayout(self.right_container)

        self.integral_info = QLabel("Aire ∫[a,b] f(x) dx = ...")
        self.integral_info.setStyleSheet("""
            color: #27ae60; font-weight: bold; background: #eafaf1; 
            padding: 15px; border-radius: 8px; border: 1px solid #abebc6; font-size: 18px;
        """)
        self.right_layout.addWidget(self.integral_info)

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.right_layout.addWidget(self.plot_widget)

        self.slider_a = QSlider(Qt.Orientation.Horizontal)
        self.slider_a.setRange(-50, 150)
        self.slider_a.setValue(0)
        self.slider_b = QSlider(Qt.Orientation.Horizontal)
        self.slider_b.setRange(-50, 150)
        self.slider_b.setValue(20)
        self.slider_a.valueChanged.connect(self.update_from_sliders)
        self.slider_b.valueChanged.connect(self.update_from_sliders)

        self.right_layout.addWidget(QLabel("Ajustement dynamique des bornes (a) et (b) :"))
        self.right_layout.addWidget(self.slider_a)
        self.right_layout.addWidget(self.slider_b)

        self.main_layout.addWidget(self.left_panel)
        self.main_layout.addWidget(self.right_container, 1)

    def get_integrals_memo_html(self):
        return """
        <table width="100%" border="1" style="border-collapse: collapse; text-align: center; background-color: white; font-size: 14px;">
            <tr style="background-color: #2c3e50; color: white;">
                <th width="50%"><b>Fonction f(x)</b></th>
                <th width="50%"><b>Primitive F(x)</b></th>
            </tr>
            <tr style="background-color: #f2f2f2;"><td colspan="2"><b>Fonctions Puissances</b></td></tr>
            <tr><td>0</td><td style="color: #27ae60; font-weight: bold;">k</td></tr>
            <tr><td>k (constante)</td><td style="color: #27ae60; font-weight: bold;">kx</td></tr>
            <tr><td>x<sup>n</sup></td><td style="color: #27ae60; font-weight: bold;">x<sup>n+1</sup> / (n+1)</td></tr>
            <tr><td>1/x</td><td style="color: #27ae60; font-weight: bold;">ln|x|</td></tr>
            <tr><td>1/x<sup>2</sup></td><td style="color: #27ae60; font-weight: bold;">-1/x</td></tr>
            <tr><td>1/√x</td><td style="color: #27ae60; font-weight: bold;">2√x</td></tr>

            <tr style="background-color: #f2f2f2;"><td colspan="2"><b>Exponentielles / Logarithmes</b></td></tr>
            <tr><td>e<sup>x</sup></td><td style="color: #27ae60; font-weight: bold;">e<sup>x</sup></td></tr>
            <tr><td>u'(x)e<sup>u(x)</sup></td><td style="color: #27ae60; font-weight: bold;">e<sup>u(x)</sup></td></tr>
            <tr><td>u'(x)/u(x)</td><td style="color: #27ae60; font-weight: bold;">ln|u(x)|</td></tr>

            <tr style="background-color: #f2f2f2;"><td colspan="2"><b>Trigonométrie</b></td></tr>
            <tr><td>cos(x)</td><td style="color: #27ae60; font-weight: bold;">sin(x)</td></tr>
            <tr><td>sin(x)</td><td style="color: #27ae60; font-weight: bold;">-cos(x)</td></tr>
            <tr><td>1 + tan<sup>2</sup>(x)</td><td style="color: #27ae60; font-weight: bold;">tan(x)</td></tr>

            <tr style="background-color: #f2f2f2;"><td colspan="2"><b>Formes Composées (u fonction)</b></td></tr>
            <tr><td>u' + v'</td><td style="color: #27ae60; font-weight: bold;">u + v</td></tr>
            <tr><td>ku'</td><td style="color: #27ae60; font-weight: bold;">ku</td></tr>
            <tr><td>u'u<sup>n</sup></td><td style="color: #27ae60; font-weight: bold;">u<sup>n+1</sup> / (n+1)</td></tr>
            <tr><td>u'/√u</td><td style="color: #27ae60; font-weight: bold;">2√u</td></tr>
        </table>
        """

    def calculate_all(self):
        try:
            raw = self.input_func.text().replace(',', '.')
            raw = raw.replace('e(', 'exp(').replace('e^', 'exp(').replace('ln', 'log')

            self.f = sp.sympify(raw)
            self.F = sp.integrate(self.f, self.x_sym)

            a_sym = sp.sympify(self.borne_a.text())
            b_sym = sp.sympify(self.borne_b.text())
            a_val = float(a_sym.evalf())
            b_val = float(b_sym.evalf())

            msg = "<div style='font-size: 15px; line-height: 1.8; font-family: Segoe UI, serif;'>"
            msg += "<h2 style='color: #27ae60; border-bottom: 2px solid #27ae60; padding-bottom: 5px;'>Démonstration</h2>"

            msg += "<b style='color: #2c3e50;'>Étape 1 : Énoncé du problème</b><br>"
            msg += "L'objectif est de déterminer l'aire de la surface délimitée par la courbe representative de la fonction f, "
            msg += "l'axe des abscisses et les droites verticales d'équations x = a et x = b.<br>"
            msg += "On définit l'intégrale I suivante :<br>"
            msg += f"<center><i style='font-size: 22px;'>I = &int;<sub>{self.format_math(a_sym)}</sub><sup>{self.format_math(b_sym)}</sup> ({self.format_math(self.f)}) dx</i></center><br>"

            msg += "<b style='color: #2c3e50;'>Étape 2 : Analyse de la continuité et domaine</b><br>"
            intervalle_etude = sp.Interval(min(a_val, b_val), max(a_val, b_val))
            singularites = sp.singularities(self.f, self.x_sym, intervalle_etude)

            if singularites:
                msg += "<div style='background: #fff5f5; border: 1px solid #ffcccc; padding: 15px; border-radius: 8px; color: #cc0000;'>"
                msg += "<b>⚠️ Erreur de définition :</b> La fonction présente des valeurs interdites sur l'intervalle choisi.<br>"
                msg += f"Points de rupture détectés : { {self.format_math(s) for s in singularites} }.<br>"
                msg += "Conformément aux conditions de Riemann, f doit être continue pour être intégrable.</div>"
                self.explanation_box.setHtml(msg)
                return

            msg += f"La fonction f est continue sur l'intervalle d'étude [{self.format_math(a_sym)} ; {self.format_math(b_sym)}]. "
            msg += "Elle admet donc des primitives.<br><br>"

            msg += "<b style='color: #2c3e50;'>Étape 3 : Identification de la forme et stratégie</b><br>"
            num, den = sp.fraction(self.f)
            analysed = False

            if self.f.is_Mul and not any(arg.is_Number for arg in self.f.args):
                poly = [a for a in self.f.args if a.is_polynomial(self.x_sym)]
                trans = [a for a in self.f.args if a.has(sp.exp, sp.sin, sp.cos, sp.log)]
                if poly and trans:
                    msg += "• On identifie un <b>produit de fonctions de natures différentes</b>.<br>"
                    msg += "➜ Méthode : <b>Intégration Par Parties (IPP)</b> : &int;uv' = uv - &int;u'v.<br>"
                    msg += f"➜ On pose u(x) = {self.format_math(poly[0])} et v'(x) = {self.format_math(trans[0])}.<br>"
                    msg += f"➜ On déduit u'(x) = {self.format_math(sp.diff(poly[0]))} et v(x) = {self.format_math(sp.integrate(trans[0]))}.<br>"
                    analysed = True

            if not analysed and den != 1:
                u_c = den.base if den.is_Pow else den
                n_c = den.exp if den.is_Pow else 1
                du_c = sp.diff(u_c, self.x_sym)
                k_c = sp.simplify(num / du_c)

                if k_c.is_Number:
                    msg += "• On détecte une structure de type quotient <b>u'/u<sup>n</sup></b>.<br>"
                    msg += f"➜ On identifie <b>u(x) = {self.format_math(u_c)}</b> et <b>u'(x) = {self.format_math(du_c)}</b>.<br>"
                    if n_c == 1:
                        msg += "➜ Formule : La primitive de u'/u est <b>F(x) = ln|u|</b>.<br>"
                    else:
                        msg += f"➜ Formule : La primitive de u'/u<sup>{n_c}</sup> est <b>F(x) = -1/((n-1)u<sup>n-1</sup>)</b>.<br>"
                    if k_c != 1:
                        msg += f"➜ <b>Ajustement :</b> f(x) = {self.format_math(k_c)} &times; (u'/u<sup>{n_c}</sup>).<br>"
                    analysed = True

            if not analysed and self.f.has(sp.exp) and not self.f.is_Add:
                u_arg = list(self.f.atoms(sp.exp))[0].args[0]
                du_arg = sp.diff(u_arg, self.x_sym)
                k_exp = sp.simplify(self.f / (sp.exp(u_arg) * du_arg))
                if k_exp.is_Number:
                    msg += "• On détecte une structure de type <b>u'e<sup>u</sup></b>.<br>"
                    msg += f"➜ On pose <b>u(x) = {self.format_math(u_arg)}</b> et sa dérivée <b>u'(x) = {self.format_math(du_arg)}</b>.<br>"
                    msg += "➜ Formule : La primitive de u'e<sup>u</sup> est <b>F(x) = e<sup>u</sup></b>.<br>"
                    analysed = True

            if not analysed and (self.f.is_Pow or self.f == self.x_sym or self.f.is_Number):
                msg += "• On identifie une <b>forme usuelle directe</b> (Puissance ou Constante).<br>"
                msg += "➜ Formule : La primitive de x<sup>n</sup> est <b>F(x) = x<sup>n+1</sup>/(n+1)</b>.<br>"
                analysed = True

            if not analysed:
                msg += "• Analyse par décomposition linéarisée ou identification directe du tableau.<br>"

            msg += "<br><b style='color: #2c3e50;'>Étape 4 : Détermination de la primitive F(x)</b><br>"
            msg += "En appliquant les règles identifiées, nous déduisons l'expression de la primitive :<br>"
            msg += f"<div style='background: #fdfdfd; padding: 15px; border: 1px solid #27ae60; border-radius: 8px; margin: 10px 0; text-align: center; font-size: 18px; color: #1e8449;'>"
            msg += f"<b>F(x) = {self.format_math(self.F)}</b></div>"

            msg += "<b style='color: #2c3e50;'>Étape 5 : Évaluation entre les bornes</b><br>"
            msg += "La valeur de l'intégrale est :<br>"
            msg += f"<center><i style='font-size: 20px;'>I = [ {self.format_math(self.F)} ]<sub>{self.format_math(a_sym)}</sub><sup>{self.format_math(b_sym)}</sup></i></center><br>"
            msg += f"Ce qui conduit au calcul de la différence : <b>I = F({self.format_math(b_sym)}) - F({self.format_math(a_sym)})</b>.<br><br>"

            fb_exact = self.F.subs(self.x_sym, b_sym)
            fa_exact = self.F.subs(self.x_sym, a_sym)

            msg += f"<b style='color: #2c3e50;'>Étape 6 : Calcul de F({self.format_math(b_sym)})</b><br>"
            msg += f"<center>F({self.format_math(b_sym)}) = <b>{self.format_math(fb_exact)}</b></center><br>"

            msg += f"<b style='color: #2c3e50;'>Étape 7 : Calcul de F({self.format_math(a_sym)})</b><br>"
            msg += f"<center>F({self.format_math(a_sym)}) = <b>{self.format_math(fa_exact)}</b></center><br>"

            msg += "<b style='color: #2c3e50;'>Étape 8 : Soustraction finale</b><br>"
            msg += f"I = ({self.format_math(fb_exact)}) - ({self.format_math(fa_exact)})<br>"

            valeur_exacte = fb_exact - fa_exact

            msg += "<div style='background: #eafaf1; padding: 20px; border: 2px solid #27ae60; border-radius: 10px; margin-top: 15px;'>"
            msg += f"<b style='color: #219150; font-size: 20px;'>VALEUR EXACTE : I = {self.format_math(valeur_exacte)}</b><br>"

            res_num = float(valeur_exacte.evalf())
            msg += f"<i style='color: #7f8c8d; font-size: 14px;'>Valeur numérique approchée : I &approx; {res_num:.4f} unités d'aire (u.a.).</i><br>"
            msg += "</div></div>"

            self.explanation_box.setHtml(msg)
            self.integral_info.setText(f"Résultat : I = {res_num:.4f} u.a.")
            self.update_graph(a_val, b_val)

        except Exception as e:
            self.explanation_box.setText(f"Erreur d'analyse experte : {e}")

    def format_math(self, expr):
        import re
        s = str(expr).replace('.0', '')

        s = re.sub(r'exp\((.*?)\)', r'e<sup>\1</sup>', s)
        s = s.replace('E', 'e')

        def sub_pow(match):
            base = match.group(1)
            exp = match.group(2)
            if base.startswith('(') and base.endswith(')') and len(base) <= 3:
                base = base[1:-1]
            return f"{base}<sup>{exp}</sup>"

        s = re.sub(r'([\w\(\)]+)\*\*([\w\(\)\-]+)', sub_pow, s)
        s = s.replace('**', '^')

        s = s.replace('log', 'ln').replace('sqrt', '&radic;').replace('pi', '&pi;')
        s = s.replace('*', '&nbsp;')

        return s

    def update_from_sliders(self):
        a, b = self.slider_a.value() / 10.0, self.slider_b.value() / 10.0
        self.borne_a.setText(str(a))
        self.borne_b.setText(str(b))
        if hasattr(self, 'f'): self.update_graph(a, b)

    def update_graph(self, a, b):
        self.plot_widget.clear()

        x_plot = np.linspace(0, 100, 2000)
        try:
            f_func = sp.lambdify(self.x_sym, self.f, modules=['numpy', {'exp': np.exp, 'log': np.log}])
            y_plot = f_func(x_plot)

            y_plot[np.abs(y_plot) > 500] = np.nan

            self.plot_widget.plot(x_plot, y_plot, pen=pg.mkPen('#2c3e50', width=3))

            x_fill = np.linspace(min(a, b), max(a, b), 600)
            y_fill = f_func(x_fill)

            y_fill = np.nan_to_num(y_fill, nan=0.0, posinf=0.0, neginf=0.0)

            curve_top = pg.PlotCurveItem(x_fill, y_fill, pen=None)
            curve_base = pg.PlotCurveItem(x_fill, np.zeros_like(x_fill), pen=None)

            fill_item = pg.FillBetweenItem(curve_top, curve_base, brush=QColor(39, 174, 96, 130))
            self.plot_widget.addItem(fill_item)

            self.plot_widget.setXRange(-0.5, 12)
            self.plot_widget.setYRange(-2, 18)
            self.plot_widget.enableAutoRange(enable=False)

        except Exception as e:
            print(f"Erreur graphique: {e}")