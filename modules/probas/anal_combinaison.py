import math
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFrame,
                               QLabel, QLineEdit, QPushButton, QTextEdit, QFormLayout)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIntValidator


class CombinatoricsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        self.control_panel = QFrame()
        self.control_panel.setFixedWidth(340)
        self.control_panel.setStyleSheet("""
            QFrame { background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 8px; }
            QLabel { color: #2c3e50; font-weight: bold; }
        """)
        self.cp_layout = QVBoxLayout(self.control_panel)
        self.cp_layout.setContentsMargins(20, 20, 20, 20)
        self.cp_layout.setSpacing(15)
        self.cp_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        title = QLabel("ANALYSE COMBINATOIRE")
        title.setStyleSheet("font-size: 18px; color: #1a5276; margin-bottom: 10px; border: 0px solid;")
        self.cp_layout.addWidget(title)

        self.form = QFormLayout()
        input_style = "color: black !important; background-color: white !important; font-weight: bold; border: 1px solid #bdc3c7; padding: 5px;"

        self.input_n = QLineEdit()
        self.input_n.setValidator(QIntValidator(0, 1000))
        self.input_n.setStyleSheet(input_style)
        self.input_n.setPlaceholderText("Nombre total (n)")

        self.input_k = QLineEdit()
        self.input_k.setValidator(QIntValidator(0, 1000))
        self.input_k.setStyleSheet(input_style)
        self.input_k.setPlaceholderText("Nombre choisi (k)")

        self.form.addRow("Taille n :", self.input_n)
        self.form.addRow("Choix k :", self.input_k)
        self.cp_layout.addLayout(self.form)

        self.btn_fact = self.create_action_btn("Factorielle (n!)", "#34495e")
        self.btn_arr = self.create_action_btn("Arrangements (An,k)", "#2980b9")
        self.btn_comb = self.create_action_btn("Combinaisons (Cn,k)", "#27ae60")

        self.cp_layout.addWidget(self.btn_fact)
        self.cp_layout.addWidget(self.btn_arr)
        self.cp_layout.addWidget(self.btn_comb)

        self.cp_layout.addStretch()

        self.display_area = QFrame()
        self.display_area.setStyleSheet("background-color: white; border: 1px solid #dee2e6; border-radius: 8px;")
        self.display_layout = QVBoxLayout(self.display_area)

        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setStyleSheet("border: none; font-family: 'Segoe UI'; font-size: 14px; color: black !important;")
        self.display_layout.addWidget(self.log_area)

        self.main_layout.addWidget(self.control_panel)
        self.main_layout.addWidget(self.display_area, 1)

        self.btn_fact.clicked.connect(self.calculate_factorial)
        self.btn_arr.clicked.connect(self.calculate_arrangement)
        self.btn_comb.clicked.connect(self.calculate_combination)

    def create_action_btn(self, text, color):
        btn = QPushButton(text)
        btn.setStyleSheet(
            f"background-color: {color}; color: white; font-weight: bold; padding: 10px; border-radius: 5px;")
        return btn

    def get_params(self):
        try:
            n = int(self.input_n.text() if self.input_n.text() else 0)
            k = int(self.input_k.text() if self.input_k.text() else 0)
            return n, k
        except:
            return 0, 0

    def calculate_factorial(self):
        n, _ = self.get_params()
        res = math.factorial(n)
        html = "<div style='color: black;'>"
        html += f"<h2>Factorielle (n!)</h2><hr>"
        html += f"<p>Le nombre de permutations de {n} éléments est le produit de tous les entiers de 1 à n.</p>"
        html += f"<p><b>Formule :</b> n! = 1 × 2 × ... × n</p>"
        html += f"<p style='background-color:#f1f2f6; padding:8px;'><b>Résultat :</b> {n}! = <b>{res}</b></p></div>"
        self.log_area.setHtml(html)

    def calculate_arrangement(self):
        n, k = self.get_params()
        if k > n:
            self.log_area.setHtml("<b style='color:red;'>Erreur : k ne peut être supérieur à n.</b>")
            return
        res = math.perm(n, k)
        html = "<div style='color: black;'>"
        html += f"<h2>Arrangements (A<sub>n</sub><sup>k</sup>)</h2><hr>"
        html += f"<p>Nombre de tirages de {k} éléments parmi {n} <b>en tenant compte de l'ordre</b> et sans remise.</p>"
        html += f"<p><b>Formule :</b> A<sub>n</sub><sup>k</sup> = n! / (n - k)!</p>"
        html += f"<p style='background-color:#f1f2f6; padding:8px;'><b>Résultat :</b> A({n},{k}) = <b>{res}</b></p></div>"
        self.log_area.setHtml(html)

    def calculate_combination(self):
        n, k = self.get_params()
        if k > n:
            self.log_area.setHtml("<b style='color:red;'>Erreur : k ne peut être supérieur à n.</b>")
            return
        res = math.comb(n, k)
        html = "<div style='color: black;'>"
        html += f"<h2>Combinaisons (C<sub>n</sub><sup>k</sup>)</h2><hr>"
        html += f"<p>Nombre de tirages de {k} éléments parmi {n} <b>sans tenir compte de l'ordre</b> et sans remise.</p>"
        html += f"<p><b>Formule :</b> C<sub>n</sub><sup>k</sup> = n! / [k! × (n - k)!]</p>"
        html += f"<p style='background-color:#f1f2f6; padding:8px;'><b>Résultat :</b> C({n},{k}) = <b>{res}</b></p></div>"
        self.log_area.setHtml(html)