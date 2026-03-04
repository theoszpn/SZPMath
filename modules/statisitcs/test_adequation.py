from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                               QPushButton, QTextEdit, QLabel, QSpinBox,
                               QLineEdit, QComboBox, QTableWidgetItem, QFrame)
from PySide6.QtCore import Qt
import math
from scipy import stats


class ChiSquareAdequacyPage(QWidget):
    def __init__(self):
        super().__init__()
        self.col_width = 60
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("""
            QWidget { color: black; font-family: 'Segoe UI'; }
            QLabel { font-weight: bold; color: #2f3640; }

            QTableWidget { background-color: white; border: 1px solid #bdc3c7; }
            QHeaderView::section { 
                background-color: #f8f9fa; 
                color: #2f3640; 
                font-weight: bold; 
                border: 1px solid #bdc3c7;
                padding: 4px;
            }

            QComboBox { 
                background-color: white; 
                border: 1px solid #bdc3c7; 
                padding: 5px; 
            }
            QComboBox QAbstractItemView {
                background-color: white;
                selection-background-color: #3498db;
                selection-color: white;
                outline: none;
            }

            QLineEdit, QSpinBox, QTextEdit {
                background-color: white; border: 1px solid #bdc3c7; padding: 4px;
            }

            QPushButton { background-color: #2980b9; color: white; font-weight: bold; border-radius: 4px; padding: 10px; }
            QPushButton:hover { background-color: #3498db; }
        """)

        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(25)

        left_container = QFrame()
        left_container.setFixedWidth(300)
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(15)
        left_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        row_ctrl_layout = QHBoxLayout()
        self.spin_k = QSpinBox()
        self.spin_k.setRange(2, 50)
        self.spin_k.setValue(5)
        self.spin_k.setFixedWidth(80)
        row_ctrl_layout.addWidget(QLabel("Catégories (k) :"))
        row_ctrl_layout.addWidget(self.spin_k)
        row_ctrl_layout.addStretch()
        left_layout.addLayout(row_ctrl_layout)

        self.table = QTableWidget(5, 2)
        self.table.setFixedHeight(400)
        self.table.setHorizontalHeaderLabels(["X", "nᵢ"])
        self.table.verticalHeader().setVisible(False)
        self.apply_column_widths()
        self.refresh_table_rows()
        left_layout.addWidget(self.table)

        left_layout.addWidget(QLabel("Loi théorique :"))
        self.combo_laws = QComboBox()
        self.combo_laws.addItems([
            "Loi Uniforme",
            "Loi Binomiale",
            "Loi Poisson",
            "Proportions custom"
        ])
        self.combo_laws.setFixedWidth(250)
        left_layout.addWidget(self.combo_laws)

        self.param_container = QWidget()
        self.param_layout = QVBoxLayout(self.param_container)
        self.param_layout.setContentsMargins(0, 0, 0, 0)

        self.row_p = QWidget()
        layout_p = QHBoxLayout(self.row_p)
        layout_p.setContentsMargins(0, 0, 0, 0)
        layout_p.addWidget(QLabel("p :"))
        self.input_p = QLineEdit("0.5")
        self.input_p.setFixedWidth(70)
        layout_p.addWidget(self.input_p)
        layout_p.addStretch()
        self.param_layout.addWidget(self.row_p)
        self.row_p.hide()

        self.row_lambda = QWidget()
        layout_lambda = QHBoxLayout(self.row_lambda)
        layout_lambda.setContentsMargins(0, 0, 0, 0)
        layout_lambda.addWidget(QLabel("λ :"))
        self.input_lambda = QLineEdit("1.0")
        self.input_lambda.setFixedWidth(70)
        layout_lambda.addWidget(self.input_lambda)
        layout_lambda.addStretch()
        self.param_layout.addWidget(self.row_lambda)
        self.row_lambda.hide()

        left_layout.addWidget(self.param_container)

        alpha_layout = QHBoxLayout()
        alpha_layout.addWidget(QLabel("Seuil alpha (α) :"))
        self.input_alpha = QLineEdit("0.05")
        self.input_alpha.setFixedWidth(70)
        alpha_layout.addWidget(self.input_alpha)
        alpha_layout.addStretch()
        left_layout.addLayout(alpha_layout)

        self.btn_analyze = QPushButton("➜ TEST D'ADÉQUATION")
        self.btn_analyze.setFixedWidth(250)
        left_layout.addWidget(self.btn_analyze)

        right_column = QVBoxLayout()
        right_column.addWidget(QLabel("Analyse"))
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setStyleSheet("font-size: 16px; border: 2px solid #bdc3c7;")
        right_column.addWidget(self.log_area)

        self.main_layout.addWidget(left_container)
        self.main_layout.addLayout(right_column)

        self.spin_k.valueChanged.connect(self.refresh_table_rows)
        self.combo_laws.currentIndexChanged.connect(self.on_model_changed)
        self.btn_analyze.clicked.connect(self.run_adequacy_test)

    def apply_column_widths(self):
        for i in range(self.table.columnCount()):
            self.table.setColumnWidth(i, self.col_width)
        total_w = (self.table.columnCount() * self.col_width) + 2
        self.table.setFixedWidth(total_w)

    def to_subscript(self, i):
        sub_map = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
        return str(i).translate(sub_map)

    def refresh_table_rows(self):
        k = self.spin_k.value()
        self.table.setRowCount(k)
        for i in range(k):
            item_x = QTableWidgetItem(f"X{self.to_subscript(i + 1)}")
            item_x.setFlags(Qt.ItemFlag.ItemIsEnabled)
            item_x.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_x.setBackground(Qt.GlobalColor.lightGray)
            self.table.setItem(i, 0, item_x)
            if not self.table.item(i, 1):
                self.table.setItem(i, 1, QTableWidgetItem(""))
        self.apply_column_widths()

    def on_model_changed(self):
        model = self.combo_laws.currentText()
        self.row_p.hide()
        self.row_lambda.hide()

        if model == "Loi Binomiale":
            self.row_p.show()
            self.set_custom_col_visible(False)
        elif model == "Loi Poisson":
            self.row_lambda.show()
            self.set_custom_col_visible(False)
        elif model == "Proportions custom":
            self.set_custom_col_visible(True)
        else:
            self.set_custom_col_visible(False)
        self.apply_column_widths()

    def set_custom_col_visible(self, visible):
        if visible:
            self.table.setColumnCount(3)
            self.table.setHorizontalHeaderLabels(["X", "nᵢ", "fᵢ"])
        else:
            self.table.setColumnCount(2)
            self.table.setHorizontalHeaderLabels(["X", "nᵢ"])

    def make_html_fraction(self, num, den, prefix=""):
        return f"""
        <table cellspacing="0" cellpadding="0" style="display: inline-table; vertical-align: middle; font-family: 'Times New Roman'; font-size: 18px;">
            <tr>
                <td rowspan="2" style="vertical-align: middle; padding-right: 5px;">{prefix}</td>
                <td style="border-bottom: 1px solid black; text-align: center; padding: 0 5px;">{num}</td>
            </tr>
            <tr>
                <td style="text-align: center; padding: 0 5px;">{den}</td>
            </tr>
        </table>
        """

    def make_summation_formula(self, k, result):
        return f"""
        <table cellspacing="0" cellpadding="0" style="display: inline-table; vertical-align: middle; font-family: 'Times New Roman'; font-size: 18px;">
            <tr>
                <td rowspan="3" style="vertical-align: middle; padding-right: 8px;">&chi;&sup2;<sub>obs</sub> = </td>
                <td style="text-align: center; font-size: 12px;">{k}</td>
                <td rowspan="3" style="vertical-align: middle; padding-left: 8px;">
                    <table cellspacing="0" cellpadding="0" style="text-align: center;">
                        <tr><td style="border-bottom: 1px solid black; padding: 0 5px;">(nᵢ - eᵢ)&sup2;</td></tr>
                        <tr><td style="text-align: center;">eᵢ</td></tr>
                    </table>
                </td>
                <td rowspan="3" style="vertical-align: middle; padding-left: 10px;"> = <b>{result:.4f}</b></td>
            </tr>
            <tr><td style="text-align: center; font-size: 28px; line-height: 22px;">&sum;</td></tr>
            <tr><td style="text-align: center; font-size: 12px;">i=1</td></tr>
        </table>
        """

    def get_law_html(self, law_type, k):
        if law_type == "Loi Uniforme":
            return self.make_html_fraction("1", "k", "pᵢ = ")

        elif law_type == "Loi Binomiale":
            p = self.input_p.text()
            return f"""
            <table cellspacing="0" cellpadding="0" style="display: inline-table; vertical-align: middle; font-family: 'Times New Roman'; font-size: 18px;">
                <tr>
                    <td rowspan="2" style="vertical-align: middle; padding-right: 5px;">pᵢ = P(X=i) = </td>
                    <td rowspan="2" style="vertical-align: middle; padding-left: 5px; font-size: 22px;">(</td>
                    <td style="font-size: 12px; text-align: center;">{k - 1}</td>
                    <td rowspan="2" style="vertical-align: middle; padding-left: 5px; font-size: 22px;">)</td>
                    <td rowspan="2" style="vertical-align: middle; padding-left: 5px;"> &middot; {p}<sup>i</sup> &middot; (1 - {p})<sup>({k - 1}-i)</sup></td>
                </tr>
                <tr>
                    <td style="font-size: 12px; text-align: center;">i</td>
                </tr>
            </table>
            """

        elif law_type == "Loi Poisson":
            l = self.input_lambda.text()
            num = f"e<sup>-{l}</sup> &middot; {l}<sup>i</sup>"
            den = "i!"
            return self.make_html_fraction(num, den, "pᵢ = P(X=i) = ")

        return "pᵢ : Définie par l'utilisateur"

    def run_adequacy_test(self):
        try:
            k = self.spin_k.value()
            alpha = float(self.input_alpha.text().replace(',', '.'))
            obs = []
            for i in range(k):
                item = self.table.item(i, 1)
                if not item or not item.text().strip():
                    raise ValueError(f"Effectif X{self.to_subscript(i + 1)} manquant.")
                obs.append(float(item.text().replace(',', '.')))

            n_total = sum(obs)
            law_type = self.combo_laws.currentText()
            probs = []

            if law_type == "Loi Uniforme":
                probs = [1 / k] * k
            elif law_type == "Loi Binomiale":
                p_param = float(self.input_p.text().replace(',', '.'))
                for i in range(k):
                    probs.append(math.comb(k - 1, i) * (p_param ** i) * ((1 - p_param) ** (k - 1 - i)))
            elif law_type == "Loi Poisson":
                l_param = float(self.input_lambda.text().replace(',', '.'))
                for i in range(k):
                    probs.append((math.exp(-l_param) * (l_param ** i)) / math.factorial(i))
                s_p = sum(probs)
                probs = [p / s_p for p in probs]
            elif law_type == "Proportions custom":
                for i in range(k):
                    item = self.table.item(i, 2)
                    if not item: raise ValueError(f"Proportion f{self.to_subscript(i + 1)} manquante.")
                    probs.append(float(item.text().replace(',', '.')))
                if sum(probs) > 1.5: probs = [p / 100 for p in probs]

            chi_obs = 0
            rows_html = ""
            for i in range(k):
                ei = n_total * probs[i]
                contrib = ((obs[i] - ei) ** 2) / ei if ei > 0 else 0
                chi_obs += contrib

                style_ei = "color: #e67e22; font-weight: bold;" if ei < 5 else ""
                rows_html += f"""
                <tr>
                    <td style="background: #f8f9fa;">X{self.to_subscript(i + 1)}</td>
                    <td>{obs[i]}</td>
                    <td>{probs[i]:.4f}</td>
                    <td style="{style_ei}">{ei:.2f}</td>
                    <td style="background: #fdfefe;"><b>{contrib:.4f}</b></td>
                </tr>"""

            ddl = k - 1
            chi_crit = stats.chi2.ppf(1 - alpha, ddl)

            html = f"<div style='font-family: Segoe UI; color: black;'>"
            html += f"<h1 style='color: #2980b9; border-bottom: 2px solid #2980b9;'>Test d'Adéquation : {law_type}</h1>"

            html += f"<p>Ce test permet de vérifier si les données observées (n = <b>{n_total}</b>) suivent une {law_type} au seuil &alpha; = <b>{alpha}</b>, en comparant la distribution de l'échantillon à la distribution théorique de la loi.</p>"
            html += "<p>On pose les hypothèse suivantes :</p>"
            html += f"<p><b>H₀</b> : L'échantillon a une distribution en adéquation la loi.<br><b>H₁</b> : L'échantillon n'a pas une distribution en adéquation avec la loi.</p>"

            html += "<p>On calcule la probabilité théorique <b>p<sub>i</sub></b> pour ensuite obtenir les effectifs théoriques <b>e<sub>i</sub></b> :"
            html += f"<div style='margin: 20px 0;' align='left'>{self.get_law_html(law_type, k)}</div>"
            html += f"<div style='margin: 20px 0;' align='left'><span style=\"font-family: 'Times New Roman'; font-size: 20px;\">eᵢ = n &middot; pᵢ</span></div>"

            html += f"<div>On dresse ensuite le tableau regroupant effectifs observés n<sub>i</sub> , probabilités p<sub>i</sub> selon la {law_type}, effectifs théoriques e<sub>i</sub>  et l'écart normalisé (nᵢ-eᵢ)&sup2;/eᵢ :"
            html += f"""
            <table border="1" cellspacing="0" cellpadding="8" style="border-collapse: collapse; width: 100%; text-align: center; border: 1px solid #bdc3c7;">
                <tr style="background: #2c3e50; color: white;">
                    <th>Catégorie</th><th>nᵢ</th><th>pᵢ</th><th>eᵢ</th><th>(nᵢ-eᵢ)&sup2;/eᵢ</th>
                </tr>
                {rows_html}
            </table>"""

            html += f"<div style='margin-top: 20px;'>On calcule la statistique suivante :</div>"
            html += f"<div style='margin: 15px 0;' align='center'>{self.make_summation_formula(k, chi_obs)}</div>"

            html += f"<p>Le degré de liberté pour ce test est <b>ddl = k - 1 = {ddl}</b>.</p>"

            html += f"<p>Table des valeurs critiques du Khi-deux pour ddl = {ddl} :</p>"
            target_alphas = [0.2, 0.1, 0.05, 0.01, 0.001]
            html += """<table border="1" cellspacing="0" cellpadding="8" style="border-collapse: collapse; text-align: center; border: 1px solid #bdc3c7;">
                <tr style="background: #f8f9fa;"><th>&alpha;</th>"""
            for a in target_alphas:
                style = "background: #3498db; color: white;" if abs(a - alpha) < 0.0001 else ""
                html += f"<th style='{style}'>{a}</th>"
            html += "</tr><tr><td style='font-weight: bold;'>&chi;&sup2;<sub>crit</sub></td>"
            for a in target_alphas:
                val_crit = stats.chi2.ppf(1 - a, ddl)
                style = "background: #ebf5fb; font-weight: bold;" if abs(a - alpha) < 0.0001 else ""
                html += f"<td style='{style}'>{val_crit:.3f}</td>"
            html += "</tr></table>"

            decision = "<b style='color: #b01319;'>rejetons l'hypothèse nulle H₀</b>" if chi_obs > chi_crit else "<b style='color: #00a113;'>ne pouvons pas rejeter H₀</b>"
            verdict = "l'échantillon ne suit pas la loi théorique" if chi_obs > chi_crit else "l'échantillon suit la loi théorique"
            color = "#e74c3c" if chi_obs > chi_crit else "#27ae60"

            html += "<p>On rejette l'hypothèse <b>H₀</b> si &chi;&sup2;<sub>obs</sub> &gt; &chi;&sup2;<sub>crit</sub>.</p>"
            html += f"""<div style='font-size: 20px; margin-top: 25px; padding: 15px; border: 2px solid {color}; border-radius: 8px; background: #fafafa;'>
                Or, &chi;&sup2;<sub>obs</sub> ({chi_obs:.4f}) {'&gt;' if chi_obs > chi_crit else '&le;'} &chi;&sup2;<sub>crit</sub> ({chi_crit:.3f}).<br>
                Nous <b>{decision}</b> : <b>{verdict}</b> au seuil de {alpha * 100}%.
            </div>"""

            html += "</div>"
            self.log_area.setHtml(html)

        except Exception as e:
            self.log_area.setHtml(f"<b style='color:red;'>Erreur :</b> {str(e)}")