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
            QPushButton#ActionBtn { background-color: #3498db; color: white; font-weight: bold; padding: 12px; border-radius: 6px; border: none; font-size: 15px;}
            QPushButton#ActionBtn:hover { background-color: #2980b9; }
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

        self.btn_derive = QPushButton("ANALYSER LA FONCTION", objectName="ActionBtn")
        self.btn_derive.clicked.connect(self.calculate_all)
        self.left_layout.addWidget(self.btn_derive)

        self.explanation_box = QTextEdit()
        self.explanation_box.setReadOnly(True)
        self.left_layout.addWidget(self.explanation_box)

        self.right_container = QFrame()
        self.right_layout = QVBoxLayout(self.right_container)

        self.right_layout.addWidget(QLabel("TABLEAU DE VARIATIONS", objectName="Title"))
        self.variation_table = QTableWidget(3, 1)
        self.variation_table.setFixedHeight(220)
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

    def get_full_memo_html(self):
        return """
        <table width="100%" height="100%" border="1" style="border-collapse: collapse; text-align: center; background-color: white; font-size: 18px;">
            <tr style="background-color: #2c3e50; color: white;">
                <th><b>f(x)</b></th><th><b>f'(x)</b></th>
            </tr>
            <tr><td>k</td><td style="color: #e67e22; font-weight: bold;">0</td></tr>
            <tr><td>x<sup>n</sup></td><td style="color: #e67e22; font-weight: bold;">nx<sup>n-1</sup></td></tr>
            <tr><td>1/x</td><td style="color: #e67e22; font-weight: bold;">-1/x<sup>2</sup></td></tr>
            <tr><td>√x</td><td style="color: #e67e22; font-weight: bold;">1/(2√x)</td></tr>
            <tr><td>e<sup>u</sup></td><td style="color: #e67e22; font-weight: bold;">u'e<sup>u</sup></td></tr>
            <tr><td>ln(u)</td><td style="color: #e67e22; font-weight: bold;">u'/u</td></tr>
            <tr><td>sin(x)</td><td style="color: #e67e22; font-weight: bold;">cos(x)</td></tr>
            <tr><td>cos(x)</td><td style="color: #e67e22; font-weight: bold;">-sin(x)</td></tr>
            <tr><td><b>u × v</b></td><td style="color: #e67e22; font-weight: bold;">u'v + uv'</td></tr>
            <tr><td><b>u / v</b></td><td style="color: #e67e22; font-weight: bold;">(u'v - uv') / v<sup>2</sup></td></tr>
        </table>
        """

    def clean_math_display(self, expr):
        return str(expr).replace("**", "^").replace("*", "").replace("exp", "e").replace("log", "ln")

    def calculate_all(self):
        try:
            raw = self.input_func.text().replace(',', '.')
            raw = raw.replace('e(', 'exp(').replace('e^', 'exp(')
            if 'exp(' in raw and ')' not in raw[raw.find('exp('):]: raw += ')'
            raw = raw.replace('ln', 'log')

            self.f = sp.sympify(raw)
            self.df = sp.diff(self.f, self.x_sym)

            msg = "<b>1. Analyse détaillée :</b><br>"
            num, den = sp.fraction(self.f)

            if den != 1 and not den.is_Number:
                u, v = num, den
                up, vp = sp.diff(u), sp.diff(v)
                msg += "• Règle : <span style='color: #e67e22;'>Quotient (u/v)'</span><br>"
                msg += f"• u = {u} ; v = {v}<br>"
                msg += f"• u' = {up} ; v' = {vp}<br><br>"
                msg += "<b>2. Développement du numérateur :</b><br>"
                msg += f"• u'v = ({up}) × ({v})<br>"
                msg += f"• uv' = ({u}) × ({vp})<br>"
                num_calc = sp.expand(up * v - u * vp)
                msg += f"• u'v - uv' = <span style='color: #27ae60;'>{self.clean_math_display(num_calc)}</span>"

            elif self.f.has(sp.exp) or self.f.has(sp.log):
                is_exp = self.f.has(sp.exp)
                node = self.f.atoms(sp.exp).pop() if is_exp else self.f.atoms(sp.log).pop()
                u_func = node.args[0]
                msg += f"• Règle : <span style='color: #e67e22;'>Composée {'Exponentielle' if is_exp else 'Logarithme'}</span><br>"
                msg += f"• u(x) = {u_func} → u'(x) = {sp.diff(u_func)}<br>"
                msg += f"• Formule : {'u\'e^u' if is_exp else 'u\'/u'}"

            elif self.f.is_Add:
                msg += "• Règle : <span style='color: #e67e22;'>Somme u' + v'</span>"
            else:
                msg += "• Règle : Formule usuelle directe."

            msg += f"<br><br><b>3. Résultat final :</b>"
            msg += f"<div style='color:#3498db; font-size:18px; font-weight:bold;'>f'(x) = {self.clean_math_display(self.df)}</div>"

            self.explanation_box.setHtml(msg)
            self.update_variation_table()
            self.update_graph(first_load=True)
            self.update_tangent()
        except Exception as e:
            self.explanation_box.setText(f"Erreur d'analyse : {e}")

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