import numpy as np
import pyqtgraph as pg
import sympy as sp
import re
from sympy.calculus.util import continuous_domain
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFrame,
                               QLabel, QLineEdit, QPushButton, QButtonGroup,
                               QComboBox, QTextEdit)
from PySide6.QtCore import Qt


class LimitsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        self.setStyleSheet("""
            QWidget { color: black; font-family: 'Segoe UI', sans-serif; }
            QLabel { border: none; font-weight: bold; color: #2c3e50; background: transparent; }
            QLineEdit {
                color: black !important; background-color: white !important;
                border: 1px solid #bdc3c7; border-radius: 4px; padding: 6px;
            }
            QComboBox { color: black; background-color: white; border: 1px solid #bdc3c7; border-radius: 4px; padding: 5px; }

            QPushButton#ToggleBtn {
                background-color: #ecf0f1; border: 1px solid #bdc3c7; 
                padding: 8px; border-radius: 4px; font-weight: bold;
            }
            QPushButton#ToggleBtn:checked {
                background-color: #e67e22; color: white; border: 1px solid #d35400;
            }
        """)

        self.control_panel = QFrame()
        self.control_panel.setFixedWidth(340)
        self.control_panel.setStyleSheet("QFrame { background-color: #f8f9fa; border: none; border-radius: 8px; }")
        self.cp_layout = QVBoxLayout(self.control_panel)

        self.cp_layout.addWidget(QLabel("FONCTION f(x)"))
        self.input_func = QLineEdit()
        self.input_func.setPlaceholderText("Ex: exp(x)/x**2")
        self.cp_layout.addWidget(self.input_func)

        self.cp_layout.addSpacing(10)
        self.cp_layout.addWidget(QLabel("TEND VERS"))

        self.mode_group = QButtonGroup(self)
        self.btn_minus_inf = QPushButton("-∞")
        self.btn_minus_inf.setCheckable(True)
        self.btn_minus_inf.setObjectName("ToggleBtn")
        self.btn_plus_inf = QPushButton("+∞")
        self.btn_plus_inf.setCheckable(True)
        self.btn_plus_inf.setObjectName("ToggleBtn")
        self.btn_a = QPushButton("Point a")
        self.btn_a.setCheckable(True)
        self.btn_a.setObjectName("ToggleBtn")

        self.mode_group.addButton(self.btn_minus_inf)
        self.mode_group.addButton(self.btn_plus_inf)
        self.mode_group.addButton(self.btn_a)
        self.btn_plus_inf.setChecked(True)

        self.toggle_layout = QHBoxLayout()
        self.toggle_layout.addWidget(self.btn_minus_inf)
        self.toggle_layout.addWidget(self.btn_plus_inf)
        self.toggle_layout.addWidget(self.btn_a)
        self.cp_layout.addLayout(self.toggle_layout)

        self.a_params_frame = QFrame()
        self.a_params_layout = QHBoxLayout(self.a_params_frame)
        self.a_params_layout.setContentsMargins(0, 0, 0, 0)
        self.input_a = QLineEdit("0")
        self.input_a.setFixedWidth(60)
        self.combo_side = QComboBox()
        self.combo_side.addItems(["Globale (±)", "Gauche (-)", "Droite (+)"])
        self.a_params_layout.addWidget(QLabel("a = "))
        self.a_params_layout.addWidget(self.input_a)
        self.a_params_layout.addWidget(self.combo_side)
        self.cp_layout.addWidget(self.a_params_frame)
        self.a_params_frame.setVisible(False)

        self.btn_calc = QPushButton("ANALYSER LA LIMITE")
        self.btn_calc.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_calc.setStyleSheet(
            "background-color: #e67e22; color: white; font-weight: bold; padding: 12px; border-radius: 5px; border: none; margin-top: 10px;")
        self.cp_layout.addWidget(self.btn_calc)

        self.btn_continuity = QPushButton("ANALYSER LA CONTINUITÉ")
        self.btn_continuity.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_continuity.setStyleSheet(
            "background-color: #27ae60; color: white; font-weight: bold; padding: 12px; border-radius: 5px; border: none; margin-top: 5px;")
        self.cp_layout.addWidget(self.btn_continuity)

        self.cp_layout.addStretch()

        self.display_area = QFrame()
        self.display_area.setStyleSheet("background-color: white; border: 1px solid #dee2e6; border-radius: 8px;")
        self.display_layout = QVBoxLayout(self.display_area)

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.display_layout.addWidget(self.plot_widget, 3)

        self.analysis_log = QTextEdit()
        self.analysis_log.setReadOnly(True)
        self.analysis_log.setStyleSheet("border: none; background-color: #fdfefe; color: black; font-size: 14px;")
        self.display_layout.addWidget(self.analysis_log, 2)

        self.main_layout.addWidget(self.control_panel)
        self.main_layout.addWidget(self.display_area, 1)

        self.btn_a.toggled.connect(self.a_params_frame.setVisible)
        self.btn_calc.clicked.connect(self.calculate_limit)
        self.btn_continuity.clicked.connect(self.analyze_continuity)

    def clean_expr(self, text):
        return text.replace("x²", "x**2").replace("x³", "x**3").replace("√", "sqrt").replace("e(", "exp(").replace("^",
                                                                                                                   "**")

    def format_math_output(self, domain):
        if domain == sp.S.Reals: return "ℝ"
        if domain == sp.S.EmptySet: return "∅"

        def format_single_interval(interval):
            res = str(interval).replace("oo", "∞").replace("Interval", "").replace(".open", "")
            res = res.strip("()")

            left_bracket = "]" if interval.left_open else "["
            right_bracket = "[" if interval.right_open else "]"

            if "-∞" in str(interval.start): left_bracket = "]"
            if "∞" in str(interval.end): right_bracket = "["

            bounds = res.split(", ")
            return f"{left_bracket}{bounds[0]} ; {bounds[1]}{right_bracket}"


        if isinstance(domain, sp.Union):
            parts = [format_single_interval(arg) for arg in domain.args]
            return " ∪ ".join(parts)

        if isinstance(domain, sp.Interval):
            return format_single_interval(domain)

        return str(domain)

    def calculate_limit(self):
        func_raw = self.input_func.text()
        if not func_raw: return
        func_str = self.clean_expr(func_raw)
        x = sp.Symbol('x')

        try:
            if self.btn_minus_inf.isChecked():
                a_sym = -sp.oo
            elif self.btn_plus_inf.isChecked():
                a_sym = sp.oo
            else:
                a_sym = sp.simplify(self.input_a.text())

            dir_str = "+-"
            if self.btn_a.isChecked():
                side = self.combo_side.currentText()
                dir_str = "+-" if "Globale" in side else ("-" if "Gauche" in side else "+")

            expr = sp.simplify(func_str)
            limit_val = sp.limit(expr, x, a_sym, dir=dir_str)

            justifications = []
            if a_sym.is_infinite:
                if expr.has(sp.exp) and any(expr.has(p) for p in [sp.Pow, sp.Symbol]):
                    justifications.append(
                        "• <b>Propriété :</b> Par croissance comparée, l'exponentielle l'emporte sur toute puissance de x au voisinage de l'infini.")
                if expr.has(sp.log) and any(expr.has(p) for p in [sp.Pow, sp.Symbol]):
                    justifications.append(
                        "• <b>Propriété :</b> Par croissance comparée, toute puissance de x l'emporte sur le logarithme au voisinage de l'infini.")

            asymptotes = []
            if a_sym.is_infinite and limit_val.is_real:
                asymptotes.append(f"• <b>Asymptote horizontale :</b> y = {round(float(limit_val), 3)}")
            if not a_sym.is_infinite and limit_val.is_infinite:
                asymptotes.append(f"• <b>Asymptote verticale :</b> x = {a_sym}")

            a_txt = str(a_sym).replace("oo", "∞")
            res_txt = str(limit_val).replace("oo", "∞").replace("**", "^")

            html = f"<div style='color: black;'>"
            html += f"<p style='font-size: 16px;'>lim<sub>x → {a_txt}</sub> f(x) = <span style='color: #e67e22; font-size: 20px;'><b>{res_txt}</b></span></p>"
            html += f"<p>La limite de f(x) quand x tend vers {a_txt} est : <b>{res_txt}</b>.</p><hr>"
            if justifications:
                html += "<h3>Analyse Mathématique :</h3>" + "".join(f"<p>{j}</p>" for j in justifications)
            if asymptotes:
                html += "<h3>Comportement Asymptotique :</h3>" + "".join(f"<p>{a}</p>" for a in asymptotes)
            html += "</div>"

            self.analysis_log.setHtml(html)
            self.update_graph(expr, a_sym, limit_val)

        except Exception as e:
            self.analysis_log.setHtml(f"<b style='color:red;'>Erreur : {e}</b>")

    def analyze_continuity(self):
        func_raw = self.input_func.text()
        if not func_raw: return
        func_str = self.clean_expr(func_raw)
        x = sp.Symbol('x')

        try:
            expr = sp.simplify(func_str)
            domain = continuous_domain(expr, x, sp.S.Reals)
            df_text = self.format_math_output(domain)

            html = f"<div style='color: black;'>"
            html += f"<h2 style='color:#27ae60;'>ÉTUDE DE CONTINUITÉ</h2><hr>"
            html += f"<p><b>1. Ensemble de définition :</b></p>"
            html += f"<p style='font-size: 18px; text-align: center; color: #2c3e50; background: #f1f9f5; padding: 10px; border-radius: 5px;'>D<sub>f</sub> = {df_text}</p>"

            num, den = sp.fraction(expr)
            singularities = sp.solve(den, x)
            html += "<p><b>2. Analyse des ruptures :</b></p>"
            if singularities:
                html += f"<p>La fonction n'est pas définie en : <span style='color:#e74c3c;'>x ∈ {singularities}</span>.</p>"
            else:
                html += "<p>Aucune singularité détectée sur ℝ.</p>"

            html += f"<p><b>3. Conclusion :</b></p>"
            html += f"<p>f est continue sur chaque intervalle de son domaine de définition.</p>"
            html += f"<p style='border-left: 4px solid #27ae60; padding-left: 10px;'><b>f est continue sur {df_text}.</b></p>"
            html += "</div>"

            self.analysis_log.setHtml(html)
            self.update_graph(expr, sp.Symbol('0'), sp.Symbol('0'), is_domain_view=True)

        except Exception as e:
            self.analysis_log.setHtml(f"Erreur d'analyse : {e}")

    def update_graph(self, expr, a_sym, limit_val, is_domain_view=False):
        self.plot_widget.clear()
        self.plot_widget.addLine(x=0, pen=pg.mkPen('k', width=2))
        self.plot_widget.addLine(y=0, pen=pg.mkPen('k', width=2))

        try:
            if is_domain_view:
                x_s, x_e = -15, 15
            elif a_sym == sp.oo:
                x_s, x_e = 0, 50
            elif a_sym == -sp.oo:
                x_s, x_e = -50, 0
            else:
                v = float(a_sym.evalf())
                x_s, x_e = v - 10, v + 10

            x_np = np.linspace(x_s, x_e, 2000)
            f_np = sp.lambdify(sp.Symbol('x'), expr, "numpy")

            with np.errstate(divide='ignore', invalid='ignore'):
                y_np = f_np(x_np)

            y_np = np.where(np.abs(y_np) > 500, np.nan, y_np)
            self.plot_widget.plot(x_np, y_np, pen=pg.mkPen('#3498db', width=2.5))

            if not is_domain_view:
                if limit_val.is_real:
                    self.plot_widget.addLine(y=float(limit_val), pen=pg.mkPen('#e67e22', style=Qt.PenStyle.DashLine, width=2))
                if not a_sym.is_infinite and limit_val.is_infinite:
                    self.plot_widget.addLine(x=float(a_sym.evalf()),
                                             pen=pg.mkPen('#e74c3c', style=Qt.PenStyle.DashLine, width=2))

            self.plot_widget.setXRange(x_s, x_e)
        except:
            pass