import numpy as np
import pyqtgraph as pg
import sympy as sp
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFrame,
                               QLabel, QLineEdit, QPushButton, QFormLayout,
                               QComboBox, QListWidget, QListWidgetItem)
from PySide6.QtCore import Qt


class FunctionPlotterPage(QWidget):
    def __init__(self):
        super().__init__()
        self.active_plots = {}
        self.selected_fid = None
        self.colors = ['#e74c3c', '#3498db', '#2ecc71', '#f1c40f', '#9b59b6', '#e67e22']
        self.color_index = 0
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
            QComboBox, QListWidget {
                color: black; background-color: white; border: 1px solid #bdc3c7; border-radius: 4px;
            }
        """)

        self.control_panel = QFrame()
        self.control_panel.setFixedWidth(340)
        self.control_panel.setStyleSheet("QFrame { background-color: #f8f9fa; border: none; border-radius: 8px; }")
        self.cp_layout = QVBoxLayout(self.control_panel)

        self.cp_layout.addWidget(QLabel("FONCTIONS TYPES"))
        self.quick_insert = QComboBox()
        self.quick_insert.addItems(
            ["-- Insérer --", "x²", "x³", "e(x)", "sin(x)", "cos(x)", "√(x)", "log(x)", "ln(x)", "1/x"])
        self.quick_insert.activated.connect(self.insert_function_type)
        self.cp_layout.addWidget(self.quick_insert)

        self.cp_layout.addWidget(QLabel("SAISIE f(x)"))
        self.input_layout = QHBoxLayout()
        self.func_input = QLineEdit()
        self.func_input.setPlaceholderText("Ex: 2*sin(x) + √(x)")

        self.btn_add = QPushButton("+")
        self.btn_add.setFixedSize(32, 32)
        self.btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add.setStyleSheet("""
            QPushButton { 
                background-color: #27ae60; color: white; font-weight: bold; 
                font-size: 22px; border-radius: 4px; border: none;
                text-align: center; padding: 0px 0px 4px 0px; 
            }
            QPushButton:hover { background-color: #2ecc71; }
        """)
        self.btn_add.clicked.connect(self.add_function)

        self.input_layout.addWidget(self.func_input)
        self.input_layout.addWidget(self.btn_add)
        self.cp_layout.addLayout(self.input_layout)

        self.cp_layout.addWidget(QLabel("FENÊTRE D'ÉTUDE"))
        self.range_form = QFormLayout()
        self.input_xmin = QLineEdit("-10")
        self.input_xmax = QLineEdit("10")
        self.range_form.addRow("x min :", self.input_xmin)
        self.range_form.addRow("x max :", self.input_xmax)
        self.cp_layout.addLayout(self.range_form)

        self.cp_layout.addWidget(QLabel("HISTORIQUE"))
        self.history_list = QListWidget()
        self.history_list.setStyleSheet("background-color: #FFFFFF;")
        self.history_list.itemClicked.connect(self.load_from_history)
        self.cp_layout.addWidget(self.history_list)
        self.cp_layout.addStretch()

        self.display_area = QFrame()
        self.display_area.setStyleSheet("background-color: white; border: 1px solid #dee2e6; border-radius: 8px;")
        self.display_layout = QVBoxLayout(self.display_area)

        self.legend_container = QFrame()
        self.legend_layout = QHBoxLayout(self.legend_container)
        self.legend_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.display_layout.addWidget(self.legend_container)

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.plot_widget.setAspectLocked(True, ratio=1)

        self.plot_widget.addLine(x=0, pen=pg.mkPen('k', width=2))
        self.plot_widget.addLine(y=0, pen=pg.mkPen('k', width=2))

        for axis in ['left', 'bottom']:
            self.plot_widget.getAxis(axis).setPen('k')
            self.plot_widget.getAxis(axis).setTextPen('k')

        self.display_layout.addWidget(self.plot_widget, 4)

        self.analysis_frame = QFrame()
        self.analysis_frame.setFixedHeight(130)
        self.analysis_frame.setStyleSheet("background-color: #fdfefe; border-top: 1px solid #dee2e6;")
        self.analysis_layout = QVBoxLayout(self.analysis_frame)
        self.lbl_analysis_results = QLabel("Cliquez sur une fonction pour l'analyser.")
        self.lbl_analysis_results.setStyleSheet("font-size: 14px; color: black;")
        self.analysis_layout.addWidget(self.lbl_analysis_results)
        self.display_layout.addWidget(self.analysis_frame)

        self.main_layout.addWidget(self.control_panel)
        self.main_layout.addWidget(self.display_area, 1)

    def insert_function_type(self):
        text = self.quick_insert.currentText()
        if text == "-- Insérer --": return
        self.func_input.setText(self.func_input.text() + text)
        self.func_input.setFocus()

    def clean_expression(self, text):
        expr = text.replace("x²", "x**2").replace("x³", "x**3")
        expr = expr.replace("√", "sqrt").replace("e(", "exp(").replace("^", "**")
        expr = expr.replace("ln(", "log(").replace("log(", "log10(")
        return expr

    def add_function(self):
        raw_text = self.func_input.text().strip()
        if not raw_text: return

        calc_expr = self.clean_expression(raw_text)
        pretty_text = raw_text.replace("sqrt", "√").replace("exp(", "e(").replace("**", "^").replace("**2",
                                                                                                     "²").replace("**3",
                                                                                                                  "³")
        color = self.colors[self.color_index % len(self.colors)]
        self.color_index += 1

        try:
            xmin, xmax = float(self.input_xmin.text()), float(self.input_xmax.text())
            x_wide = np.linspace(-1000, 1000, 20000)

            safe_dict = {
                'x': x_wide, 'sin': np.sin, 'cos': np.cos, 'tan': np.tan,
                'exp': np.exp, 'log10': np.log10, 'log': np.log, 'sqrt': np.sqrt,
                'abs': np.abs, 'pi': np.pi, 'e': np.e
            }

            y = eval(calc_expr, {"__builtins__": __builtins__}, safe_dict)
            curve = self.plot_widget.plot(x_wide, y, pen=pg.mkPen(color=color, width=2.5))
            fid = str(id(curve))
            self.active_plots[fid] = {'pretty': pretty_text, 'raw': raw_text, 'curve': curve, 'color': color}

            exists = False
            for i in range(self.history_list.count()):
                if self.history_list.item(i).data(Qt.ItemDataRole.UserRole) == raw_text:
                    exists = True
                    break

            if not exists:
                item = QListWidgetItem(pretty_text)
                item.setData(Qt.ItemDataRole.UserRole, raw_text)
                self.history_list.insertItem(0, item)

            self.func_input.clear()
            self.update_legend_ui()
            self.select_function(fid)

            self.plot_widget.setXRange(xmin, xmax, padding=0)
            half = (xmax - xmin) / 2
            self.plot_widget.setYRange(-half, half, padding=0)

        except Exception as e:
            print(f"Erreur : {e}")

    def update_legend_ui(self):
        while self.legend_layout.count():
            item = self.legend_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        for fid, data in self.active_plots.items():
            badge = QFrame()
            is_sel = (fid == self.selected_fid)
            badge.setStyleSheet(
                f"background-color: white; border: {'2.5px solid ' + data['color'] if is_sel else '1.2px solid #bdc3c7'}; border-radius: 12px;")
            b_layout = QHBoxLayout(badge)
            b_layout.setContentsMargins(10, 2, 5, 2)
            lbl = QLabel(f"f(x) = {data['pretty']}")
            lbl.setStyleSheet(f"color: {data['color']}; border: none;")

            btn_del = QPushButton("-")
            btn_del.setFixedSize(20, 20)
            btn_del.setStyleSheet(
                "QPushButton { background-color: #e74c3c; font-weight: bold; color: white; border-radius: 10px; border: none; text-align: center; padding: 0px 0px 3px 0px; }")
            btn_del.clicked.connect(lambda chk=False, f=fid: self.remove_plot(f))

            b_layout.addWidget(lbl)
            b_layout.addWidget(btn_del)
            self.legend_layout.addWidget(badge)
            badge.mousePressEvent = lambda ev, f=fid: self.select_function(f)

    def select_function(self, fid):
        if fid not in self.active_plots: return
        self.selected_fid = fid
        self.update_legend_ui()
        self.analyze_current_function()

    def analyze_current_function(self):
        data = self.active_plots[self.selected_fid]
        raw_expr = self.clean_expression(data['raw'])
        x_sym = sp.Symbol('x')

        try:
            sp_expr_str = raw_expr.replace("log10(", "sp.log(x, 10)").replace("log(", "sp.log(").replace("exp(",
                                                                                                         "sp.exp(").replace(
                "sqrt(", "sp.sqrt(")
            sp_expr = eval(sp_expr_str, {"sp": sp, "x": x_sym})

            deriv = sp.diff(sp_expr, x_sym)
            deriv_txt = str(deriv).replace("**", "^").replace("sqrt", "√").replace("exp", "e").replace("*", "")

            all_roots = sp.solve(sp_expr, x_sym)
            real_roots = []
            for r in all_roots:
                try:
                    val = complex(r.evalf())
                    if abs(val.imag) < 1e-10:
                        root_val = round(val.real, 4)
                        if abs(root_val) < 1e-10: root_val = 0
                        real_roots.append(root_val)
                except:
                    continue

            roots_str = ", ".join(map(str, sorted(list(set(real_roots))))) if real_roots else "Aucune racine réelle"

        except Exception:
            deriv_txt = "Calcul complexe"
            roots_str = "Indéterminé"

        res_html = f"<b>Fonction :</b> <span style='color:{data['color']};'>{data['pretty']}</span><br>"
        res_html += f"<b>Dérivée :</b> f'(x) = <span style='color:#8e44ad;'>{deriv_txt}</span><br>"
        res_html += f"<b>Racines (f(x)=0) :</b> x ∈ {{ <span style='color:#27ae60;'>{roots_str}</span> }}"
        self.lbl_analysis_results.setText(res_html)

    def remove_plot(self, fid):
        if fid in self.active_plots:
            self.plot_widget.removeItem(self.active_plots[fid]['curve'])
            del self.active_plots[fid]
            if self.selected_fid == fid: self.selected_fid = None
            self.update_legend_ui()

    def load_from_history(self, item):
        raw_text = item.data(Qt.ItemDataRole.UserRole)
        self.func_input.setText(raw_text)
        self.func_input.setFocus()