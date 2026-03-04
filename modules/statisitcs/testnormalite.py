import numpy as np
from scipy import stats
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFrame,
                               QLabel, QLineEdit, QPushButton, QTextEdit,
                               QFormLayout, QTableWidget, QTableWidgetItem,
                               QHeaderView, QStackedWidget, QButtonGroup)
from PySide6.QtCore import Qt


class TestsNormalitePage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        self.setStyleSheet("""
            QWidget { color: #2c3e50; font-family: 'Segoe UI', sans-serif; }
            QLabel { font-weight: bold; font-size: 14px; }
            QLineEdit { 
                color: black !important; background-color: white !important; 
                border: 1px solid #bdc3c7; border-radius: 4px; padding: 6px; 
            }
        """)

        self.control_panel = QFrame()
        self.control_panel.setFixedWidth(380)
        self.control_panel.setStyleSheet("background-color: #f8f9fa; border-radius: 12px; border: none;")
        self.cp_layout = QVBoxLayout(self.control_panel)
        self.cp_layout.setContentsMargins(15, 15, 15, 15)
        self.cp_layout.setSpacing(10)

        self.toggle_layout = QHBoxLayout()
        self.btn_mode_table = QPushButton("Table X")
        self.btn_mode_echantillon = QPushButton("Echantillon")

        style_table = """
            QPushButton { 
                background-color: white; color: #3498db; border: 2px solid #3498db; 
                border-radius: 6px; height: 18px; font-weight: bold; font-size: 16px;
            }
            QPushButton:hover { background-color: #ebf5fb; }
            QPushButton:checked { background-color: #3498db; color: white; }
            QPushButton:checked:hover { background-color: #2980b9; }
        """
        style_ech = """
            QPushButton { 
                background-color: white; color: #f7a359; border: 2px solid #f7a359; 
                border-radius: 6px; height: 18px; font-weight: bold; font-size: 16px;
            }
            QPushButton:hover { background-color: #fef5ec; }
            QPushButton:checked { background-color: #f7a359; color: white; }
            QPushButton:checked:hover { background-color: #e67e22; }
        """
        self.btn_mode_table.setStyleSheet(style_table)
        self.btn_mode_echantillon.setStyleSheet(style_ech)

        self.btn_mode_table.setCheckable(True)
        self.btn_mode_echantillon.setCheckable(True)
        self.btn_mode_table.setChecked(True)

        self.btn_group = QButtonGroup(self)
        self.btn_group.addButton(self.btn_mode_table)
        self.btn_group.addButton(self.btn_mode_echantillon)
        self.btn_group.setExclusive(True)

        self.toggle_layout.addWidget(self.btn_mode_table)
        self.toggle_layout.addWidget(self.btn_mode_echantillon)
        self.cp_layout.addLayout(self.toggle_layout)

        # 2. STACKED WIDGET
        self.input_stack = QStackedWidget()

        self.page_table = QWidget()
        self.layout_table = QVBoxLayout(self.page_table)
        self.layout_table.setContentsMargins(0, 5, 0, 0)

        self.data_table = QTableWidget(15, 1)
        self.data_table.setFixedWidth(150)
        self.data_table.setFixedHeight(350)
        self.data_table.setHorizontalHeaderLabels(["X"])
        self.data_table.verticalHeader().setVisible(False)
        self.data_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.data_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                color: black !important;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
            }
            QTableWidget QLineEdit { background-color: white; color: black; border: none; }
        """)
        self.data_table.horizontalHeader().setStyleSheet(
            "QHeaderView::section { background-color: #f8f9fa; color: black !important; font-weight: bold; border: 1px solid #dee2e6; height: 30px; }")

        for r in range(15):
            self.data_table.setItem(r, 0, QTableWidgetItem(""))

        self.row_controls = QHBoxLayout()
        self.btn_add_row = QPushButton("+ Ligne")
        self.btn_rem_row = QPushButton("- Ligne")
        btn_row_style = ("""QPushButton { background-color: #ecf0f1; border: 1px solid #bdc3c7; padding: 6px; font-weight: bold; border-radius: 4px; }
                         QPushButton:hover { background-color: white; }""")
        self.btn_add_row.setStyleSheet(btn_row_style)
        self.btn_rem_row.setStyleSheet(btn_row_style)

        self.row_controls.addWidget(self.btn_add_row)
        self.row_controls.addWidget(self.btn_rem_row)

        self.layout_table.addWidget(self.data_table, 0, Qt.AlignmentFlag.AlignLeft)
        self.layout_table.addLayout(self.row_controls)

        self.page_echantillon = QWidget()
        self.layout_ech_container = QVBoxLayout(self.page_echantillon)
        self.layout_ech_container.setContentsMargins(0, 10, 0, 0)

        self.ech_frame = QFrame()
        self.ech_frame.setStyleSheet("""
            QFrame { border: 2px solid #f7a359; border-radius: 10px; background-color: white; }
            QLabel { border: none; }
        """)
        self.layout_params = QFormLayout(self.ech_frame)
        self.layout_params.setContentsMargins(15, 15, 15, 15)
        self.layout_params.setSpacing(10)

        self.input_n = QLineEdit()
        self.input_k = QLineEdit("0")
        self.input_skew = QLineEdit()
        self.input_kurt = QLineEdit()

        self.layout_params.addRow(QLabel("Effectif n :"), self.input_n)
        self.layout_params.addRow(QLabel("Paramètre k :"), self.input_k)
        self.layout_params.addRow(QLabel("Skewness S :"), self.input_skew)
        self.layout_params.addRow(QLabel("Kurtosis K :"), self.input_kurt)

        self.layout_ech_container.addWidget(self.ech_frame)
        self.layout_ech_container.addStretch()

        self.input_stack.addWidget(self.page_table)
        self.input_stack.addWidget(self.page_echantillon)
        self.cp_layout.addWidget(self.input_stack)

        self.alpha_container = QHBoxLayout()
        self.input_alpha = QLineEdit("0.05")
        self.input_alpha.setFixedWidth(60)
        self.input_alpha.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.input_alpha.setStyleSheet("font-size: 12px; background-color: white; border: 1px solid #b5b5b5; border-radius: 8px;")
        self.alpha_container.addWidget(QLabel("Seuil de risque α :"))
        self.alpha_container.addWidget(self.input_alpha)
        self.alpha_container.addStretch()
        self.cp_layout.addLayout(self.alpha_container)

        self.cp_layout.addSpacing(10)
        self.btn_jb = QPushButton("TEST DE JARQUE-BERA")
        self.btn_lilliefors = QPushButton("TEST DE LILLIEFORS")

        btn_test_style = """
            QPushButton {{
                background-color: {color}; color: white; font-weight: bold;
                font-size: 14px; padding: 12px; border-radius: 6px; border: none;
            }}
            QPushButton:hover {{ background-color: {hover}; border-left: 3px solid {color2}; }}
            QPushButton:disabled {{ background-color: #f5f6fa; color: #bdc3c7; border: 1px solid #dcdde1; }}
        """
        self.btn_jb.setStyleSheet(btn_test_style.format(color="#44cf5b", hover="#4ede66", color2="#26a63b"))
        self.btn_lilliefors.setStyleSheet(btn_test_style.format(color="#67bcf5", hover="#3498db", color2="#1669a1"))

        self.cp_layout.addWidget(self.btn_jb)
        self.cp_layout.addWidget(self.btn_lilliefors)
        self.cp_layout.addStretch()

        self.display_area = QFrame()
        self.display_area.setStyleSheet("background-color: white; border: 1px solid #dee2e6; border-radius: 8px;")
        self.display_layout = QVBoxLayout(self.display_area)

        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setStyleSheet("border: none; background: transparent;")

        self.display_layout.addWidget(self.log_area)

        self.main_layout.addWidget(self.control_panel)
        self.main_layout.addWidget(self.display_area, 1)

        self.btn_mode_table.clicked.connect(lambda: self.switch_mode(0))
        self.btn_mode_echantillon.clicked.connect(lambda: self.switch_mode(1))
        self.btn_add_row.clicked.connect(self.add_row)
        self.btn_rem_row.clicked.connect(self.remove_row)
        self.btn_jb.clicked.connect(self.run_jb_test)
        self.btn_lilliefors.clicked.connect(self.run_lilliefors_test)

    def switch_mode(self, index):
        self.input_stack.setCurrentIndex(index)
        self.btn_lilliefors.setEnabled(index == 0)

    def add_row(self):
        self.data_table.insertRow(self.data_table.rowCount())
        self.data_table.setItem(self.data_table.rowCount() - 1, 0, QTableWidgetItem(""))

    def remove_row(self):
        if self.data_table.rowCount() > 1:
            self.data_table.removeRow(self.data_table.rowCount() - 1)

    def run_jb_test(self):
        try:
            alpha = float(self.input_alpha.text().replace(',', '.'))
            crit_val = stats.chi2.ppf(1 - alpha, df=2)

            data = []
            if self.input_stack.currentIndex() == 0:  # Mode Table X
                for i in range(self.data_table.rowCount()):
                    item = self.data_table.item(i, 0)
                    if item and item.text().strip():
                        data.append(float(item.text().replace(',', '.')))

                if len(data) < 2:
                    raise ValueError("Veuillez saisir au moins 2 valeurs dans la table.")

                n = len(data)
                k_val = 0
                x_bar = np.mean(data)
                diff = data - x_bar
                var_s2 = np.sum(diff ** 2) / (n - 1)
                skew_val = (np.sum(diff ** 3) / n) / (var_s2 ** 1.5)
                kurt_raw = (np.sum(diff ** 4) / n) / (var_s2 ** 2)
                jb_stat = ((n - k_val) / 6) * (skew_val ** 2 + ((kurt_raw - 3) ** 2 / 4))

                self.render_jb_table_results(n, k_val, x_bar, skew_val, kurt_raw, jb_stat, alpha, crit_val)
            else:
                n = int(self.input_n.text())
                k_val = int(self.input_k.text())
                skew_val = float(self.input_skew.text().replace(',', '.'))
                kurt_raw = float(self.input_kurt.text().replace(',', '.'))

                jb_stat = ((n - k_val) / 6) * (skew_val ** 2 + ((kurt_raw - 3) ** 2 / 4))

                self.render_jb_echantillon_results(n, k_val, skew_val, kurt_raw, jb_stat, alpha, crit_val)
        except Exception as e:
            self.log_area.setHtml(f"<b style='color:red;'>Erreur :</b> {str(e)}")

    def render_jb_table_results(self, n, k, x_bar, S, K, jb_stat, alpha, crit_val):
        is_normal = jb_stat < crit_val
        color = "#27ae60" if is_normal else "#e74c3c"
        reject_text = "on ne peut pas" if is_normal else "on peut"
        comp_symbol = "&lt;" if is_normal else "&gt;"

        html = f"<div style='font-size: 15px; color: #2c3e50; line-height: 1.7;'>"
        html += "<h1 style='text-align: center; border-bottom: 2px solid #52d98b; padding-bottom: 10px;'>Test de normalité de Jarque-Bera</h1>"

        html += f"<p>Ce test consiste à déterminer si les données X, avec <b>n = {n}</b> et <b>k = {k}</b> (une seule variable), suivent une loi normale au seuil de risque α = <b>{alpha}</b>.<br>Le test de Jarque-Bera utilise les parametres de forme des données : <b>skewness</b> et <b>kurtosis</b>.<br>On pose les hypothèses suivantes :</p>"
        html += "<p style='margin-left: 20px;'><b>H<sub>0</sub></b> : les données suivent une loi normale.<br>"
        html += "<b>H<sub>1</sub></b> : les données ne suivent pas une loi normale.</p>"

        html += "<p>Afin de calculer la statistique de Jarque-Bera pour déterminer au sens statistique si X suit une loi normale, on va calculer les termes suivants.</p>"

        html += f"""
        <div align="center" style="margin: 15px 0;">
            <table cellspacing="0" cellpadding="0" style="font-size: 18px; font-family: 'Times New Roman';">
                <tr>
                    <td style="vertical-align: middle;"><b>x̄</b> = </td>
                    <td style="padding: 0 5px;">
                        <table cellspacing="0" cellpadding="0" style="text-align: center; font-size: 14px;">
                            <tr><td style="border-bottom: 1px solid black;">1</td></tr>
                            <tr><td>n</td></tr>
                        </table>
                    </td>
                    <td style="vertical-align: middle;"> &times; <span style="font-size: 24px;">&sum;</span> </td>
                    <td style="vertical-align: middle; font-size: 11px;">
                        <table cellspacing="0" cellpadding="0">
                            <tr><td>n</td></tr>
                            <tr><td style="padding-top: 15px;">i=1</td></tr>
                        </table>
                    </td>
                    <td style="vertical-align: middle; padding-left: 5px;">x<sub>i</sub> = <b>{x_bar:.3f}</b></td>
                </tr>
            </table>
        </div>
        """

        html += f"""
        <div align="center" style="margin: 20px 0;">
            <table cellspacing="0" cellpadding="0" style="font-size: 18px; font-family: 'Times New Roman';">
                <tr>
                    <td style="vertical-align: middle;"><b>S (skew)</b> = </td>
                    <td style="padding: 0 10px;">
                        <table cellspacing="0" cellpadding="0" style="text-align: center; font-size: 14px;">
                            <tr><td style="text-align: center; border-bottom: 1px solid black; padding-bottom: 3px;">
                                1/{n} &sum; (x<sub>i</sub> - x̄)<sup>3</sup>
                            </td></tr>
                            <tr><td style="text-align: center; padding-top: 3px;">
                                [ 1/({n}-1) &sum; (x<sub>i</sub> - x̄)<sup>2</sup> ]<sup>3/2</sup>
                            </td></tr>
                        </table>
                    </td>
                    <td style="vertical-align: middle;"> = <b>{S:.3f}</b></td>
                </tr>
            </table>
        </div>
        """

        html += f"""
        <div align="center" style="margin: 20px 0;">
            <table cellspacing="0" cellpadding="0" style="font-size: 18px; font-family: 'Times New Roman';">
                <tr>
                    <td style="vertical-align: middle;"><b>K (kurt)</b> = </td>
                    <td style="padding: 0 10px;">
                        <table cellspacing="0" cellpadding="0" style="text-align: center; font-size: 14px;">
                            <tr><td style="text-align: center; border-bottom: 1px solid black; padding-bottom: 3px;">
                                1/{n} &sum; (x<sub>i</sub> - x̄)<sup>4</sup>
                            </td></tr>
                            <tr><td style="text-align: center; padding-top: 3px;">
                                [ 1/({n}-1) &sum; (x<sub>i</sub> - x̄)<sup>2</sup> ]<sup>2</sup>
                            </td></tr>
                        </table>
                    </td>
                    <td style="vertical-align: middle;"> = <b>{K:.3f}</b></td>
                </tr>
            </table>
        </div>
        """

        html += f"<p>la valeur critique du test de Jarque-Bera au seuil de risque α = <b>{alpha}</b> est : <b>{crit_val:.3f}</b></p>"
        html += "<p>Donc, la variable aléatoire X suit une loi normale si et seulement si :</p>"
        html += f"""
        <div align="center" style="margin: 20px 0;">
            <table cellspacing="0" cellpadding="0" style="font-size: 19px; font-family: 'Times New Roman';">
                <tr>
                    <td style="vertical-align: middle;"><b>JB</b> = </td>
                    <td style="padding: 0 5px;">
                        <table cellspacing="0" cellpadding="0" style="text-align: center; font-size: 15px;">
                            <tr><td style="border-bottom: 1px solid black; padding: 0 5px;">n - k</td></tr>
                            <tr><td style="text-align: center;">6</td></tr>
                        </table>
                    </td>
                    <td style="font-size: 38px; vertical-align: middle;"> ( </td>
                    <td style="vertical-align: middle;"> S<sup>2</sup> + </td>
                    <td style="padding: 0 5px;">
                        <table cellspacing="0" cellpadding="0" style="text-align: center; font-size: 15px;">
                            <tr><td style="border-bottom: 1px solid black; padding: 0 5px;">(K - 3)<sup>2</sup></td></tr>
                            <tr><td style="text-align: center;">4</td></tr>
                        </table>
                    </td>
                    <td style="font-size: 38px; vertical-align: middle;"> ) </td>
                    <td style="vertical-align: middle; padding-left: 10px;"> <b>&lt; {crit_val:.3f}</b></td>
                </tr>
            </table>
        </div>
        """

        html += f"""
        <div align="center" style="margin: 20px 0; color: black;">
            <table cellspacing="0" cellpadding="0" style="font-size: 18px; font-family: 'Times New Roman';">
                <tr>
                    <td style="vertical-align: middle;"><b>JB</b> = </td>
                    <td style="padding: 0 5px;">
                        <table cellspacing="0" cellpadding="0" style="text-align: center; font-size: 14px;">
                            <tr><td style="border-bottom: 1px solid black; padding: 0 5px;">{n} - {k}</td></tr>
                            <tr><td style="text-align: center;">6</td></tr>
                        </table>
                    </td>
                    <td style="font-size: 38px; vertical-align: middle;"> ( </td>
                    <td style="vertical-align: middle;"> ({S:.3f})<sup>2</sup> + </td>
                    <td style="padding: 0 5px;">
                        <table cellspacing="0" cellpadding="0" style="text-align: center; font-size: 14px;">
                            <tr><td style="border-bottom: 1px solid black; padding: 0 5px;">({K:.3f} - 3)<sup>2</sup></td></tr>
                            <tr><td style="text-align: center;">4</td></tr>
                        </table>
                    </td>
                    <td style="font-size: 38px; vertical-align: middle;"> ) </td>
                </tr>
            </table>
        </div>
        """

        html += f"<p align='center' style='font-size: 19px;'><b>JB = {jb_stat:.3f}</b></p>"

        html += f"""
        <div align="left" style="margin-top: 20px; padding: 15px; border: 2px solid {color}; border-radius: 10px;">
            Or, JB = {jb_stat:.3f} <b>{comp_symbol}</b> {crit_val:.3f}, donc <b>{reject_text}</b> rejeter H<sub>0</sub> au seuil de risque α = {alpha}. 
        </div>
        """

        html += "</div>"
        self.log_area.setHtml(html)

    def render_jb_echantillon_results(self, n, k, S, K, jb_stat, alpha, crit_val):

        is_normal = jb_stat < crit_val
        color = "#27ae60" if is_normal else "#e74c3c"
        reject_text = "on ne peut pas" if is_normal else "on peut"
        comp_symbol = "&lt;" if is_normal else "&gt;"

        html = f"<div style='font-size: 15px; color: #2c3e50; line-height: 1.7;'>"
        html += "<h1 style='text-align: center; border-bottom: 2px solid #f7a359; padding-bottom: 10px;'>Test de normalité de Jarque-Bera</h1>"

        html += f"<p>Ce test consiste à déterminer si les données X de l'échantillon, avec <b>n = {n}</b> et <b>k = {k}</b>, suivent une loi normale au seuil de risque α = <b>{alpha}</b>.<br>Le test de Jarque-Bera utilise les parametres de forme des données : <b>skewness</b> et <b>kurtosis</b>.<br>On pose les hypothèses suivantes :</p>"
        html += "<p style='margin-left: 20px;'><b>H<sub>0</sub></b> : les données suivent une loi normale.<br>"
        html += "<b>H<sub>1</sub></b> : les données ne suivent pas une loi normale.</p>"

        html += f"<p>Afin de calculer la statistique de Jarque-Bera, on utilise les paramètres de forme de l'échantillon saisis :<br>"
        html += f"&bull; Coefficient d'asymétrie <b>S (skew) = {S:.4f}</b><br>"
        html += f"&bull; Coefficient d'aplatissement <b>K (kurt)= {K:.4f}</b></p>"

        html += f"<p>La valeur critique du test de Jarque-Bera au seuil de risque α = <b>{alpha}</b> est : <b>{crit_val:.3f}</b></p>"

        html += "<p>Donc, la variable aléatoire X suit une loi normale si et seulement si :</p>"
        html += f"""
        <div align="center" style="margin: 20px 0;">
            <table cellspacing="0" cellpadding="0" style="font-size: 19px; font-family: 'Times New Roman';">
                <tr>
                    <td style="vertical-align: middle;"><b>JB</b> = </td>
                    <td style="padding: 0 5px;">
                        <table cellspacing="0" cellpadding="0" style="text-align: center; font-size: 15px;">
                            <tr><td style="border-bottom: 1px solid black; padding: 0 5px;">n - k</td></tr>
                            <tr><td style="text-align: center;">6</td></tr>
                        </table>
                    </td>
                    <td style="font-size: 38px; vertical-align: middle;"> ( </td>
                    <td style="vertical-align: middle;"> S<sup>2</sup> + </td>
                    <td style="padding: 0 5px;">
                        <table cellspacing="0" cellpadding="0" style="text-align: center; font-size: 15px;">
                            <tr><td style="border-bottom: 1px solid black; padding: 0 5px;">(K - 3)<sup>2</sup></td></tr>
                            <tr><td style="text-align: center;">4</td></tr>
                        </table>
                    </td>
                    <td style="font-size: 38px; vertical-align: middle;"> ) </td>
                    <td style="vertical-align: middle; padding-left: 10px;"> <b>&lt; {crit_val:.3f}</b></td>
                </tr>
            </table>
        </div>
        """

        html += f"""
        <div align="center" style="margin: 20px 0; color: black;">
            <table cellspacing="0" cellpadding="0" style="font-size: 18px; font-family: 'Times New Roman';">
                <tr>
                    <td style="vertical-align: middle;"><b>JB</b> = </td>
                    <td style="padding: 0 5px;">
                        <table cellspacing="0" cellpadding="0" style="text-align: center; font-size: 14px;">
                            <tr><td style="border-bottom: 1px solid black; padding: 0 5px;">{n} - {k}</td></tr>
                            <tr><td style="text-align: center;">6</td></tr>
                        </table>
                    </td>
                    <td style="font-size: 38px; vertical-align: middle;"> ( </td>
                    <td style="vertical-align: middle;"> ({S:.4f})<sup>2</sup> + </td>
                    <td style="padding: 0 5px;">
                        <table cellspacing="0" cellpadding="0" style="text-align: center; font-size: 14px;">
                            <tr><td style="border-bottom: 1px solid black; padding: 0 5px;">({K:.4f} - 3)<sup>2</sup></td></tr>
                            <tr><td style="text-align: center;">4</td></tr>
                        </table>
                    </td>
                    <td style="font-size: 38px; vertical-align: middle;"> ) </td>
                </tr>
            </table>
        </div>
        """

        html += f"<p align='center' style='font-size: 19px;'><b>JB = {jb_stat:.3f}</b></p>"

        html += f"""
        <div align="left" style="margin-top: 20px; padding: 15px; border: 2px solid {color}; border-radius: 10px;">
            Or, JB = {jb_stat:.3f} <b>{comp_symbol}</b> {crit_val:.3f}, donc <b>{reject_text}</b> rejeter H<sub>0</sub> au seuil de risque α = {alpha}. 
        </div>
        """

        html += "</div>"
        self.log_area.setHtml(html)

    def run_lilliefors_test(self):
        try:
            data = []
            for i in range(self.data_table.rowCount()):
                item = self.data_table.item(i, 0)
                if item and item.text().strip():
                    data.append(float(item.text().replace(',', '.')))

            if len(data) < 4:
                raise ValueError("Le test de Lilliefors nécessite au moins 4 observations.")

            data.sort()
            n = len(data)
            alpha = float(self.input_alpha.text().replace(',', '.'))

            x_bar = np.mean(data)
            s_std = np.std(data, ddof=1)

            rows_calc = []
            d_max = 0
            for i, x_val in enumerate(data):
                z_i = (x_val - x_bar) / s_std
                f_xi = stats.norm.cdf(z_i)
                s_xi = (i + 1) / n
                dist = abs(f_xi - s_xi)
                if dist > d_max:
                    d_max = dist

                rows_calc.append({
                    'xi': x_val, 'zi': z_i, 's_xi': s_xi, 'f_xi': f_xi, 'dist': dist
                })

            d_crit = self.get_lilliefors_crit(n, alpha)

            self.render_lilliefors_results(n, alpha, x_bar, s_std, rows_calc, d_max, d_crit)

        except Exception as e:
            self.log_area.setHtml(f"<b style='color:red;'>Erreur :</b> {str(e)}")

    def get_lilliefors_crit(self, n, alpha):
        table_05 = {
            4: 0.381, 5: 0.337, 6: 0.319, 7: 0.300, 8: 0.285, 9: 0.271, 10: 0.258,
            11: 0.249, 12: 0.242, 13: 0.234, 14: 0.227, 15: 0.222, 16: 0.216,
            17: 0.212, 18: 0.208, 19: 0.204, 20: 0.190, 25: 0.173, 30: 0.161
        }

        if abs(alpha - 0.05) < 1e-4 and n in table_05:
            return table_05[n]

        coeffs = {0.20: 0.736, 0.15: 0.768, 0.10: 0.805, 0.05: 0.886, 0.01: 1.031}
        c = coeffs.get(alpha, 0.886)
        return c / np.sqrt(n)

    def render_lilliefors_results(self, n, alpha, x_bar, sigma, rows, d_obs, d_crit):

        is_normal = d_obs < d_crit
        color = "#27ae60" if is_normal else "#e74c3c"
        comp_symbol = "&ge;" if d_obs >= d_crit else "&lt;"
        reject_text = "peut" if not is_normal else "ne peut pas"

        html = f"<div style='font-size: 15px; color: #2c3e50; line-height: 1.7;'>"
        html += "<h1 style='text-align: center; border-bottom: 2px solid #67bcf5; padding-bottom: 10px;'>Test de normalité de Lilliefors</h1>"

        html += f"<p>Ce test consiste à déterminer si les données X (n={n}), suivent une loi normale, au seuil de risque &alpha; = <b>{alpha}</b>.</p>"
        html += "<p>Le test de Lilliefors compare la distribution de l'échantillon et la distribution théorique si l'échantillon suivait vraiment une loi normale.</p>"

        html += "<p>On pose les hypothèses suivantes :<br>"
        html += "&nbsp;&nbsp;&nbsp;<b>H<sub>0</sub></b> : les données suivent une loi normale.<br>"
        html += "&nbsp;&nbsp;&nbsp;<b>H<sub>1</sub></b> : les données ne suivent pas une loi normale.</p>"

        html += f"<p>On calcule la moyenne <b>x̄ = {x_bar:.4f}</b>, et l'écart-type <b>&sigma; = {sigma:.4f}</b> de cet échantillon. "
        html += f"""
        <p>Ensuite, on dresse le tableau suivant où à chaque valeur <b>X<sub>i</sub></b>, on associe :
        <ul>
            <li style="margin-bottom: 10px;">
                <table cellspacing="0" cellpadding="0" style="display: inline-table; vertical-align: middle; font-size: 16px;">
                    <tr>
                        <td style="vertical-align: middle; padding-right: 5px;">sa valeur standardisée</td>
                        <td style="vertical-align: middle;"><b>Z<sub>i</sub></b> = </td>
                        <td style="padding: 0 5px;">
                            <table cellspacing="0" cellpadding="0" style="text-align: center; font-size: 13px;">
                                <tr><td style="border-bottom: 1px solid black; padding: 0 3px;">X<sub>i</sub> - x̄</td></tr>
                                <tr><td style="text-align: center;">&sigma;</td></tr>
                            </table>
                        </td>
                    </tr>
                </table>
            </li>
            <li>sa fréquence cumulée réelle <b>S(X<sub>i</sub>)</b></li>
            <li>sa fréquence cumulée théorique <b>F(X<sub>i</sub>)</b> 
                (si elle suivait une loi parfaitement normale)</li>
            <li>et enfin la distance absolue entre la fréquence réelle et la fréquence théorique 
                <b>|F(X<sub>i</sub>) - S(X<sub>i</sub>)|</b>.</li><br>
            </ul>
        </p>
        """

        html += """
        <table border="1" cellspacing="0" cellpadding="5" style="width:100%; border-collapse:collapse; text-align:center; font-size:15px;">
            <tr style="background-color:#f8f9fa;">
                <th>X<sub>i</sub></th>
                <th>Z<sub>i</sub></th>
                <th>S(X<sub>i</sub>) <br></th>
                <th>F(X<sub>i</sub>) <br></th>
                <th>|F(X<sub>i</sub>) - S(X<sub>i</sub>)|</th>
            </tr>
        """
        for r in rows:
            html += f"""
            <tr>
                <td>{r['xi']:.3f}</td>
                <td>{r['zi']:.3f}</td>
                <td>{r['s_xi']:.3f}</td>
                <td>{r['f_xi']:.3f}</td>
                <td style="font-weight:bold; text-align: center;">{r['dist']:.4f}</td>
            </tr>
            """
        html += "</table><br>"

        html += f"<p>On rejette l'hypothèse de normalité si la valeur <b>D = max |F(X) - S(X)|</b> est supérieure à la valeur critique <b>D<sub>max</sub> = {d_crit:.4f}</b>, obtenue dans la table suivante :</p>"

        alphas = [0.20, 0.15, 0.10, 0.05, 0.01]
        html += """<table border="1" cellspacing="0" cellpadding="5" style="width:85%; margin:auto; border-collapse:collapse; text-align:center; font-size:12px;">
                    <tr style="background-color:#e1f5fe;"><th>&alpha; (Risque)</th>"""

        for a in alphas:
            bg = "background-color:#fff3cd; font-weight:bold;" if abs(a - alpha) < 1e-4 else ""
            html += f"<td style='{bg}'>{a}</td>"

        html += "</tr><tr><th>D<sub>crit</sub></th>"

        for a in alphas:
            val_col = self.get_lilliefors_crit(n, a)
            bg = "background-color:#fff3cd; font-weight:bold;" if abs(a - alpha) < 1e-4 else ""
            html += f"<td style='{bg}'>{val_col:.4f}</td>"

        html += "</tr></table>"

        html += f"""
        <div align="center" style="margin-top: 20px; padding: 15px; border: 2px solid {color}; border-radius: 10px;">
            <p style="font-size: 17px; margin:0;">
                Or, <b>D = {d_obs:.4f} {comp_symbol} D<sub>max</sub> ({d_crit:.3f})</b>, 
                on <b>{reject_text}</b> rejeter l'hypothèse <b>H<sub>0</sub></b> au seuil de risque &alpha; = {alpha}.
            </p>
        </div>
        """

        html += "</div>"
        self.log_area.setHtml(html)