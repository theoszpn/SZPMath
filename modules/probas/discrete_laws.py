import numpy as np
import io
import base64
import math
import matplotlib.pyplot as plt
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFrame,
                               QLabel, QLineEdit, QPushButton, QTextEdit,
                               QFormLayout, QComboBox, QSlider)
from PySide6.QtCore import Qt


class DiscreteLawsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        self.setStyleSheet("""
            QWidget { color: black; font-family: 'Segoe UI', sans-serif; }
            QLabel { border: none; background: transparent; font-weight: bold; color: #2c3e50; }
            QLineEdit {
                color: black !important;
                background-color: white !important;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                padding: 5px;
                font-weight: bold;
            }
            QComboBox {
                color: black;
                background-color: white;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                padding: 5px;
            }
        """)

        self.control_panel = QFrame()
        self.control_panel.setFixedWidth(340)
        self.control_panel.setStyleSheet(
            "QFrame { background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 8px; }")
        self.cp_layout = QVBoxLayout(self.control_panel)
        self.cp_layout.setContentsMargins(20, 20, 20, 20)
        self.cp_layout.setSpacing(15)
        self.cp_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.cp_layout.addWidget(QLabel("LOI À ÉTUDIER"))
        self.law_selector = QComboBox()
        self.law_selector.addItems(["Binomiale B(n, p)", "Poisson P(λ)", "Bernoulli B(p)", "Géométrique G(p)"])
        self.cp_layout.addWidget(self.law_selector)

        self.formula_box = QFrame()
        self.formula_box.setStyleSheet("background-color: #e8f4f8; border-radius: 6px; border: 1px solid #3498db;")
        self.fb_layout = QVBoxLayout(self.formula_box)
        self.lbl_formula = QLabel("")
        self.lbl_formula.setStyleSheet("color: #1a5276; font-size: 13px;")
        self.lbl_formula.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.fb_layout.addWidget(self.lbl_formula)
        self.cp_layout.addWidget(self.formula_box)

        self.params_form = QFormLayout()
        self.input_n_lam = QLineEdit()
        self.input_p = QLineEdit()
        self.lbl_param1 = QLabel("n :")
        self.lbl_param2 = QLabel("p :")
        self.params_form.addRow(self.lbl_param1, self.input_n_lam)
        self.params_form.addRow(self.lbl_param2, self.input_p)
        self.cp_layout.addLayout(self.params_form)

        self.cp_layout.addWidget(QLabel("TYPE DE PROBABILITÉ"))
        self.mode_selector = QComboBox()
        self.mode_selector.addItems(["P(X = k)", "P(X ≤ k)", "P(X > k)", "P(k₁ ≤ X ≤ k₂)"])
        self.cp_layout.addWidget(self.mode_selector)

        self.inputs_k_layout = QHBoxLayout()
        self.input_k1 = QLineEdit()
        self.input_k1.setPlaceholderText("k ou k₁")
        self.input_k2 = QLineEdit()
        self.input_k2.setPlaceholderText("k₂")
        self.input_k2.setVisible(False)
        self.inputs_k_layout.addWidget(self.input_k1)
        self.inputs_k_layout.addWidget(self.input_k2)
        self.cp_layout.addLayout(self.inputs_k_layout)

        self.cp_layout.addWidget(QLabel("Varier paramètre p"))
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(1, 100)
        self.cp_layout.addWidget(self.slider)

        self.btn_calc = QPushButton("CALCULER L'ANALYSE")
        self.btn_calc.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_calc.setStyleSheet("""
            QPushButton { background-color: #2980b9; color: white; font-weight: bold; padding: 12px; border-radius: 5px; border: none; }
            QPushButton:hover { background-color: #5fb2ed; }
            """)
        self.cp_layout.addWidget(self.btn_calc)

        self.cp_layout.addStretch()

        self.display_area = QFrame()
        self.display_area.setStyleSheet("background-color: white; border: 1px solid #dee2e6; border-radius: 8px;")
        self.display_layout = QVBoxLayout(self.display_area)
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setStyleSheet("border: none; color: black !important; background-color: white;")
        self.display_layout.addWidget(self.log_area)

        self.main_layout.addWidget(self.control_panel)
        self.main_layout.addWidget(self.display_area, 1)

        self.law_selector.currentIndexChanged.connect(self.update_ui_by_law)
        self.mode_selector.currentIndexChanged.connect(self.update_ui_by_mode)
        self.btn_calc.clicked.connect(self.calculate_all)
        self.slider.valueChanged.connect(self.handle_slider)

        self.update_ui_by_law()

    def update_ui_by_law(self):
        law = self.law_selector.currentText()
        if "Binomiale" in law:
            self.lbl_formula.setText("P(X = k) = Cₙᵏ pᵏ (1-p)ⁿ⁻ᵏ")
            self.lbl_param1.setText("n (essais) :")
            self.lbl_param2.setText("p (succès) :")
            self.input_p.setVisible(True)
            self.lbl_param2.setVisible(True)
            self.slider.setRange(0, 100)
        elif "Poisson" in law:
            self.lbl_formula.setText("P(X = k) = (e⁻λ λᵏ) / k!")
            self.lbl_param1.setText("λ (moyenne) :")
            self.input_p.setVisible(False)
            self.lbl_param2.setVisible(False)
            self.slider.setRange(1, 50)
        elif "Bernoulli" in law:
            self.lbl_formula.setText("P(X = k) = pᵏ (1-p)¹⁻ᵏ")
            self.lbl_param1.setText("p (succès) :")
            self.input_p.setVisible(False)
            self.lbl_param2.setVisible(False)
            self.slider.setRange(0, 100)
        elif "Géométrique" in law:
            self.lbl_formula.setText("P(X = k) = (1-p)<sup>k-1</sup> p")
            self.lbl_param1.setText("p (succès) :")
            self.input_p.setVisible(False)
            self.lbl_param2.setVisible(False)
            self.slider.setRange(1, 100)

    def update_ui_by_mode(self):
        self.input_k2.setVisible(self.mode_selector.currentText() == "P(k₁ ≤ X ≤ k₂)")

    def handle_slider(self):
        law = self.law_selector.currentText()
        val = self.slider.value()
        if "Binomiale" in law:
            self.input_p.setText(str(val / 100))
        elif "Poisson" in law:
            self.input_n_lam.setText(str(val))
        elif "Bernoulli" in law:
            self.input_n_lam.setText(str(val / 100))
        elif "Géométrique" in law:
            self.input_n_lam.setText(str(val / 100 if val > 0 else 0.01))
        self.calculate_all()

    def get_pmf(self, k, n, p, lam, law):
        if "Binomiale" in law:
            return math.comb(n, k) * (p ** k) * ((1 - p) ** (n - k)) if 0 <= k <= n else 0
        elif "Poisson" in law:
            return (math.exp(-lam) * (lam ** k)) / math.factorial(k) if k >= 0 else 0
        elif 'Bernoulli' in law:
            return (p ** k) * ((1 - p) ** (1 - k)) if k in [0, 1] else 0
        elif "Géométrique" in law:
            return ((1 - p) ** (k - 1)) * p if k >= 1 else 0

    def calculate_all(self):
        try:
            law = self.law_selector.currentText()
            mode = self.mode_selector.currentText()

            t_n_lam = self.input_n_lam.text()
            t_p = self.input_p.text()

            n = int(t_n_lam if t_n_lam else 0) if "Binomiale" in law else 0

            if "Binomiale" in law:
                p = float(t_p if t_p else 0)
            elif "Bernoulli" in law or "Géométrique" in law:
                p = float(t_n_lam if t_n_lam else 0)
            else:
                p = 0

            lam = float(t_n_lam if t_n_lam else 0) if "Poisson" in law else 0
            k1 = int(self.input_k1.text() if self.input_k1.text() else 0)
            k2 = int(self.input_k2.text() if self.input_k2.text() else 0)

            res, formula_str, method_str, mean, var = 0, "", "", 0, 0

            if "Binomiale" in law:
                mean, var = n * p, n * p * (1 - p)
            elif "Poisson" in law:
                mean, var = lam, lam
            elif "Bernoulli" in law:
                mean, var = p, p * (1 - p)
            elif "Géométrique" in law:
                if p <= 0 or p > 1: raise ValueError("p doit être compris entre 0 (exclu) et 1")
                mean, var = 1 / p, (1 - p) / (p ** 2)

            if mode == "P(X = k)":
                res = self.get_pmf(k1, n, p, lam, law)
                formula_str = f"P(X = {k1})"
                method_str = "Calcul direct de la probabilité ponctuelle."

            elif mode == "P(X ≤ k)":
                if "Géométrique" in law:
                    res = 1 - (1 - p) ** k1
                    formula_str = f"P(X ≤ {k1}) = 1 - (1-p)<sup>{k1}</sup>"
                    method_str = "Utilisation de la fonction de répartition directe."
                else:
                    res = sum(self.get_pmf(i, n, p, lam, law) for i in range(k1 + 1))
                    formula_str = f"P(X ≤ {k1}) = Σ P(X=i) pour i de 0 à {k1}"
                    method_str = "Somme cumulée des probabilités à gauche."

            elif mode == "P(X > k)":
                if "Géométrique" in law:
                    res = (1 - p) ** k1
                    formula_str = f"P(X > {k1}) = (1-p)<sup>{k1}</sup>"
                    method_str = f"Probabilité d'avoir {k1} échecs consécutifs : (1-{p})<sup>{k1}</sup>"
                else:
                    prob_inf = sum(self.get_pmf(i, n, p, lam, law) for i in range(k1 + 1))
                    res = 1 - prob_inf
                    formula_str = f"P(X > {k1}) = 1 - P(X ≤ {k1})"
                    method_str = f"Passage par l'événement contraire : 1 - {prob_inf:.5f}"

            else:  # Intervalle
                res = sum(self.get_pmf(i, n, p, lam, law) for i in range(k1, k2 + 1))
                formula_str = f"P({k1} ≤ X ≤ {k2}) = Σ P(X=i) pour i de {k1} à {k2}"
                method_str = "Somme des probabilités sur l'intervalle spécifié."

            html = f"<div style='color: black;'><h1>Analyse : {law}</h1><hr>"
            html += f"<p><b>Formule adaptée :</b> <span style='color:#2980b9;'>{formula_str}</span></p>"
            html += f"<p><b>Méthode :</b> {method_str}</p>"
            html += f"<p style='background-color:#f1f2f6; padding:10px; font-size:16px;'><b>Résultat : {res:.5f}</b></p>"
            html += f"<p>E(X) = <b>{mean:.2f}</b> | V(X) = <b>{var:.4f}</b></p>"

            fig, ax = plt.subplots(figsize=(6, 3.5))

            if "Binomiale" in law:
                x_limit = n
            elif "Bernoulli" in law:
                x_limit = 1
            elif "Poisson" in law:
                x_limit = int(lam * 3 + 5)
            elif "Géométrique" in law:
                x_limit = int(mean * 2.5 + 5)
            else:
                x_limit = 10

            x = np.arange(0 if "Géométrique" not in law else 1, x_limit + 1)
            y = [self.get_pmf(i, n, p, lam, law) for i in x]

            colors = []
            for val in x:
                is_selected = False
                if mode == "P(X = k)":
                    is_selected = (val == k1)
                elif mode == "P(X ≤ k)":
                    is_selected = (val <= k1)
                elif mode == "P(X > k)":
                    is_selected = (val > k1)
                elif mode == "P(k₁ ≤ X ≤ k₂)":
                    is_selected = (k1 <= val <= k2)
                colors.append('#3498db' if is_selected else '#bdc3c7')

            ax.bar(x, y, color=colors, alpha=0.8, edgecolor='black' if any(colors) else 'none')
            ax.set_title("Distribution et Probabilité calculée")
            ax.set_ylabel("P(X=k)")
            ax.grid(axis='y', linestyle='--', alpha=0.3)

            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
            plt.close(fig)
            b64 = base64.b64encode(buf.getvalue()).decode()
            html += f"<center><img src='data:image/png;base64,{b64}' width='450'></center></div>"
            self.log_area.setHtml(html)

        except Exception as e:
            self.log_area.setHtml(f"<b style='color:red;'>Erreur : {str(e)}</b>")