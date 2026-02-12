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
        <table width="100%" height="100%" border="1" style="border-collapse: collapse; text-align: center; background-color: white; font-size: 18px;">
            <tr style="background-color: #2c3e50; color: white;">
                <th><b>Fonction f(x)</b></th><th><b>Primitive F(x)</b></th>
            </tr>
            <tr><td>k (constante)</td><td style="color: #27ae60; font-weight: bold;">kx</td></tr>
            <tr><td>x<sup>n</sup></td><td style="color: #27ae60; font-weight: bold;">x<sup>n+1</sup> / (n+1)</td></tr>
            <tr><td>1/x</td><td style="color: #27ae60; font-weight: bold;">ln|x|</td></tr>
            <tr><td>e<sup>x</sup></td><td style="color: #27ae60; font-weight: bold;">e<sup>x</sup></td></tr>
            <tr><td>cos(x)</td><td style="color: #27ae60; font-weight: bold;">sin(x)</td></tr>
            <tr><td>sin(x)</td><td style="color: #27ae60; font-weight: bold;">-cos(x)</td></tr>
            <tr><td>u'(x) / u(x)</td><td style="color: #27ae60; font-weight: bold;">ln|u(x)|</td></tr>
            <tr><td>u'(x) e<sup>u(x)</sup></td><td style="color: #27ae60; font-weight: bold;">e<sup>u(x)</sup></td></tr>
            <tr><td>u'(x) u(x)<sup>n</sup></td><td style="color: #27ae60; font-weight: bold;">u<sup>n+1</sup> / (n+1)</td></tr>
        </table>
        """

    def clean_math_display(self, expr):
        return str(expr).replace("**", "^").replace("*", "").replace("exp", "e").replace("log", "ln")

    def calculate_all(self):
        try:
            raw = self.input_func.text().replace(',', '.').replace('e(', 'exp(').replace('e^', 'exp(').replace('ln',
                                                                                                               'log')
            self.f = sp.sympify(raw)
            self.F = sp.integrate(self.f, self.x_sym)

            a_val, b_val = float(self.borne_a.text()), float(self.borne_b.text())
            res_exact = sp.integrate(self.f, (self.x_sym, a_val, b_val))
            res_num = res_exact.evalf()

            msg = "<b style='color: #2c3e50; font-size: 16px;'>I. ANALYSE DE LA STRUCTURE</b><br>"

            if self.f.is_Add:
                msg += "• <i>Propriété de Linéarité :</i> f(x) est une somme de termes. On applique : ∫[u(x) + v(x)]dx = ∫u(x)dx + ∫v(x)dx.<br>"

            num, den = sp.fraction(self.f)
            if den != 1:
                msg += "• <i>Détection de Fraction :</i> On examine la forme u'(x)/u(x).<br>"
                u_c = den
                du_c = sp.diff(u_c, self.x_sym)
                coeff = sp.simplify(num / du_c)
                if coeff.is_Number:
                    msg += f"  → Forme reconnue : {coeff} * (u'/u) avec u(x) = {u_c}.<br>"
                else:
                    msg += "  → Forme complexe : intégration par décomposition.<br>"

            if self.f.has(sp.exp):
                msg += "• <i>Détection Exponentielle :</i> On cherche la forme u'(x)e^u(x).<br>"

            msg += f"<br><b style='color: #2c3e50; font-size: 16px;'>II. CALCUL DE LA PRIMITIVE</b><br>"
            msg += f"En utilisant le tableau des primitives usuelles :<br>"
            msg += f"<center><b style='color:#27ae60; font-size: 18px;'>F(x) = {self.clean_math_display(self.F)} + C</b></center><br>"

            msg += f"<b style='color: #2c3e50; font-size: 16px;'>III. ÉVALUATION NUMÉRIQUE (THÉORÈME FONDAMENTAL)</b><br>"
            msg += f"On calcule la variation de la primitive entre a={a_val} et b={b_val} :<br>"
            fb = self.F.subs(self.x_sym, b_val).evalf()
            fa = self.F.subs(self.x_sym, a_val).evalf()
            msg += f"• F(b) = F({b_val}) = {fb:.4f}<br>"
            msg += f"• F(a) = F({a_val}) = {fa:.4f}<br>"
            msg += f"• <b>Résultat :</b> F(b) - F(a) = <span style='color:#3498db; font-weight:bold;'>{res_num:.4f}</span>"

            self.explanation_box.setHtml(msg)
            self.integral_info.setText(f"Résultat : ∫[{a_val} ; {b_val}] f(x) dx = {res_num:.4f} u.a.")

            self.update_graph(a_val, b_val)

        except Exception as e:
            self.explanation_box.setText(f"Erreur d'analyse : {e}")

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