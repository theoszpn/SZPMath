import numpy as np
from scipy import stats
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFrame,
                               QLabel, QLineEdit, QPushButton, QTextEdit,
                               QFormLayout, QComboBox, QButtonGroup)
from PySide6.QtCore import Qt


class EstimationsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.current_sample_idx = 0
        self.samples_data = [["", "", "", "", "", ""] for _ in range(2)]
        self.init_ui()

    def init_ui(self):
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        self.setStyleSheet("""
            QWidget { 
                color: #2c3e50; 
                font-family: 'Segoe UI', sans-serif; 
            }
            QLabel { 
                font-weight: bold;
                font-size: 14px; 
                color: #2c3e50;
            }
            QLineEdit {
                color: black !important;
                background-color: #ffffff !important;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                padding: 6px;
            }
            /* Style robuste pour le blanc pur des ComboBox */
            QComboBox {
                color: black !important;
                background-color: #ffffff !important;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                padding: 6px;
            }
            QComboBox:hover {
                border: 1px solid #3498db;
            }
            QComboBox QAbstractItemView {
                background-color: #ffffff !important;
                border: 1px solid #bdc3c7;
                selection-background-color: #3498db;
                selection-color: white;
                outline: none;
            }
        """)

        self.control_panel = QFrame()
        self.control_panel.setFixedWidth(380)
        self.control_panel.setStyleSheet("background-color: #f8f9fa; border: none; border-radius: 12px;")
        self.cp_layout = QVBoxLayout(self.control_panel)
        self.cp_layout.setContentsMargins(15, 15, 15, 15)
        self.cp_layout.setSpacing(10)

        self.sample_container = QFrame()
        self.sample_container.setObjectName("SampleBox")
        # Par défaut en Bleu
        self.sample_container.setStyleSheet(
            "QFrame#SampleBox { border: 2px solid #3498db; border-radius: 10px; background-color: white; }")

        self.sc_layout = QVBoxLayout(self.sample_container)
        self.sc_layout.setContentsMargins(0, 0, 0, 10)

        self.nav_bar = QFrame()
        self.nav_bar.setFixedHeight(40)
        self.nav_bar.setStyleSheet(
            "background-color: #3498db; border-top-left-radius: 8px; border-top-right-radius: 8px; border: none;")
        self.nb_layout = QHBoxLayout(self.nav_bar)
        self.nb_layout.setContentsMargins(15, 0, 15, 0)

        self.btn_prev = QPushButton("◀")
        self.btn_prev.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_prev.setStyleSheet(
            "color: white; font-weight: bold; font-size: 18px; border: none; background: transparent;")

        self.lbl_sample_title = QLabel("ÉCHANTILLON 1")
        self.lbl_sample_title.setStyleSheet("color: white; font-size: 13px; border: none;")
        self.lbl_sample_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.btn_next = QPushButton("▶")
        self.btn_next.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_next.setStyleSheet(
            "color: white; font-weight: bold; font-size: 18px; border: none; background: transparent;")

        self.nb_layout.addWidget(self.btn_prev)
        self.nb_layout.addWidget(self.lbl_sample_title, 1)
        self.nb_layout.addWidget(self.btn_next)
        self.sc_layout.addWidget(self.nav_bar)

        self.form_frame = QFrame()
        self.form_frame.setStyleSheet("border: none; background: transparent;")
        self.params_form = QFormLayout(self.form_frame)
        self.params_form.setSpacing(8)

        self.input_n = QLineEdit()
        self.input_n.setPlaceholderText("Ex: 50")
        self.input_mean = QLineEdit()
        self.input_mean.setPlaceholderText("Ex: 12.5")
        self.input_var = QLineEdit()
        self.input_var.setPlaceholderText("Ex: 4.2")
        self.input_med = QLineEdit()
        self.input_med.setPlaceholderText("Ex: 15")
        self.input_skew = QLineEdit()
        self.input_skew.setPlaceholderText("-0.3")
        self.input_kurt = QLineEdit()
        self.input_kurt.setPlaceholderText("1.2")

        self.params_form.addRow(QLabel("Effectif n :"), self.input_n)
        self.params_form.addRow(QLabel("Moyenne x̄ :"), self.input_mean)
        self.params_form.addRow(QLabel("Variance σ² / V(x) :"), self.input_var)
        self.params_form.addRow(QLabel("Médiane (optionnel) :"), self.input_med)
        self.params_form.addRow(QLabel("Skewness (optionnel) :"), self.input_skew)
        self.params_form.addRow(QLabel("Kurtosis (optionnel) :"), self.input_kurt)

        self.sc_layout.addWidget(self.form_frame)
        self.cp_layout.addWidget(self.sample_container)

        self.cp_layout.addSpacing(5)
        self.input_conf = QLineEdit("0.95")
        self.input_conf.setStyleSheet("""
            QLineEdit {
                color: black !important; background-color: #ffffff !important; border: 1px solid #bdc3c7; border-radius: 4px; padding: 6px;
                }
            """)
        conf_layout = QHBoxLayout()
        conf_layout.addWidget(QLabel("Confiance \u03b2 (1-\u03b1) :"))
        conf_layout.addWidget(self.input_conf)
        self.cp_layout.addLayout(conf_layout)

        self.combo_box_style = """QComboBox {
                color: black !important;
                background-color: #ffffff !important;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                padding: 6px;
            }
            QComboBox:hover {
                border: 1px solid #3498db;
            }
            QComboBox QAbstractItemView {
                background-color: #ffffff !important;
                border: 1px solid #bdc3c7;
                selection-background-color: #3498db;
                selection-color: white;
                outline: none;
            }"""

        self.sel_container = QHBoxLayout()
        self.combo_param = QComboBox()
        self.combo_param.setStyleSheet(self.combo_box_style)
        self.combo_param.addItems([
            "Moyenne (m)", "Écart-type (\u03c3)", "Variance (\u03c3\u00b2)",
            "Proportion (p)", "Lambda (\u03bb)", "Alpha (\u03b1)",
            "Médiane (Me)", "Skewness (S)", "Kurtosis (K)"
        ])
        self.sel_container.addWidget(QLabel("Parametre estimé :"))
        self.sel_container.addWidget(self.combo_param)
        self.cp_layout.addLayout(self.sel_container)

        self.law_container = QFrame()
        self.law_layout = QVBoxLayout(self.law_container)
        self.law_layout.setSpacing(10)

        self.btn_group_laws = QButtonGroup(self)
        self.btn_group_laws.setExclusive(True)

        self.btn_norm = QPushButton("Loi Normale")
        self.btn_norm.setObjectName("btnNorm")

        self.btn_stud = QPushButton("Loi de Student")
        self.btn_stud.setObjectName("btnStud")

        self.btn_khi = QPushButton("Loi du Khi-deux")
        self.btn_khi.setObjectName("btnKhi")

        self.law_container.setStyleSheet("""
                    QPushButton {
                        background-color: white;
                        border: 2px solid #bdc3c7;
                        border-radius: 6px;
                        padding: 12px;
                        font-weight: bold;
                        color: #2c3e50;
                    }
                    QPushButton:disabled {
                        background-color: #f5f6fa !important;
                        color: #dcdde1 !important;
                        border: 1px solid #dcdde1 !important;
                    }
                    QPushButton:hover {
                        border-left: 5px solid #d1d1d1;
                    }
                    QPushButton#btnNorm:checked {
                        background-color: #67bcf5 !important;
                        color: white !important;
                        border: 2px solid #2980b9 !important;
                    }
                    QPushButton#btnStud:checked {
                        background-color: #f7a359 !important;
                        color: white !important;
                        border: 2px solid #d35400 !important;
                    }
                    QPushButton#btnKhi:checked {
                        background-color: #52d98b !important;
                        color: white !important;
                        border: 2px solid #219150 !important;
                    }
                """)

        for btn in [self.btn_norm, self.btn_stud, self.btn_khi]:
            btn.setCheckable(True)
            self.btn_group_laws.addButton(btn)
            self.law_layout.addWidget(btn)

        self.cp_layout.addWidget(QLabel("Loi applicable :"))
        self.cp_layout.addWidget(self.law_container)

        self.combo_param.currentTextChanged.connect(self.update_available_laws)
        self.update_available_laws()

        self.btn_calc = QPushButton("LANCER L'ESTIMATION")
        self.btn_calc.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_calc.setStyleSheet("""
                    QPushButton { 
                        background-color: #213f69; color: white; padding: 12px; 
                        font-weight: bold; border-radius: 5px; margin-top: 10px;
                        text-align: left; padding-left: 20px; border: none;
                        font-size: 18px;
                    }
                    QPushButton:hover { 
                        background-color: #204d8c; 
                        border-left: 5px solid #2662b5;
                    }
                """)
        self.cp_layout.addWidget(self.btn_calc)
        self.cp_layout.addStretch()

        self.display_area = QFrame()
        self.display_area.setStyleSheet("background-color: white; border: 1px solid #dee2e6; border-radius: 8px;")
        self.display_layout = QVBoxLayout(self.display_area)
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setStyleSheet("border: none; background-color: white; color: black;")
        self.display_layout.addWidget(self.log_area)

        self.main_layout.addWidget(self.control_panel)
        self.main_layout.addWidget(self.display_area, 1)

        self.btn_prev.clicked.connect(lambda: self.switch_sample(-1))
        self.btn_next.clicked.connect(lambda: self.switch_sample(1))
        self.btn_calc.clicked.connect(self.run_estimation)

    def update_available_laws(self):
        param = self.combo_param.currentText()

        self.btn_norm.setEnabled(False)
        self.btn_stud.setEnabled(False)
        self.btn_khi.setEnabled(False)

        if "Moyenne" in param:
            self.btn_norm.setEnabled(True)
            self.btn_stud.setEnabled(True)
            if not self.btn_stud.isChecked():
                self.btn_norm.setChecked(True)

        elif "Variance" in param:
            self.btn_khi.setEnabled(True)
            self.btn_norm.setEnabled(True)
            if not self.btn_norm.isChecked():
                self.btn_khi.setChecked(True)

        elif "Écart-type" in param:
            self.btn_khi.setEnabled(True)
            self.btn_khi.setChecked(True)

        elif "Proportion" in param or "Lambda" in param or "Alpha" in param:
            self.btn_norm.setEnabled(True)
            self.btn_norm.setChecked(True)

    def switch_sample(self, direction):
        self.samples_data[self.current_sample_idx] = [
            self.input_n.text(), self.input_mean.text(), self.input_var.text(),
            self.input_med.text(), self.input_skew.text(), self.input_kurt.text()
        ]

        self.current_sample_idx = (self.current_sample_idx + direction) % 2

        color = "#3498db" if self.current_sample_idx == 0 else "#27ae60"
        hover_color = "#2980b9" if self.current_sample_idx == 0 else "#219150"

        self.sample_container.setStyleSheet(
            f"QFrame#SampleBox {{ border: 2px solid {color}; border-radius: 10px; background-color: white; }}")
        self.nav_bar.setStyleSheet(
            f"background-color: {color}; border-top-left-radius: 8px; border-top-right-radius: 8px; border: none;")
        self.btn_calc.setStyleSheet(
            f"QPushButton {{ background-color: {color}; color: white; font-weight: bold; padding: 12px; border-radius: 6px; border: none; }} QPushButton:hover {{ background-color: {hover_color}; }}")

        self.lbl_sample_title.setText(f"ÉCHANTILLON {self.current_sample_idx + 1}")
        d = self.samples_data[self.current_sample_idx]
        self.input_n.setText(d[0])
        self.input_mean.setText(d[1])
        self.input_var.setText(d[2])
        self.input_med.setText(d[3])
        self.input_skew.setText(d[4])
        self.input_kurt.setText(d[5])

    def format_math_stats(self, text):
        import re
        text = text.replace(r'\beta', '&beta;')
        text = text.replace(r'\alpha', '&alpha;')
        text = text.replace(r'\sigma', '&sigma;')
        text = text.replace(r'\mu', '<b>m</b>')
        text = text.replace(r'\bar{x}', '<b>x̄</b>')
        text = text.replace(r'\sqrt', '&radic;')
        text = text.replace(r'\cdot', '&times;')

        text = re.sub(r'_(.*?)(?=\s|$|\)|\.|,)', r'<sub>\1</sub>', text)
        return text

    def run_estimation(self):
        try:
            selected_law_btn = self.btn_group_laws.checkedButton()
            if not selected_law_btn:
                self.log_area.setHtml("<b style='color:red;'>Erreur :</b> Veuillez sélectionner une loi applicable.")
                return

            law = selected_law_btn.text()
            param = self.combo_param.currentText()

            if law == "Loi Normale":
                self.logic_normal(param)
            elif law == "Loi de Student":
                self.logic_student(param)
            elif law == "Loi du Khi-deux":
                self.logic_chi2(param)

        except Exception as e:
            self.log_area.setHtml(f"<b style='color:red;'>Erreur d'aiguillage :</b> {e}")

    def logic_normal(self, param_name):
        try:
            import io, base64
            import matplotlib.pyplot as plt

            n_val = int(self.input_n.text())
            estim_val = float(self.input_mean.text())
            var_val = float(self.input_var.text())
            beta_val = float(self.input_conf.text())
            t_beta_val = stats.norm.ppf((1 + beta_val) / 2)

            html = "<div style='font-size: 15px; color: #2c3e50; line-height: 1.7;'>"
            html += "<h1 style='color: #2c3e50; text-align: center; border-bottom: 2px solid #bdc3c7; padding-bottom: 10px;'>Estimation paramétrique - Loi Normale</h1>"

            if "Moyenne" in param_name:
                symbol_param = "m"
                symbol_estim = "<b>x̄</b>"
                phrase1 = fr"On cherche à donner un intervalle de confiance pour la valeur du paramètre <b>m</b> (estimé par <b>x̄</b> = {estim_val}), au seuil \beta : <b>{beta_val}</b>.<br>"
                num_v, den_v = "V(x)", "n"
                margin = t_beta_val * np.sqrt(var_val / n_val)
                dist_se = np.sqrt(var_val / n_val)

            elif "Variance" in param_name:
                estim_val = var_val
                symbol_param = r"<b>\sigma<sup>2</sup></b>"
                symbol_estim = "<b>V<sub>x</sub></b>"
                phrase1 = fr"On cherche à donner un intervalle de confiance pour la valeur du paramètre <b>\sigma<sup>2</sup></b> (estimé par <b>V<sub>x</sub></b> = {estim_val}), au seuil \beta = <b>{beta_val}</b>.<br>"
                num_v, den_v = "2(V<sub>x</sub>)<sup>2</sup>", "n"
                margin = t_beta_val * np.sqrt((2 * (var_val ** 2)) / n_val)
                dist_se = np.sqrt((2 * (var_val ** 2)) / n_val)

            elif "Proportion" in param_name:
                symbol_param = "p"
                symbol_estim = "<b>p̂</b>"
                phrase1 = fr"On cherche à donner un intervalle de confiance pour la proportion <b>p</b> (estimée par <b>p̂</b> = {estim_val}), au seuil \beta = <b>{beta_val}</b>.<br>"
                num_v = "p̂(1 - p̂)"
                den_v = "n"
                margin = t_beta_val * np.sqrt((estim_val * (1 - estim_val)) / n_val)
                dist_se = np.sqrt((estim_val * (1 - estim_val)) / n_val)

            elif "Lambda" in param_name:
                symbol_param = "&lambda;"
                symbol_estim = "<b>λ̂</b>"
                phrase1 = fr"On cherche à donner un intervalle de confiance pour le paramètre <b>&lambda;</b> (estimé par <b>λ̂</b> = {estim_val}), au seuil \beta = <b>{beta_val}</b>.<br>"
                num_v = "λ̂"
                den_v = "n"
                margin = t_beta_val * np.sqrt(estim_val / n_val)
                dist_se = np.sqrt(estim_val / n_val)

            elif "Alpha" in param_name:
                symbol_param = "&alpha;"
                symbol_estim = "<b>α̂</b>"
                phrase1 = fr"On cherche à donner un intervalle de confiance pour le paramètre <b>&alpha;</b> (estimé par <b>α̂</b> = {estim_val}), au seuil \beta = <b>{beta_val}</b>.<br>"
                num_v = "α̂<sup>2</sup>"
                den_v = "n"
                margin = t_beta_val * (estim_val / np.sqrt(n_val))
                dist_se = estim_val / np.sqrt(n_val)

            elif "Médiane" in param_name:
                estim_val = float(self.input_med.text())
                symbol_param, symbol_estim = "M", "<b>Med</b>"
                phrase1 = fr"On cherche à donner un intervalle de confiance pour la médiane <b>M</b> (estimée par <b>Med</b> = {estim_val}), au seuil \beta = <b>{beta_val}</b>.<br>"
                num_v, den_v = "1.253 &times; &sigma;", "&radic;n"
                dist_se = 1.253 * (np.sqrt(var_val) / np.sqrt(n_val))
                margin = t_beta_val * dist_se

            elif "Skewness" in param_name:
                estim_val = float(self.input_skew.text())
                symbol_param, symbol_estim = "<b>S</b>", "<b>S'</b>"
                phrase1 = fr"On cherche à donner un intervalle de confiance pour le skewness <b>S</b> (estimé par <b>S'</b> = {estim_val}), au seuil \beta = <b>{beta_val}</b>.<br>"
                num_v, den_v = "6", "n"
                dist_se = np.sqrt(6 / n_val)
                margin = t_beta_val * dist_se

            elif "Kurtosis" in param_name:
                estim_val = float(self.input_kurt.text())
                symbol_param, symbol_estim = "<b>K</b>", "<b>K'</b>"
                phrase1 = fr"On cherche à donner un intervalle de confiance pour le kurtosis <b>K</b> (estimé par <b>K'</b> = {estim_val}), au seuil \beta = <b>{beta_val}</b>.<br>"
                num_v, den_v = "24", "n"
                dist_se = np.sqrt(24 / n_val)
                margin = t_beta_val * dist_se

            html += self.format_math_stats(phrase1)

            if n_val < 30:
                html += "<p style='color: #e67e22;'><b>Attention :</b> ici n &lt; 30 donc l'utilisation d'une loi exacte serait plus précise. On peut toutefois utiliser l'approximation normale.</p>"
            else:
                html += f"L'échantillon est de taille <b>n</b> = {n_val} donc on peut utiliser l'approximation normale.<br>"

            phrase3 = fr"On pose <b>t_\beta = {t_beta_val:.3f}</b>, tel que si X suit une loi N(0,1) : <b>P(-t_\beta &lt; X &lt; t_\beta) = {beta_val}</b>.<br><br>"
            html += self.format_math_stats(phrase3)

            cell_style = "border: 1px solid #2c3e50; padding: 4px;"
            html += f"""
                    <p style='text-align: center; margin-bottom: 5px;'><b>Valeurs de t<sub>&beta;</sub> usuelles (Loi Normale) :</b></p>
                    <table style='border-collapse: collapse; width: 100%; text-align: center; background-color: white; font-size: 11px; border: 1px solid #2c3e50;'>
                        <tr style='background-color: #f2f2f2;'>
                            <th style='{cell_style}'>&beta;</th>
                            <td style='{cell_style}'>0.80</td><td style='{cell_style}'>0.85</td><td style='{cell_style}'>0.90</td>
                            <td style='{cell_style}'>0.925</td><td style='{cell_style}'>0.95</td><td style='{cell_style}'>0.975</td>
                            <td style='{cell_style}'>0.98</td><td style='{cell_style}'>0.99</td><td style='{cell_style}'>0.995</td>
                            <td style='{cell_style}'>0.999</td>
                        </tr>
                        <tr>
                            <th style='{cell_style}'>t<sub>&beta;</sub></th>
                            <td style='{cell_style}'>1.282</td><td style='{cell_style}'>1.440</td><td style='{cell_style}'>1.645</td>
                            <td style='{cell_style}'>1.780</td><td style='{cell_style}'>1.960</td><td style='{cell_style}'>2.241</td>
                            <td style='{cell_style}'>2.326</td><td style='{cell_style}'>2.576</td><td style='{cell_style}'>2.807</td>
                            <td style='{cell_style}'>3.291</td>
                        </tr>
                    </table><br>
                    """

            html += self.format_math_stats(fr"Selon le Théoreme Limite Central (TLC), un intervalle de confiance de {symbol_param} au niveau de confiance <b>\beta = {beta_val}</b> est :<br>")

            if "Médiane" in param_name:
                inner_symbol_theo = "&nbsp;&times;&nbsp;"
                radical_left_theo = ""
                border_theo = "none"
            else:
                inner_symbol_theo = ""
                radical_left_theo = '<td style="vertical-align: middle; font-size: 26px; padding-left: 5px;">&radic;</td>'
                border_theo = "1px solid black"

            formula_html = f"""
                    <div align="center" style="margin: 20px 0;">
                        <table cellspacing="0" cellpadding="0" style="color: black; font-size: 19px; font-family: 'Times New Roman';">
                            <tr>
                                <td style="font-size: 38px; vertical-align: middle;">[</td>
                                <td style="font-size: 19px; vertical-align: middle;">{symbol_estim} - t<sub>&beta;</sub>{inner_symbol_theo}</td>
                                {radical_left_theo}
                                <td style="vertical-align: middle; border-top: {border_theo};">
                                    <table cellspacing="0" cellpadding="0" style="text-align: center; font-size: 14px;">
                                        <tr><td style="border-bottom: 1px solid black; padding: 0 4px;">{num_v}</td></tr>
                                        <tr><td style="padding: 0 10px;">{den_v}</td></tr>
                                    </table>
                                </td>
                                <td style="vertical-align: middle;">&nbsp;&nbsp;;&nbsp;&nbsp; {symbol_estim} + t<sub>&beta;</sub>{inner_symbol_theo}</td>
                                {radical_left_theo}
                                <td style="vertical-align: middle; border-top: {border_theo};">
                                    <table cellspacing="0" cellpadding="0" style="text-align: center; font-size: 14px;">
                                        <tr><td style="border-bottom: 1px solid black; padding: 0 4px;">{num_v}</td></tr>
                                        <tr><td style="padding: 0 10px;">{den_v}</td></tr>
                                    </table>
                                </td>
                                <td style="font-size: 38px; vertical-align: middle; padding-left: 5px;"> ]</td>
                            </tr>
                        </table>
                    </div>
                    """
            html += formula_html

            sigma_val = np.sqrt(var_val)

            if "Médiane" in param_name:
                val_num_top = f"1.253 &times; {sigma_val:.2f}"
                val_den = f"&radic;{n_val}"
            elif "Skewness" in param_name:
                val_num_top = "6"
                val_den = f"{n_val}"
            elif "Kurtosis" in param_name:
                val_num_top = "24"
                val_den = f"{n_val}"
            elif "Proportion" in param_name:
                val_num_top = f"{estim_val}(1 - {estim_val})"
                val_den = f"{n_val}"
            elif "Lambda" in param_name:
                val_num_top = f"{estim_val}"
                val_den = f"{n_val}"
            elif "Alpha" in param_name:
                val_num_top = f"{estim_val}<sup>2</sup>"
                val_den = f"{n_val}"
            elif "Variance" in param_name:
                val_num_top = f"2 &times; {var_val}<sup>2</sup>"
                val_den = f"{n_val}"
            elif "Moyenne" in param_name:
                val_num_top = f"{var_val}"
                val_den = f"{n_val}"


            if "Médiane" in param_name:
                inner_symbol = "&nbsp;&times;&nbsp;"
                radical_left = ""
            else:
                inner_symbol = ""
                radical_left = '<td style="vertical-align: middle; font-size: 26px; padding-left: 5px;">&radic;</td>'

            html += f"""
            <div align="center" style="margin: 20px 0;">
                <table cellspacing="0" cellpadding="0" style="color: black; font-size: 19px; font-family: 'Times New Roman';">
                    <tr>
                        <td style="font-size: 38px; vertical-align: middle;">[</td>
                        <td style="font-size: 19px; vertical-align: middle;">{estim_val} - {t_beta_val:.3f}{inner_symbol}</td>
                        {radical_left}
                        <td style="vertical-align: middle; border-top: {"1px solid black" if radical_left else "none"};">
                            <table cellspacing="0" cellpadding="0" style="text-align: center; font-size: 14px;">
                                <tr><td style="border-bottom: 1px solid black; padding: 0 4px;">{val_num_top}</td></tr>
                                <tr><td style="padding: 0 10px;">{val_den}</td></tr>
                            </table>
                        </td>
                        <td style="vertical-align: middle;">&nbsp;&nbsp;;&nbsp;&nbsp; {estim_val} + {t_beta_val:.3f}{inner_symbol}</td>
                        {radical_left}
                        <td style="vertical-align: middle; border-top: {"1px solid black" if radical_left else "none"};">
                            <table cellspacing="0" cellpadding="0" style="text-align: center; font-size: 14px;">
                                <tr><td style="border-bottom: 1px solid black; padding: 0 4px;">{val_num_top}</td></tr>
                                <tr><td style="padding: 0 10px;">{val_den}</td></tr>
                            </table>
                        </td>
                        <td style="font-size: 38px; vertical-align: middle; padding-left: 5px;"> ]</td>
                    </tr>
                </table>
            </div>
            """

            ic_inf, ic_sup = estim_val - margin, estim_val + margin
            html += f"""
                <div align="center" style="margin: 20px 0;">
                    <table cellspacing="0" cellpadding="0" style="color: black; font-size: 19px; font-weight: bold; font-family: 'Times New Roman'">
                        <tr>
                            <td style="vertical-align: middle;">RÉSULTAT FINAL :&nbsp;&nbsp; <b>IC</b> = </td>
                            <td style="font-size: 38px; vertical-align: middle; padding-left: 5px;">[</td>
                            <td style="font-size: 19px; vertical-align: middle; padding: 0 5px;"> {ic_inf:.4f} ; {ic_sup:.4f} </td>
                            <td style="font-size: 38px; vertical-align: middle;"> ]</td>
                        </tr>
                    </table>
                </div>
                """

            fig, ax = plt.subplots(figsize=(6, 3))
            x_axis = np.linspace(estim_val - 4 * dist_se, estim_val + 4 * dist_se, 200)
            y_axis = stats.norm.pdf(x_axis, estim_val, dist_se)
            ax.plot(x_axis, y_axis, color='#3498db', lw=2)
            ax.fill_between(x_axis, y_axis, where=((x_axis >= ic_inf) & (x_axis <= ic_sup)), color='#3498db', alpha=0.3)
            ax.set_title(f"Distribution de l'estimateur ({param_name})", fontsize=10)
            ax.grid(True, alpha=0.3)

            buf = io.BytesIO(); plt.savefig(buf, format='png', bbox_inches='tight'); plt.close(fig)
            html += f"<br><center><img src='data:image/png;base64,{base64.b64encode(buf.getvalue()).decode()}' width='450'></center></div>"

            self.log_area.setHtml(html)

        except Exception as e:
            self.log_area.setHtml(f"<b style='color:red;'>Erreur dans logic_normal :</b> {e}")

    def logic_student(self, param_name):
        try:
            import io, base64
            import matplotlib.pyplot as plt

            n_val = int(self.input_n.text())
            mean_val = float(self.input_mean.text())
            var_val = float(self.input_var.text())
            beta_val = float(self.input_conf.text())

            ddl = n_val - 1
            t_beta_val = stats.t.ppf((1 + beta_val) / 2, df=ddl)

            html = "<div style='font-size: 15px; color: #2c3e50; line-height: 1.7;'>"
            html += "<h1 style='color: #2c3e50; text-align: center; border-bottom: 2px solid #bdc3c7; padding-bottom: 10px;'>Estimation paramétrique - Loi de Student</h1>"

            phrase1 = fr"On cherche à donner un intervalle de confiance pour la valeur du paramètre <b>m</b> (estimé par <b>x̄</b>), au seuil \beta : <b>{beta_val}</b>.<br>"
            html += self.format_math_stats(phrase1)

            html += f"La variance de la population &sigma;² est inconnue, nous utilisons donc la variance observée (celle de l'échantillon) <b>V<sub>x</sub></b>. "
            html += f"L'échantillon étant petit (n = {n_val}), la <b>loi de Student</b> est plus précise que la <b>loi Normale</b>."

            phrase3 = fr"On utilise une loi de Student à <b>n - 1 = {ddl}</b> degrés de liberté.<br>"
            phrase3 += fr"On pose <b>t_\beta = {t_beta_val:.3f}</b>, tel que si X suit une loi de Student : <b>P(-t_\beta &lt; X &lt; t_\beta) = {beta_val}</b>.<br><br>"
            html += self.format_math_stats(phrase3)

            betas_table = [0.80, 0.85, 0.90, 0.925, 0.95, 0.975, 0.98, 0.99, 0.995, 0.999]
            t_vals = [stats.t.ppf((1 + b) / 2, df=ddl) for b in betas_table]

            cell_style = "border: 1px solid #2c3e50; padding: 4px;"
            html += f"""
                    <p style='text-align: center; margin-bottom: 5px;'><b>Valeurs de t<sub>&beta;</sub> usuelles (Loi de Student, ddl = {ddl}) :</b></p>
                    <table style='border-collapse: collapse; width: 100%; text-align: center; background-color: white; font-size: 11px; border: 1px solid #2c3e50;'>
                        <tr style='background-color: #f2f2f2;'>
                            <th style='{cell_style}'>&beta;</th>
                            {"".join([f"<td style='{cell_style}'>{b}</td>" for b in betas_table])}
                        </tr>
                        <tr>
                            <th style='{cell_style}'>t<sub>&beta;</sub></th>
                            {"".join([f"<td style='{cell_style}'>{t:.3f}</td>" for t in t_vals])}
                        </tr>
                    </table><br>
                    """

            html += self.format_math_stats(
                fr"Selon la loi de Student, un intervalle de confiance de <b>m</b> au niveau de confiance <b>\beta = {beta_val}</b> est :<br>")

            formula_html = f"""
            <div align="center" style="margin: 20px 0;">
                <table cellspacing="0" cellpadding="0" style="color: black; font-size: 19px; font-family: 'Times New Roman';">
                    <tr>
                        <td style="font-size: 38px; vertical-align: middle;">[</td>
                        <td style="font-size: 19px; vertical-align: middle;"><b>x̄</b> - t<sub>&beta;</sub></td>
                        <td style="vertical-align: middle; font-size: 26px; padding-left: 5px;">&radic;</td>
                        <td style="vertical-align: middle; border-top: 1px solid black;">
                            <table cellspacing="0" cellpadding="0" style="text-align: center; font-size: 14px;">
                                <tr><td style="border-bottom: 1px solid black; padding: 0 4px;">V<sub>x</sub></td></tr>
                                <tr><td style="padding: 0 10px;">n</td></tr>
                            </table>
                        </td>
                        <td style="vertical-align: middle;">&nbsp;&nbsp;;&nbsp;&nbsp; <b>x̄</b> + t<sub>&beta;</sub></td>
                        <td style="vertical-align: middle; font-size: 26px; padding-left: 5px;">&radic;</td>
                        <td style="vertical-align: middle; border-top: 1px solid black;">
                            <table cellspacing="0" cellpadding="0" style="text-align: center; font-size: 14px;">
                                <tr><td style="border-bottom: 1px solid black; padding: 0 4px;">V<sub>x</sub></td></tr>
                                <tr><td style="padding: 0 10px;">n</td></tr>
                            </table>
                        </td>
                        <td style="font-size: 38px; vertical-align: middle; padding-left: 5px;"> ]</td>
                    </tr>
                </table>
            </div>
            """
            html += formula_html

            app_num_html = f"""
            <div align="center" style="margin: 20px 0;">
                <table cellspacing="0" cellpadding="0" style="color: black; font-size: 19px; font-family: 'Times New Roman';">
                    <tr>
                        <td style="font-size: 38px; vertical-align: middle;">[</td>
                        <td style="font-size: 19px; vertical-align: middle;">{mean_val} - {t_beta_val:.3f}</td>
                        <td style="vertical-align: middle; font-size: 26px; padding-left: 5px;">&radic;</td>
                        <td style="vertical-align: middle; border-top: 1px solid black;">
                            <table cellspacing="0" cellpadding="0" style="text-align: center; font-size: 14px;">
                                <tr><td style="border-bottom: 1px solid black; padding: 0 4px;">{var_val}</td></tr>
                                <tr><td style="padding: 0 10px;">{n_val}</td></tr>
                            </table>
                        </td>
                        <td style="vertical-align: middle;">&nbsp;&nbsp;;&nbsp;&nbsp; {mean_val} + {t_beta_val:.3f}</td>
                        <td style="vertical-align: middle; font-size: 26px; padding-left: 5px;">&radic;</td>
                        <td style="vertical-align: middle; border-top: 1px solid black;">
                            <table cellspacing="0" cellpadding="0" style="text-align: center; font-size: 14px;">
                                <tr><td style="border-bottom: 1px solid black; padding: 0 4px;">{var_val}</td></tr>
                                <tr><td style="padding: 0 10px;">{n_val}</td></tr>
                            </table>
                        </td>
                        <td style="font-size: 38px; vertical-align: middle; padding-left: 5px;"> ]</td>
                    </tr>
                </table>
            </div>
            """
            html += app_num_html

            margin = t_beta_val * np.sqrt(var_val / n_val)
            ic_inf, ic_sup = mean_val - margin, mean_val + margin

            result_html = f"""
                <div align="center" style="margin: 20px 0;">
                    <table cellspacing="0" cellpadding="0" style="color: black; font-size: 19px; font-weight: bold; font-family: 'Times New Roman'">
                        <tr>
                            <td style="vertical-align: middle;">RÉSULTAT FINAL :&nbsp;&nbsp; <b>IC</b> = </td>
                            <td style="font-size: 38px; vertical-align: middle; padding-left: 5px;">[</td>
                            <td style="font-size: 19px; vertical-align: middle; padding: 0 5px;"> {ic_inf:.4f} ; {ic_sup:.4f} </td>
                            <td style="font-size: 38px; vertical-align: middle;"> ]</td>
                        </tr>
                    </table>
                </div>
                """
            html += result_html

            fig, ax = plt.subplots(figsize=(6, 3))
            se = np.sqrt(var_val / n_val)
            x_axis = np.linspace(mean_val - 4 * se, mean_val + 4 * se, 200)
            y_axis = stats.t.pdf(x_axis, df=ddl, loc=mean_val, scale=se)
            ax.plot(x_axis, y_axis, color='#e67e22', lw=2)
            ax.fill_between(x_axis, y_axis, where=((x_axis >= ic_inf) & (x_axis <= ic_sup)), color='#e67e22', alpha=0.3)
            ax.set_title(f"Visualisation de l'intervalle à {beta_val * 100}%", fontsize=10)
            ax.grid(True, alpha=0.3)

            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight')
            plt.close(fig)
            b64 = base64.b64encode(buf.getvalue()).decode()
            html += f"<br><center><img src='data:image/png;base64,{b64}' width='450'></center></div>"

            self.log_area.setHtml(html)

        except Exception as e:
            self.log_area.setHtml(f"<b style='color:red;'>Erreur dans logic_student :</b> {e}")

    def logic_chi2(self, param_name):
        try:
            import io, base64
            import matplotlib.pyplot as plt

            n_val = int(self.input_n.text())
            var_val = float(self.input_var.text())
            beta_val = float(self.input_conf.text())

            ddl = n_val - 1
            alpha = 1 - beta_val

            khi2_inf = stats.chi2.ppf(alpha / 2, df=ddl)
            khi2_sup = stats.chi2.ppf(1 - alpha / 2, df=ddl)

            html = "<div style='font-size: 15px; color: #2c3e50; line-height: 1.7;'>"
            html += "<h1 style='color: #2c3e50; text-align: center; border-bottom: 2px solid #bdc3c7; padding-bottom: 10px;'>Estimation paramétrique - Loi du Khi-deux</h1>"

            symbol_param = "<b>&sigma;²</b>"
            symbol_estim = "<b>V<sub>x</sub></b>"
            phrase1 = fr"On cherche à donner un intervalle de confiance pour la valeur du paramètre {symbol_param} (estimé par {symbol_estim}), au seuil \beta = <b>{beta_val}</b>.<br>"
            html += self.format_math_stats(phrase1)

            html += f"On suppose que la population d'origine suit une loi normale. Comme l'échantillon est petit (n &lt; 30), la loi du <b>Khi-deux</b> est la méthode la plus précise pour estimer la variance.<br>"

            html += f"<br>Pour un niveau de confiance &beta; = {beta_val}, le risque d'erreur total est &alpha; = 1 - &beta; = {alpha:.3f}. "
            html += f"On partage ce risque en deux extrémités de la distribution, soit <b>&alpha;/2 = {alpha / 2:.4f}</b> à gauche et à droite.<br>"

            html += f"On cherche donc les valeurs critiques dans la table du &chi;&sup2; à <b>n - 1 = {ddl}</b> degrés de liberté :<br>"
            html += f"&bull; <b>&chi;&sup2;<sub>inf</sub></b> = &chi;&sup2;<b><sub>{alpha / 2:.4f} ; {ddl}</sub></b> = <b>{khi2_inf:.3f}</b><br>"
            html += f"&bull; <b>&chi;&sup2;<sub>sup</sub></b> = &chi;&sup2;<b><sub>{1 - alpha / 2:.4f} ; {ddl}</sub></b> = <b>{khi2_sup:.3f}</b><br>"

            betas_table = [0.90, 0.95, 0.975, 0.98, 0.99]
            cell_style = "border: 1px solid #2c3e50; padding: 4px;"
            html += f"<p style='text-align: center; margin-bottom: 5px;'><b>Valeurs critiques usuelles du &chi;² (ddl = {ddl}) :</b></p>"
            html += f"<table style='border-collapse: collapse; width: 100%; text-align: center; background-color: white; font-size: 11px; border: 1px solid #2c3e50;'>"
            html += f"<tr style='background-color: #f2f2f2;'><th style='{cell_style}'>&beta;</th>" + "".join(
                [f"<td style='{cell_style}'>{b}</td>" for b in betas_table]) + "</tr>"
            html += f"<tr><th style='{cell_style}'>&chi;²<sub>inf</sub></th>" + "".join(
                [f"<td style='{cell_style}'>{stats.chi2.ppf((1 - b) / 2, ddl):.3f}</td>" for b in
                 betas_table]) + "</tr>"
            html += f"<tr><th style='{cell_style}'>&chi;²<sub>sup</sub></th>" + "".join(
                [f"<td style='{cell_style}'>{stats.chi2.ppf(1 - (1 - b) / 2, ddl):.3f}</td>" for b in
                 betas_table]) + "</tr></table><br>"

            html += self.format_math_stats(
                fr"<br>Selon la loi du Khi-deux à <b>{ddl}</b> degrés de liberté, l'intervalle de confiance est :<br>")

            formula_html = f"""
            <div align="center" style="margin: 20px 0;">
                <table cellspacing="0" cellpadding="0" style="color: black; font-size: 19px; font-family: 'Times New Roman';">
                    <tr>
                        <td style="vertical-align: middle;"><b>IC</b> = </td>
                        <td style="font-size: 38px; vertical-align: middle; padding-left: 10px;">[</td>
                        <td style="vertical-align: middle;">
                            <table cellspacing="0" cellpadding="0" style="text-align: center; font-size: 16px;">
                                <tr><td style="border-bottom: 1px solid black; padding: 0 10px;">(n - 1)V<sub>x</sub></td></tr>
                                <tr><td style="text-align: center;">&chi;²<sub>sup</sub></td></tr>
                            </table>
                        </td>
                        <td style="vertical-align: middle;">&nbsp;&nbsp;;&nbsp;&nbsp;</td>
                        <td style="vertical-align: middle;">
                            <table cellspacing="0" cellpadding="0" style="text-align: center; font-size: 16px;">
                                <tr><td style="border-bottom: 1px solid black; padding: 0 10px;">(n - 1)V<sub>x</sub></td></tr>
                                <tr><td style="text-align: center;">&chi;²<sub>inf</sub></td></tr>
                            </table>
                        </td>
                        <td style="font-size: 38px; vertical-align: middle; padding-left: 5px;"> ]</td>
                    </tr>
                </table>
            </div>
            """
            html += formula_html

            app_num_html = f"""
            <div align="center" style="margin: 20px 0;">
                <table cellspacing="0" cellpadding="0" style="color: black; font-size: 19px; font-family: 'Times New Roman';">
                    <tr>
                        <td style="vertical-align: middle;"><b>IC</b> = </td>
                        <td style="font-size: 38px; vertical-align: middle; padding-left: 10px;">[</td>
                        <td style="vertical-align: middle;">
                            <table cellspacing="0" cellpadding="0" style="text-align: center; font-size: 16px;">
                                <tr><td style="border-bottom: 1px solid black; padding: 0 10px;">{ddl} &times; {var_val}</td></tr>
                                <tr><td style="text-align: center;">{khi2_sup:.3f}</td></tr>
                            </table>
                        </td>
                        <td style="vertical-align: middle;">&nbsp;&nbsp;;&nbsp;&nbsp;</td>
                        <td style="vertical-align: middle;">
                            <table cellspacing="0" cellpadding="0" style="text-align: center; font-size: 16px;">
                                <tr><td style="border-bottom: 1px solid black; padding: 0 10px;">{ddl} &times; {var_val}</td></tr>
                                <tr><td style="text-align: center;">{khi2_inf:.3f}</td></tr>
                            </table>
                        </td>
                        <td style="font-size: 38px; vertical-align: middle; padding-left: 5px;"> ]</td>
                    </tr>
                </table>
            </div>
            """
            html += app_num_html

            ic_inf_var = (ddl * var_val) / khi2_sup
            ic_sup_var = (ddl * var_val) / khi2_inf

            final_inf, final_sup = ic_inf_var, ic_sup_var
            res_label = "<b>IC<sub>&sigma;²</sub></b>"

            result_html = f"""
                            <div align="center" style="margin: 20px 0;">
                                <table cellspacing="0" cellpadding="0" style="color: black; font-size: 19px; font-weight: bold; font-family: 'Times New Roman'">
                                    <tr>
                                        <td style="vertical-align: middle;">RÉSULTAT FINAL :&nbsp;&nbsp; {res_label} = </td>
                                        <td style="font-size: 38px; vertical-align: middle; padding-left: 5px;">[</td>
                                        <td style="font-size: 19px; vertical-align: middle; padding: 0 5px;"> {final_inf:.4f} ; {final_sup:.4f} </td>
                                        <td style="font-size: 38px; vertical-align: middle;"> ]</td>
                                    </tr>
                                </table>
                            </div>
                            """
            html += result_html

            if "Écart-type" in param_name:
                final_inf = np.sqrt(ic_inf_var)
                final_sup = np.sqrt(ic_sup_var)

                html += f"""
                            <div align="center" style="margin: 10px 0;">
                                <table cellspacing="0" cellpadding="0" style="color: #7f8c8d; font-size: 18px; font-family: 'Times New Roman'">
                                    <tr>
                                        <td style="vertical-align: middle;">D'où l'écart-type :&nbsp;&nbsp; <b>IC<sub>&sigma;</sub></b> = </td>
                                        <td style="font-size: 38px; vertical-align: middle; padding-left: 5px;">[</td>
                                        <td style="font-size: 19px; vertical-align: middle; padding: 0 5px;"> &radic;<span style="text-decoration:overline;">{ic_inf_var:.4f}</span> ; &radic;<span style="text-decoration:overline;">{ic_sup_var:.4f}</span> </td>
                                        <td style="font-size: 38px; vertical-align: middle;"> ]</td>
                                    </tr>
                                </table>
                            </div>
                            """

                html += f"""
                            <div align="center" style="margin: 10px 0;">
                                <table cellspacing="0" cellpadding="0" style="color: black; font-size: 19px; font-weight: bold; font-family: 'Times New Roman'">
                                    <tr>
                                        <td style="vertical-align: middle;">SOIT FINALEMENT :&nbsp;&nbsp; <b>IC<sub>&sigma;</sub></b> = </td>
                                        <td style="font-size: 38px; vertical-align: middle; padding-left: 5px;">[</td>
                                        <td style="font-size: 19px; vertical-align: middle; padding: 0 5px;"> {final_inf:.4f} ; {final_sup:.4f} </td>
                                        <td style="font-size: 38px; vertical-align: middle;"> ]</td>
                                    </tr>
                                </table>
                            </div>
                            """

            fig, ax = plt.subplots(figsize=(6, 3))
            x_axis = np.linspace(0, stats.chi2.ppf(0.999, df=ddl), 300)
            y_axis = stats.chi2.pdf(x_axis, df=ddl)
            ax.plot(x_axis, y_axis, color='#3ead46', lw=2)
            ax.fill_between(x_axis, y_axis, where=((x_axis >= khi2_inf) & (x_axis <= khi2_sup)), color='#3ead46',
                            alpha=0.3)
            ax.set_title(f"Distribution du Khi-deux (ddl = {ddl})", fontsize=10)
            ax.grid(True, alpha=0.3)

            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight')
            plt.close(fig)
            html += f"<br><center><img src='data:image/png;base64,{base64.b64encode(buf.getvalue()).decode()}' width='450'></center></div>"

            self.log_area.setHtml(html)

        except Exception as e:
            self.log_area.setHtml(f"<b style='color:red;'>Erreur dans logic_chi2 :</b> {e}")