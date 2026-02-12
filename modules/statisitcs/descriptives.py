import numpy as np
import re
import io
import base64
import matplotlib.pyplot as plt
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFrame,
                               QLabel, QPushButton, QTableWidget, QTableWidgetItem,
                               QHeaderView, QStyledItemDelegate, QLineEdit, QTextEdit)
from PySide6.QtCore import Qt, QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator


class NumericDelegate(QStyledItemDelegate):
    def __init__(self, parent=None, var_type="discrete"):
        super().__init__(parent)
        self.var_type = var_type

    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        if self.var_type == "discrete" or index.column() == 1:
            regex = QRegularExpression(r"^-?[0-9]*[.]?[0-9]*$")
        else:
            regex = QRegularExpression(r"^[\[\];0-9.\-\s]*$")
        editor.setValidator(QRegularExpressionValidator(regex, editor))
        editor.setAlignment(Qt.AlignmentFlag.AlignCenter)
        editor.setStyleSheet(
            "color: black !important; background-color: white !important; font-weight: bold; border: 2px solid #3498db;")
        return editor


class DescriptiveStatsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.variable_type = "discrete"
        self.saved_states = {
            "discrete": {"data": [], "log": ""},
            "continue": {"data": [], "log": ""}
        }
        self.init_ui()

    def init_ui(self):
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        self.control_panel = QFrame()
        self.control_panel.setFixedWidth(340)
        self.control_panel.setStyleSheet("""
            QFrame { background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 8px; }
            QLabel { border: none; font-weight: bold; color: #2c3e50; }
        """)
        self.cp_layout = QVBoxLayout(self.control_panel)
        self.cp_layout.setContentsMargins(20, 20, 20, 20)
        self.cp_layout.setSpacing(12)
        self.cp_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        title = QLabel("CONFIGURATION DES DONNÉES")
        title.setStyleSheet("font-size: 15px; margin-bottom: 5px; color: #1a5276;")
        self.cp_layout.addWidget(title)

        self.cp_layout.addWidget(QLabel("Type de variable :"))
        self.toggle_layout = QHBoxLayout()
        self.btn_discrete = self.create_toggle_button("Discrète", True)
        self.btn_continue = self.create_toggle_button("Continue", False)
        self.btn_discrete.clicked.connect(lambda: self.set_var_type("discrete"))
        self.btn_continue.clicked.connect(lambda: self.set_var_type("continue"))
        self.toggle_layout.addWidget(self.btn_discrete)
        self.toggle_layout.addWidget(self.btn_continue)
        self.cp_layout.addLayout(self.toggle_layout)

        self.data_table = QTableWidget(10, 2)
        self.setup_table()
        self.cp_layout.addWidget(self.data_table)

        self.row_controls = QHBoxLayout()
        self.btn_add = QPushButton("+ Ligne")
        self.btn_del = QPushButton("- Ligne")
        btn_style = """QPushButton { background-color: #34495e; color: white; font-weight: bold; padding: 6px; border-radius: 4px; border: none; }
                       QPushButton:hover { background-color: #415a73; }
                    """
        self.btn_add.setStyleSheet(btn_style)
        self.btn_del.setStyleSheet(btn_style)
        self.btn_add.clicked.connect(self.add_row)
        self.btn_del.clicked.connect(self.remove_row)
        self.row_controls.addWidget(self.btn_add)
        self.row_controls.addWidget(self.btn_del)
        self.cp_layout.addLayout(self.row_controls)

        self.cp_layout.addSpacing(15)
        self.btn_tendance = self.create_action_button("Paramètres de tendance centrale", "#2980b9")
        self.btn_tendance.clicked.connect(self.calculate_central_tendency)
        self.cp_layout.addWidget(self.btn_tendance)

        self.btn_dispersion = self.create_action_button("Paramètres de dispersion", "#27ae60")
        self.btn_dispersion.clicked.connect(self.calculate_dispersion)
        self.cp_layout.addWidget(self.btn_dispersion)

        self.btn_forme = self.create_action_button("Paramètres de forme", "#e67e22")
        self.btn_forme.clicked.connect(self.calculate_shape)
        self.cp_layout.addWidget(self.btn_forme)

        self.btn_graphs = self.create_action_button("Générer les Graphiques", "#8e44ad")
        self.btn_graphs.clicked.connect(self.calculate_graphs)
        self.cp_layout.addWidget(self.btn_graphs)

        self.cp_layout.addStretch()

        self.display_area = QFrame()
        self.display_area.setStyleSheet("background-color: white; border: 1px solid #dee2e6; border-radius: 8px;")
        self.display_layout = QVBoxLayout(self.display_area)
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setStyleSheet(
            "border: none; font-family: 'Segoe UI', sans-serif; font-size: 14px; color: black !important; background-color: white;")
        self.display_layout.addWidget(self.log_area)

        self.main_layout.addWidget(self.control_panel)
        self.main_layout.addWidget(self.display_area, 1)
        self.data_table.itemChanged.connect(self.handle_table_input)

    def create_toggle_button(self, text, active):
        btn = QPushButton(text)
        btn.setCheckable(True)
        btn.setMinimumHeight(35)
        self.update_button_style(btn, active)
        return btn

    def create_action_button(self, text, color):
        btn = QPushButton(text)
        btn.setStyleSheet(
            """QPushButton { background-color: #1665b5; color: white; font-weight: bold; padding: 10px; border-radius: 5px; font-size: 13px; margin-top: 5px; }
               QPushButton:hover { background-color: #2d82d6; }
            """)
        return btn

    def update_button_style(self, btn, active):
        style = "background-color: #3498db; color: white; font-weight: bold; border-radius: 4px; border: none; padding: 2px 10px;" if active else \
            "background-color: #ecf0f1; color: #7f8c8d; border: 1px solid #bdc3c7; border-radius: 4px; padding: 2px 10px;"
        btn.setStyleSheet(style)
        btn.setChecked(active)

    def set_var_type(self, vtype):
        if self.variable_type == vtype: return
        current_data = []
        for r in range(self.data_table.rowCount()):
            xi = self.data_table.item(r, 0).text() if self.data_table.item(r, 0) else ""
            ni = self.data_table.item(r, 1).text() if self.data_table.item(r, 1) else "0"
            current_data.append((xi, ni))
        self.saved_states[self.variable_type] = {"data": current_data, "log": self.log_area.toHtml()}

        self.variable_type = vtype
        self.update_button_style(self.btn_discrete, vtype == "discrete")
        self.update_button_style(self.btn_continue, vtype == "continue")
        h_x = "xᵢ" if vtype == "discrete" else "[aᵢ ; bᵢ["
        self.data_table.setHorizontalHeaderLabels([h_x, "nᵢ"])
        self.data_table.setItemDelegate(NumericDelegate(self, vtype))

        state = self.saved_states[vtype]
        self.data_table.blockSignals(True)
        if state["data"]:
            self.data_table.setRowCount(len(state["data"]))
            for r, (xi, ni) in enumerate(state["data"]):
                self.data_table.setItem(r, 0, QTableWidgetItem(xi))
                it_n = QTableWidgetItem(ni)
                it_n.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.data_table.setItem(r, 1, it_n)
        else:
            self.data_table.setRowCount(10)
            for r in range(10):
                self.data_table.setItem(r, 0, QTableWidgetItem("[  ;  [" if vtype == "continue" else ""))
                it_n = QTableWidgetItem("0")
                it_n.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.data_table.setItem(r, 1, it_n)
        self.log_area.setHtml(state["log"])
        self.data_table.blockSignals(False)

    def setup_table(self):
        self.data_table.setHorizontalHeaderLabels(["xᵢ", "nᵢ"])
        self.data_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.data_table.verticalHeader().setVisible(False)
        self.data_table.setStyleSheet("""
                                QTableWidget {
                                    background-color: white;
                                    color: black !important;
                                }
                                QTableWidget QLineEdit {
                                    background-color: white;
                                    color: black;
                                    border: none;
                                }
                                """)

        self.data_table.horizontalHeader().setStyleSheet(
            "QHeaderView::section { background-color: #f8f9fa; color: black !important; font-weight: bold; border: 1px solid #dee2e6; }")
        for r in range(10):
            self.data_table.setItem(r, 0, QTableWidgetItem(""))
            it_n = QTableWidgetItem("0")
            it_n.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.data_table.setItem(r, 1, it_n)

    def handle_table_input(self, item):
        if self.variable_type != "continue" or item.column() != 0: return
        text = item.text().strip()
        if text in ["", "[  ;  ["]: return
        nums = re.findall(r"[-+]?\d*\.\d+|\d+", text)
        self.data_table.blockSignals(True)
        if len(nums) >= 2:
            item.setText(f"[{nums[0]} ; {nums[1]}[")
        elif len(nums) == 1:
            item.setText(f"[{nums[0]} ;  [")
        self.data_table.blockSignals(False)

    def add_row(self):
        r = self.data_table.rowCount()
        self.data_table.insertRow(r)
        self.data_table.setItem(r, 0, QTableWidgetItem("[  ;  [" if self.variable_type == "continue" else ""))
        it_n = QTableWidgetItem("0")
        it_n.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.data_table.setItem(r, 1, it_n)

    def remove_row(self):
        if self.data_table.rowCount() > 1:
            curr = self.data_table.currentRow()
            self.data_table.removeRow(curr if curr != -1 else self.data_table.rowCount() - 1)

    def get_valid_data(self):
        data = []
        for r in range(self.data_table.rowCount()):
            it_x, it_n = self.data_table.item(r, 0).text().strip(), self.data_table.item(r, 1).text().strip()
            if not it_x or it_x == "[  ;  [" or not it_n: continue
            try:
                ni = float(it_n)
                if ni <= 0: continue
                if self.variable_type == "discrete":
                    data.append({'val': float(it_x), 'ni': ni})
                else:
                    nums = re.findall(r"[-+]?\d*\.\d+|\d+", it_x)
                    if len(nums) >= 2:
                        a, b = float(nums[0]), float(nums[1])
                        data.append({'a': a, 'b': b, 'val': (a + b) / 2, 'ni': ni})
            except:
                continue
        if data: data.sort(key=lambda x: x['val'] if self.variable_type == 'discrete' else x['a'])
        return data

    def calculate_central_tendency(self):
        data = self.get_valid_data()
        if not data: return
        N = sum(d['ni'] for d in data)
        html = "<div style='color: black;'>"
        html += "<h1 style='color:#1a5276; text-align:center;'>TENDANCE CENTRALE</h1><hr>"

        mean = sum(d['val'] * d['ni'] for d in data) / N
        detail = " + ".join([f"({d['ni']}×{d['val']})" for d in data])
        html += "<h2>1. Moyenne (x̄)</h2><p>La moyenne représente la valeur centrale théorique de la distribution.</p>"
        html += f"<p><b>Formule :</b> x̄ = (Σ nᵢxᵢ) / N</p>"
        html += f"<p style='background-color:#f1f2f6; padding:8px;'><b>Calcul :</b> ({detail}) / {N}</p>"
        html += f"<p><b>Résultat :</b> x̄ = <b>{mean:.2f}</b></p><hr>"

        max_ni = max(d['ni'] for d in data)
        modes = [d for d in data if d['ni'] == max_ni]
        mode_str = ", ".join(
            [str(m['val']) if self.variable_type == "discrete" else f"[{m['a']}; {m['b']}[" for m in modes])
        html += "<h2>2. Mode (Mₒ)</h2><p>Le mode est la valeur (ou classe) la plus fréquente.</p>"
        html += f"<p><b>Identification :</b> Effectif maximal nᵢ = {max_ni}.</p>"
        html += f"<p><b>Résultat :</b> Mₒ = <b>{mode_str}</b></p><hr>"

        target = N / 2
        html += f"<h2>3. Médiane (Mₑ)</h2><p>La médiane divise l'échantillon en deux parties égales (Rang = {target}).</p>"
        ecc = 0
        if self.variable_type == "discrete":
            for d in data:
                ecc += d['ni']
                if ecc >= target: res_me = d['val']; break
            html += f"<p>Le premier ECC ≥ {target} est {ecc}, correspondant à xᵢ = {res_me}.</p>"
        else:
            prev_ecc = 0
            for d in data:
                ecc += d['ni']
                if ecc >= target:
                    h = d['b'] - d['a']
                    res_me = d['a'] + ((target - prev_ecc) / d['ni']) * h
                    html += f"<p style='color:#d35400;'><b>Étape 1 :</b> Classe médiane [{d['a']}; {d['b']}[ (ECC={ecc} ≥ {target})</p>"
                    html += "<p><b>Étape 2 :</b> Interpolation : Mₑ = L_inf + [(N/2 - ECC_prec)/nᵢ] × h</p>"
                    html += f"<p style='background-color:#f1f2f6; padding:8px;'><b>Calcul :</b> {d['a']} + [({target}-{prev_ecc})/{d['ni']}] × {h}</p>"
                    break
                prev_ecc = ecc
        html += f"<p><b>Résultat :</b> Mₑ = <b>{res_me:.2f}</b></p></div>"
        self.log_area.setHtml(html)

    def calculate_dispersion(self):
        data = self.get_valid_data()
        if not data: return
        N = sum(d['ni'] for d in data)
        mean = sum(d['val'] * d['ni'] for d in data) / N
        html = "<div style='color: black;'>"
        html += "<h1 style='color:#27ae60; text-align:center;'>ANALYSE DE LA DISPERSION</h1><hr>"

        v_min = data[0]['val'] if self.variable_type == "discrete" else data[0]['a']
        v_max = data[-1]['val'] if self.variable_type == "discrete" else data[-1]['b']
        html += f"<h2>1. Étendue (E)</h2><p>Mesure l'écart total (Max - Min): {v_max} - {v_min} = <b>{v_max - v_min}</b></p><hr>"

        html += "<h2>2. Quartiles</h2>"
        qs = {}
        for k, lbl in [(1, "Q₁"), (3, "Q₃")]:
            target, ecc, prev_ecc = (k * N) / 4, 0, 0
            for d in data:
                ecc += d['ni']
                if ecc >= target:
                    qs[lbl] = d['val'] if self.variable_type == "discrete" else d['a'] + (
                            (target - prev_ecc) / d['ni']) * (d['b'] - d['a'])
                    break
                prev_ecc = ecc
            html += f"<p><b>{lbl} :</b> Rang {k}N/4 = {target} → <b>{qs[lbl]:.2f}</b></p>"
        iqr = qs["Q₃"] - qs["Q₁"]
        html += f"<p><b>IQR (Q₃ - Q₁) :</b> <b>{iqr:.2f}</b></p><hr>"

        lb = qs["Q₁"] - 1.5 * iqr
        ub = qs["Q₃"] + 1.5 * iqr
        outliers = [d['val'] for d in data if d['val'] < lb or d['val'] > ub]

        html += "<h2>3. Identification des valeurs aberrantes</h2>"
        html += "<p>On utilise la règle des barrières d'interquartile pour détecter les valeurs atypiques.</p>"
        html += f"<p><b>Barrière Inférieure :</b> Q₁ - 1.5 × IQR = <b>{lb:.2f}</b></p>"
        html += f"<p><b>Barrière Supérieure :</b> Q₃ + 1.5 × IQR = <b>{ub:.2f}</b></p>"
        if outliers:
            html += f"<p style='color:#e74c3c;'><b>Valeurs aberrantes détectées :</b> {', '.join(map(str, sorted(list(set(outliers)))))}</p><hr>"
        else:
            html += "<p><b>Aucune valeur aberrante détectée.</b></p><hr>"

        sum_sq = sum(d['ni'] * (d['val'] ** 2) for d in data)
        vx = (sum_sq / N) - (mean ** 2)
        std = np.sqrt(vx)
        html += "<h2>4. Variance V(X) et Écart-type σ</h2>"
        html += "<p><b>Formule Koenig :</b> V(X) = [ (Σ nᵢxᵢ²) / N ] - x̄²</p>"
        html += f"<p style='background-color:#f1f2f6; padding:8px;'><b>Calcul :</b> ({sum_sq:.2f}/{N}) - {mean:.2f}²</p>"
        html += f"<p><b>V(X) = {vx:.4f}</b> | <b>σ = {std:.4f}</b></p><hr>"

        html += "<h2>5. Dispersion Relative</h2>"
        cv = (std / mean * 100)
        cq_rel = iqr / (qs["Q₃"] + qs["Q₁"])
        ema = sum(d['ni'] * abs(d['val'] - mean) for d in data) / N
        html += f"<p><b>CV :</b> {cv:.2f}% | <b>Coeff. Interquartile Rel :</b> {cq_rel:.4f} | <b>Écart Moyen Rel :</b> {ema / mean:.4f}</p></div>"
        self.log_area.setHtml(html)

    def calculate_shape(self):
        self.log_area.clear()
        data = self.get_valid_data()
        if not data: return
        N = sum(d['ni'] for d in data)
        mean = sum(d['val'] * d['ni'] for d in data) / N
        variance = (sum(d['ni'] * (d['val'] ** 2) for d in data) / N) - (mean ** 2)
        std = np.sqrt(variance)

        html = "<div style='color: black;'>"
        html += "<h1 style='color:#d35400; text-align:center;'>ANALYSE DE LA FORME</h1><hr>"

        m3 = sum(d['ni'] * ((d['val'] - mean) ** 3) for d in data) / N
        skewness = m3 / (std ** 3) if std != 0 else 0
        html += "<h2>1. Skewness (Asymétrie)</h2>"

        html += "<p>Le Skewness mesure si la distribution est décalée à gauche ou à droite par rapport à sa moyenne.</p>"
        html += "<p><b>Formule :</b> S = [ Σ n<sub>i</sub>(x<sub>i</sub> - x̄)³ / N ] / σ³</p>"
        html += f"<p style='background-color:#f1f2f6; padding:8px;'><b>Calcul :</b> m₃ = {m3:.4f} | σ³ = {std ** 3:.4f}</p>"
        interp_skew = "Distribution symétrique" if abs(skewness) < 0.1 else \
            "Asymétrie positive (étalée vers la droite)" if skewness > 0 else "Asymétrie négative (étalée vers la gauche)"
        html += f"<p><b>Résultat :</b> Skewness = <b>{skewness:.4f}</b> ({interp_skew})</p><hr>"

        m4 = sum(d['ni'] * ((d['val'] - mean) ** 4) for d in data) / N
        kurtosis = (m4 / (std ** 4)) - 3 if std != 0 else 0
        html += "<h2>2. Kurtosis (Aplatissement)</h2>"
        html += "<p>Le Kurtosis mesure si la distribution est pointue ou aplatie par rapport à une cloche normale.</p>"
        html += "<p><b>Formule :</b> K = [ Σ n<sub>i</sub>(x<sub>i</sub> - x̄)⁴ / N ] / σ⁴ - 3</p>"
        html += f"<p style='background-color:#f1f2f6; padding:8px;'><b>Calcul :</b> m₄ = {m4:.4f} | σ⁴ = {std ** 4:.4f}</p>"
        interp_kurt = "Mésokurtique (Normal)" if abs(kurtosis) < 0.1 else \
            "Leptokurtique (Pointu / Fins)" if kurtosis > 0 else "Platykurtique (Aplati / Épais)"
        html += f"<p><b>Résultat :</b> Kurtosis = <b>{kurtosis:.4f}</b> ({interp_kurt})</p><hr>"

        html += "<h2>3. Comparaison à la Loi Normale</h2>"
        fig, ax = plt.subplots(figsize=(7, 4))
        x_vals = [d['val'] for d in data]
        y_vals = [d['ni'] / N for d in data]
        if self.variable_type == "discrete":
            ax.bar(x_vals, y_vals, color='#2c58db', alpha=0.8, label='Données')
        else:
            for d in data:
                ax.bar(d['a'], d['ni'] / N, width=(d['b'] - d['a']), align='edge', color='#e67e22', alpha=0.4,
                       edgecolor='white')
        x_norm = np.linspace(min(x_vals) - std, max(x_vals) + std, 100)
        y_norm = (1 / (std * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x_norm - mean) / std) ** 2)
        y_norm = y_norm * (max(y_vals) / max(y_norm))
        ax.plot(x_norm, y_norm, color='#2c3e50', linestyle='--', label='Référence Normale')
        ax.set_title("Forme de la distribution", fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.2)
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
        plt.close(fig)
        b64 = base64.b64encode(buf.getvalue()).decode()
        html += f"<div style='text-align:center;'><img src='data:image/png;base64,{b64}' width='500'></div></div>"
        self.log_area.setHtml(html)

    def calculate_graphs(self):
        data = self.get_valid_data()
        if not data: return
        N = sum(d['ni'] for d in data)

        sb = {}
        for k, lbl in [(1, "q1"), (2, "med"), (3, "q3")]:
            target, ecc, prev_ecc = (k * N) / 4, 0, 0
            for d in data:
                ecc += d['ni']
                if ecc >= target:
                    sb[lbl] = d['val'] if self.variable_type == 'discrete' else d['a'] + (
                                (target - prev_ecc) / d['ni']) * (d['b'] - d['a'])
                    break
                prev_ecc = ecc

        iqr = sb["q3"] - sb["q1"]
        lb = sb["q1"] - 1.5 * iqr
        ub = sb["q3"] + 1.5 * iqr

        fliers = [d['val'] for d in data if d['val'] < lb or d['val'] > ub]
        valid_vals = [d['val'] for d in data if d['val'] >= lb and d['val'] <= ub]
        whis_lo = min(valid_vals) if valid_vals else sb["q1"]
        whis_hi = max(valid_vals) if valid_vals else sb["q3"]

        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(8, 12), gridspec_kw={'height_ratios': [1, 1, 0.5]})
        plt.subplots_adjust(hspace=0.4)

        if self.variable_type == "discrete":
            ax1.bar([d['val'] for d in data], [d['ni'] for d in data], color='#3498db', alpha=0.7, width=0.2)
            ax1.set_title("Diagramme en bâtons", fontweight='bold')
        else:
            for d in data: ax1.bar(d['a'], d['ni'], width=(d['b'] - d['a']), align='edge', color='#3498db', alpha=0.6,
                                   edgecolor='white')
            ax1.set_title("Histogramme", fontweight='bold')

        ecc, x_pts, y_pts = 0, [], []
        if self.variable_type == "discrete":
            for d in data:
                ecc += d['ni']
                x_pts.append(d['val'])
                y_pts.append((ecc / N) * 100)
        else:
            x_pts.append(data[0]['a'])
            y_pts.append(0)
            for d in data:
                ecc += d['ni']
                x_pts.append(d['b'])
                y_pts.append((ecc / N) * 100)
        ax2.plot(x_pts, y_pts, marker='o', linestyle='-', color='#e67e22', lw=2)
        ax2.set_title("Courbe des fréquences cumulées (%)", fontweight='bold')
        ax2.set_ylim(-5, 105)
        ax2.grid(True, alpha=0.3)

        ax3.bxp([{'med': sb['med'], 'q1': sb['q1'], 'q3': sb['q3'], 'whislo': whis_lo, 'whishi': whis_hi,
                  'fliers': fliers}],
                vert=False, patch_artist=True,
                boxprops=dict(facecolor='#2ecc71', alpha=0.7),
                medianprops=dict(color='white', lw=2),
                flierprops=dict(marker='o', markerfacecolor='#e74c3c', markersize=8, linestyle='none'))
        ax3.set_title("Boxplot (Moustaches aux valeurs non-aberrantes)", fontweight='bold')
        ax3.set_yticklabels([])
        ax3.grid(axis='x', alpha=0.3)

        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
        plt.close(fig)
        b64 = base64.b64encode(buf.getvalue()).decode()
        self.log_area.setHtml(
            f"<div style='color: black; text-align:center;'><h1>VISUALISATION</h1><hr><img src='data:image/png;base64,{b64}' width='500'></div>")