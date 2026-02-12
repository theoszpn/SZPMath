import numpy as np
import io
import base64
from scipy import stats
import matplotlib.pyplot as plt
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFrame,
                               QLabel, QLineEdit, QPushButton, QTextEdit,
                               QFormLayout, QComboBox, QSlider)
from PySide6.QtCore import Qt


class ContinuousLawsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        self.setStyleSheet("""
            QWidget { 
                color: black; 
                font-family: 'Segoe UI', sans-serif; 
            }
            QLabel { 
                border: none !important; 
                background: transparent; 
                font-weight: bold; 
                color: #2c3e50;
                padding: 2px;
            }
            QLineEdit {
                color: black !important;
                background-color: white !important;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                padding: 5px;
            }
            QComboBox {
                color: black;
                background-color: white;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                padding: 5px;
            }
            QFrame#ControlSubFrame {
                border: none;
                background: transparent;
            }
        """)

        self.control_panel = QFrame()
        self.control_panel.setFixedWidth(340)
        self.control_panel.setStyleSheet(
            "QFrame { background-color: #f8f9fa; border: none; border-radius: 8px; }")
        self.cp_layout = QVBoxLayout(self.control_panel)
        self.cp_layout.setContentsMargins(20, 20, 20, 20)
        self.cp_layout.setSpacing(12)
        self.cp_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.cp_layout.addWidget(QLabel("LOI CONTINUE"))
        self.law_selector = QComboBox()
        self.law_selector.addItems(["Normale N(μ, σ)", "Exponentielle E(λ)", "Uniforme U(a, b)"])
        self.cp_layout.addWidget(self.law_selector)

        self.formula_box = QFrame()
        self.formula_box.setObjectName("ControlSubFrame")
        self.formula_box.setStyleSheet("background-color: #f4ecf7; border-radius: 6px; border: 1px solid #8e44ad;")
        self.fb_layout = QVBoxLayout(self.formula_box)
        self.lbl_formula = QLabel("")
        self.lbl_formula.setStyleSheet("color: #4a235a; font-size: 13px; font-weight: normal; border: none;")
        self.lbl_formula.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.fb_layout.addWidget(self.lbl_formula)
        self.cp_layout.addWidget(self.formula_box)

        self.params_form = QFormLayout()
        self.params_form.setSpacing(10)
        self.input_p1 = QLineEdit("0")
        self.input_p2 = QLineEdit("1")
        self.lbl_p1 = QLabel("μ :")
        self.lbl_p2 = QLabel("σ :")
        self.params_form.addRow(self.lbl_p1, self.input_p1)
        self.params_form.addRow(self.lbl_p2, self.input_p2)
        self.cp_layout.addLayout(self.params_form)

        self.cp_layout.addSpacing(10)
        self.cp_layout.addWidget(QLabel("INTERVALLE (AIRE)"))
        self.mode_selector = QComboBox()
        self.mode_selector.addItems(["P(X < k)", "P(X > k)", "P(k₁ < X < k₂)"])
        self.cp_layout.addWidget(self.mode_selector)

        self.k_inputs = QFrame()
        self.k_inputs.setObjectName("ControlSubFrame")
        self.k_layout = QHBoxLayout(self.k_inputs)
        self.k_layout.setContentsMargins(0, 0, 0, 0)
        self.input_k1 = QLineEdit("0")
        self.input_k1.setPlaceholderText("k₁")
        self.input_k2 = QLineEdit()
        self.input_k2.setPlaceholderText("k₂")
        self.input_k2.setVisible(False)
        self.k_layout.addWidget(self.input_k1)
        self.k_layout.addWidget(self.input_k2)
        self.cp_layout.addWidget(self.k_inputs)

        self.cp_layout.addSpacing(10)
        self.cp_layout.addWidget(QLabel("DÉPLACER k (Visualisation)"))
        self.slider_k = QSlider(Qt.Orientation.Horizontal)
        self.slider_k.setStyleSheet("color: #82cbff;")
        self.slider_k.setRange(0, 1000)
        self.cp_layout.addWidget(self.slider_k)

        self.btn_calc = QPushButton("CALCULER L'AIRE")
        self.btn_calc.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_calc.setStyleSheet("""
            QPushButton { background-color: #8e44ad; color: white; font-weight: bold; padding: 12px; border-radius: 5px; border: none; }
            QPushButton:hover { background-color: #9b59b6; }
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

        self.law_selector.currentIndexChanged.connect(self.update_ui)
        self.mode_selector.currentIndexChanged.connect(self.update_ui)
        self.btn_calc.clicked.connect(self.calculate_all)
        self.slider_k.valueChanged.connect(self.sync_k_from_slider)

        self.update_ui()

    def update_ui(self):
        law = self.law_selector.currentText()
        self.input_k2.setVisible(self.mode_selector.currentText() == "P(k₁ < X < k₂)")
        if "Normale" in law:
            self.lbl_formula.setText("f(x) = (1 / σ√2π) e<sup>-1/2((x-μ)/σ)²</sup>")
            self.lbl_p1.setText("μ (Moyenne) :")
            self.lbl_p2.setText("σ (Écart-type) :")
            self.input_p2.setVisible(True)
            self.lbl_p2.setVisible(True)
        elif "Exponentielle" in law:
            self.lbl_formula.setText("f(x) = λ e<sup>-λx</sup>  (x ≥ 0)")
            self.lbl_p1.setText("λ (Taux) :")
            self.input_p2.setVisible(False)
            self.lbl_p2.setVisible(False)
        else:
            self.lbl_formula.setText("f(x) = 1 / (b - a)  (a ≤ x ≤ b)")
            self.lbl_p1.setText("a (Borne Inf) :")
            self.lbl_p2.setText("b (Borne Sup) :")
            self.input_p2.setVisible(True)
            self.lbl_p2.setVisible(True)

    def sync_k_from_slider(self):
        """Calcule une valeur de k cohérente selon la loi actuelle."""
        try:
            val = self.slider_k.value() / 1000.0  # Ratio 0 à 1
            law = self.law_selector.currentText()
            p1 = float(self.input_p1.text())
            p2 = float(self.input_p2.text())

            if "Normale" in law:
                k_val = p1 + (val - 0.5) * (8 * p2)
            elif "Exponentielle" in law:
                k_val = val * (5 / p1) if p1 > 0 else val * 10
            elif "Uniforme" in law:
                k_val = p1 + val * (p2 - p1)

            self.input_k1.setText(f"{k_val:.3f}")
            self.calculate_all()
        except:
            pass

    def calculate_all(self):
        try:
            law = self.law_selector.currentText()
            mode = self.mode_selector.currentText()
            p1 = float(self.input_p1.text() if self.input_p1.text() else 0)
            p2 = float(self.input_p2.text() if self.input_p2.text() else 1)
            k1 = float(self.input_k1.text() if self.input_k1.text() else 0)
            k2 = float(self.input_k2.text() if self.input_k2.text() else 0)

            if "Normale" in law:
                dist = stats.norm(loc=p1, scale=p2)
                x = np.linspace(p1 - 4 * p2, p1 + 4 * p2, 500)
            elif "Exponentielle" in law:
                dist = stats.expon(scale=1 / p1)
                x = np.linspace(0, dist.ppf(0.999), 500)
            elif "Uniforme" in law:
                dist = stats.uniform(loc=p1, scale=p2 - p1)
                x = np.linspace(p1 - 0.5, p2 + 0.5, 500)

            mean, var = dist.stats(moments='mv')

            if mode == "P(X < k)":
                res = dist.cdf(k1)
                formula_str = f"P(X < {k1:.3f})"
                method = "Calcul de l'intégrale de -∞ à k (CDF)."
            elif mode == "P(X > k)":
                res = dist.sf(k1)
                formula_str = f"P(X > {k1:.3f}) = 1 - P(X < {k1:.3f})"
                method = "Calcul de l'intégrale de k à +∞ (Survival Function)."
            else:
                res = dist.cdf(k2) - dist.cdf(k1)
                formula_str = f"P({k1:.3f} < X < {k2:.3f}) = F({k2:.3f}) - F({k1:.3f})"
                method = "Différence des probabilités cumulées."

            html = "<div style='color: black;'>"
            html += f"<h1 style='color:#8e44ad; text-align:center;'>ANALYSE CONTINUE : {law}</h1><hr>"
            html += f"<p><b>Probabilité :</b> <span style='color:#2980b9;'>{formula_str}</span></p>"
            html += f"<p><b>Méthode :</b> {method}</p>"
            html += f"<p style='background-color:#f4ecf7; padding:10px; font-size:16px;'><b>Résultat : {res:.5f}</b></p>"
            html += f"<p>Espérance E(X) = <b>{float(mean):.3f}</b> | Variance V(X) = <b>{float(var):.4f}</b></p>"

            fig, ax = plt.subplots(figsize=(6, 3.5))
            y = dist.pdf(x)
            ax.plot(x, y, color='#8e44ad', lw=2)

            if mode == "P(X < k)":
                ax.fill_between(x, y, where=(x < k1), color='#8e44ad', alpha=0.3)
            elif mode == "P(X > k)":
                ax.fill_between(x, y, where=(x > k1), color='#8e44ad', alpha=0.3)
            else:
                ax.fill_between(x, y, where=((x >= k1) & (x <= k2)), color='#8e44ad', alpha=0.3)

            ax.set_title("Aire sous la courbe de densité", fontweight='bold')
            ax.set_ylabel("f(x)")
            ax.grid(True, alpha=0.2)

            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
            plt.close(fig)
            b64 = base64.b64encode(buf.getvalue()).decode()
            html += f"<center><img src='data:image/png;base64,{b64}' width='450'></center></div>"

            self.log_area.setHtml(html)
        except Exception as e:
            self.log_area.setHtml(f"<b style='color:red;'>Paramètres invalides : {str(e)}</b>")