from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                               QPushButton, QTextEdit, QLabel, QSpinBox,
                               QLineEdit, QButtonGroup, QTableWidgetItem, QFrame)
from PySide6.QtCore import Qt
import numpy as np
import io
import base64
import matplotlib.pyplot as plt
from scipy import stats

class CorrelationPearsonPage(QWidget):
    def __init__(self):
        super().__init__()
        self.cell_size_w = 90
        self.cell_size_h = 40
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("""
            QWidget { 
                color: black; 
                font-family: 'Segoe UI', Arial;
            }
            QLabel { 
                font-weight: bold; 
                color: #2f3640; 
            }
            QLineEdit, QSpinBox, QTableWidget, QTextEdit {
                background-color: white;
                color: black;
                border: 1px solid #bdc3c7;
            }
            QPushButton {
                color: black;
            }
            QSpinBox {
                padding: 2px;
            }
        """)

        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(25)

        left_container = QFrame()
        left_container.setFixedWidth(350)
        left_column = QVBoxLayout(left_container)
        left_column.setContentsMargins(0, 0, 0, 0)
        left_column.setSpacing(10)
        left_column.setAlignment(Qt.AlignmentFlag.AlignTop)

        dims_layout = QHBoxLayout()
        dims_layout.setSpacing(10)

        self.spin_n = QSpinBox()
        self.spin_n.setRange(3, 100)
        self.spin_n.setValue(6)
        self.spin_n.setFixedWidth(65)

        self.spin_vars_x = QSpinBox()
        self.spin_vars_x.setRange(1, 5)
        self.spin_vars_x.setValue(1)
        self.spin_vars_x.setFixedWidth(65)

        dims_layout.addWidget(QLabel("Effectif n :"))
        dims_layout.addWidget(self.spin_n)
        dims_layout.addStretch()

        left_column.addLayout(dims_layout)

        self.table = QTableWidget(7, 2)
        self.setup_table_style()
        self.refresh_table_headers()
        left_column.addWidget(self.table)

        alpha_layout = QHBoxLayout()
        alpha_layout.addWidget(QLabel("Seuil alpha (α) :"))
        self.input_alpha = QLineEdit("0.05")
        self.input_alpha.setFixedWidth(65)
        alpha_layout.addWidget(self.input_alpha)
        alpha_layout.addStretch()
        left_column.addLayout(alpha_layout)

        left_column.addSpacing(5)
        left_column.addWidget(QLabel("Modèle de régression :"))

        self.model_group = QButtonGroup(self)
        self.model_group.setExclusive(True)

        models = [
            ("Linéaire", "linear"),
            ("Exponentiel", "exponential"),
            ("Puissance", "power"),
            ("Logarithmique", "log")
        ]

        toggle_style = """
            QPushButton { 
                background-color: #f1f2f6; border: 1px solid #ced4da; 
                padding: 6px; border-radius: 4px; 
            }
            QPushButton:checked { 
                background-color: #34495e; color: white; font-weight: bold; 
            }
            QPushButton:hover { background-color: #dfe4ea; }
        """

        model_btns_layout = QVBoxLayout()
        model_btns_layout.setSpacing(4)
        for text, key in models:
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.setProperty("model_key", key)
            btn.setStyleSheet(toggle_style)
            if key == "linear": btn.setChecked(True)
            self.model_group.addButton(btn)
            model_btns_layout.addWidget(btn)
        left_column.addLayout(model_btns_layout)

        self.btn_analyze = QPushButton("➜ LANCER L'ANALYSE")
        self.btn_analyze.setStyleSheet("""
            QPushButton { background-color: #2980b9; color: white; padding: 15px; font-weight: bold; border-radius: 5px; }
        """)

        left_column.addWidget(self.btn_analyze)
        left_column.addStretch()

        right_column = QVBoxLayout()
        lbl_res = QLabel("Étapes de résolution & Graphiques")
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setStyleSheet("font-size: 18px; padding: 10px; border: 2px solid #bdc3c7;")

        right_column.addWidget(lbl_res)
        right_column.addWidget(self.log_area)

        self.main_layout.addWidget(left_container)
        self.main_layout.addLayout(right_column)

        self.spin_n.valueChanged.connect(self.update_table_dims)
        self.spin_vars_x.valueChanged.connect(self.update_table_dims)

        self.btn_analyze.clicked.connect(self.run_analysis)

    def setup_table_style(self):
        self.table.horizontalHeader().setVisible(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setStyleSheet("font-weight: bold; font-size: 15px;")
        self.table.itemChanged.connect(lambda item: item.setTextAlignment(Qt.AlignmentFlag.AlignCenter))

    def to_subscript(self, n):
        sub_map = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
        return str(n).translate(sub_map)

    def refresh_table_headers(self):
        self.table.blockSignals(True)

        item_x = QTableWidgetItem("X")
        item_x.setFlags(Qt.ItemFlag.ItemIsEnabled)
        item_x.setBackground(Qt.GlobalColor.lightGray)
        item_x.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(0, 0, item_x)

        item_y = QTableWidgetItem("y")
        item_y.setFlags(Qt.ItemFlag.ItemIsEnabled)
        item_y.setBackground(Qt.GlobalColor.lightGray)
        item_y.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(0, 1, item_y)

        self.table.blockSignals(False)
        self.adjust_table_size()

    def update_table_dims(self):
        self.table.setRowCount(self.spin_n.value() + 1)
        self.table.setColumnCount(2)
        self.refresh_table_headers()

    def adjust_table_size(self):
        cols, rows = self.table.columnCount(), self.table.rowCount()
        for j in range(cols): self.table.setColumnWidth(j, self.cell_size_w)
        for i in range(rows): self.table.setRowHeight(i, self.cell_size_h)
        th = (rows * self.cell_size_h) + 2
        self.table.setFixedHeight(min(th, 350))
        tw = (cols * self.cell_size_w) + 2
        self.table.setFixedWidth(min(tw, 330))


    def make_math_fraction(self, num, den, prefix="", suffix="", is_inline=True):
        display = "inline-table" if is_inline else "table"
        return f"""
        <table cellspacing="0" cellpadding="0" style="display: {display}; vertical-align: middle; font-family: 'Times New Roman';">
            <tr>
                <td rowspan="2" style="vertical-align: middle; padding-right: 5px;">{prefix}</td>
                <td style="border-bottom: 1px solid black; text-align: center; padding: 0 5px;">{num}</td>
                <td rowspan="2" style="vertical-align: middle; padding-left: 5px;">{suffix}</td>
            </tr>
            <tr>
                <td style="text-align: center; padding: 0 5px;">{den}</td>
            </tr>
        </table>
        """

    def make_sqrt_fraction(self, num, den, prefix=""):
        return f"""
        <table cellspacing="0" cellpadding="0" style="display: inline-table; vertical-align: middle;">
            <tr>
                <td rowspan="2" style="vertical-align: middle; padding-right: 2px;">{prefix}</td>
                <td rowspan="2" style="vertical-align: middle; font-size: 24px;">&radic;</td>
                <td style="border-top: 1px solid black; border-bottom: 1px solid black; text-align: center; padding: 2px 5px 0 5px;">{num}</td>
            </tr>
            <tr>
                <td style="border-top: 1px solid black; text-align: center; padding: 0 5px;">{den}</td>
            </tr>
        </table>
        """

    def get_plot_b64(self, x, y, a=None, b=None):
        plt.figure(figsize=(5, 3.5))
        plt.scatter(x, y, color='#2980b9', s=40, label='Observations')
        if a is not None and b is not None:
            x_range = np.array([min(x), max(x)])
            plt.plot(x_range, a * x_range + b, color='#e74c3c', linewidth=2, label=f'y = {a:.3f}x + {b:.3f}')

        plt.xlabel('X')
        plt.ylabel('y')
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        plt.close()
        return base64.b64encode(buf.getvalue()).decode('utf-8')

    def make_summation_formula(self, n_val, result_val):
        return f"""
        <table cellspacing="0" cellpadding="0" style="display: inline-table; vertical-align: middle; font-family: 'Times New Roman'; font-size: 16px;">
            <tr>
                <td rowspan="3" style="vertical-align: middle; padding-right: 5px;">C<sub>xy</sub> = </td>
                <td rowspan="3" style="vertical-align: middle; padding-right: 5px;">
                    <table cellspacing="0" cellpadding="0" style="text-align: center; font-size: 13px;">
                        <tr><td style="border-bottom: 1px solid black;">1</td></tr>
                        <tr><td>n</td></tr>
                    </table>
                </td>
                <td style="text-align: center; font-size: 11px;">{n_val}</td>
                <td rowspan="3" style="vertical-align: middle; padding-left: 5px;">(x<sub>i</sub> - x̄)(y<sub>i</sub> - ȳ) = <b>{result_val:.3f}</b></td>
            </tr>
            <tr>
                <td style="text-align: center; font-size: 24px; line-height: 20px;">&sum;</td>
            </tr>
            <tr>
                <td style="text-align: center; font-size: 11px;">i=1</td>
            </tr>
        </table>
        """

    def make_complex_fraction(self, num, den, result, prefix=""):
        return f"""
        <table cellspacing="0" cellpadding="0" style="display: inline-table; vertical-align: middle; font-family: 'Times New Roman'; font-size: 16px;">
            <tr>
                <td style="vertical-align: middle; padding-right: 5px;">{prefix} = </td>
                <td style="padding: 0 5px;">
                    <table cellspacing="0" cellpadding="0" style="text-align: center; font-size: 14px;">
                        <tr><td style="border-bottom: 1px solid black; padding: 0 5px;">{num}</td></tr>
                        <tr><td>{den}</td></tr>
                    </table>
                </td>
                <td style="vertical-align: middle; padding-left: 5px;"> = <b>{result}</b></td>
            </tr>
        </table>
        """

    def run_analysis(self):
        selected_button = self.model_group.checkedButton()
        if not selected_button:
            return

        model_key = selected_button.property("model_key")

        if model_key == "linear":
            self.run_linear_analysis()
        elif model_key == "exponential":
            self.run_exponential_analysis()
        elif model_key == "power":
            self.run_power_analysis()
        elif model_key == "log":
            self.run_logarithmic_analysis()

    def run_linear_analysis(self):
        try:
            n_rows = self.spin_n.value()
            x_raw, y_raw = [], []
            for i in range(1, n_rows + 1):
                item_x = self.table.item(i, 0)
                item_y = self.table.item(i, 1)
                if item_y and item_x and item_y.text().strip() and item_x.text().strip():
                    y_raw.append(float(item_y.text().replace(',', '.')))
                    x_raw.append(float(item_x.text().replace(',', '.')))

            n = len(x_raw)
            if n < 3:
                raise ValueError("Le test nécessite au moins 3 couples de données.")

            X, Y = np.array(x_raw), np.array(y_raw)
            alpha = float(self.input_alpha.text().replace(',', '.'))

            mx, my = np.mean(X), np.mean(Y)
            vx, vy = np.var(X), np.var(Y)
            sx, sy = np.sqrt(vx), np.sqrt(vy)

            cxy = np.mean(X * Y) - (mx * my)
            r = cxy / (sx * sy)
            r2 = r ** 2

            df = n - 2
            t_stat = r * np.sqrt(df) / np.sqrt(1 - r2) if abs(r) < 1 else 0
            t_crit = stats.t.ppf(1 - alpha / 2, df)

            slope, intercept, r_value, p_value, std_err = stats.linregress(X, Y)
            a = slope
            b = intercept

            html = "<div style='font-family: Segoe UI; color: black; line-height: 1.6;'>"
            html += "<h1 style='color: #2980b9; border-bottom: 2px solid #2980b9;'>Test de Corrélation : Modèle Linéaire <br>(y = ax + b)</h1>"

            html += "<p>Dans ce test, on cherche à déterminer si deux variables aléatoires sont correlées. On considère les données X (variable explicative) et y (variable \"à expliquer\") :</p><br>"

            html += f"""
            <table border="1" cellspacing="0" cellpadding="8" style="border-collapse: collapse; text-align: center; width: 100%; margin-bottom: 15px;">
                <tr style="background: #ecf0f1;"><td><b>X</b></td>""" + "".join(
                [f"<td>{v:.2f}</td>" for v in X]) + "</tr>"
            html += f"""<tr><td><b>y</b></td>""" + "".join([f"<td>{v:.2f}</td>" for v in Y]) + "</tr></table>"

            img_cloud = self.get_plot_b64(X, Y)
            html += f"<div style='text-align: center; margin-bottom: 20px;'><img src='data:image/png;base64,{img_cloud}' width='350'></div>"

            html += "<p>On calcule d'abord la moyenne, la variance et l'écart type pour X et y :</p>"
            html += f"<div>X : x̄ = <b>{mx:.3f}</b> ; V<sub>x</sub> = <b>{vx:.3f}</b> ; &sigma;<sub>x</sub> = <b>{sx:.3f}</b></div>"
            html += f"<div>y : ȳ = <b>{my:.3f}</b> ; V<sub>y</sub> = <b>{vy:.3f}</b> ; &sigma;<sub>y</sub> = <b>{sy:.3f}</b></div>"

            html += "<p>On calcule ensuite la covariance C<sub>xy</sub> et le coefficient de corrélation linéaire R<sub>xy</sub> :</p>"
            html += f"<div style='margin-bottom: 10px;'>{self.make_summation_formula(n, cxy)}</div>"

            r_num = f"{cxy:.3f}"
            r_den = f"{sx:.3f} &times; {sy:.3f}"
            html += f"<div>{self.make_complex_fraction(r_num, r_den, f'{r:.3f}', 'R<sub>xy</sub> = C<sub>xy</sub> / (&sigma;<sub>x</sub>&sigma;<sub>y</sub>)')}</div>"

            html += f"""<p><b>Interprétation</b> : le coefficient de correlation linéaire R<sub>xy</sub> (toujours compris entre -1 et 1) permet de connaitre la nature de la relation entre X et y.<br><br>
            - Si R<sub>xy</sub> est proche de <b style="color: #575757;">0</b>, il n'y a pas ou peu de correlation linéaire.<br>
            - Si R<sub>xy</sub> est proche de <b style="color: #30b4cf;">1</b>, il y a une correlation linéaire forte <b style="color: #30b4cf;">(croissante)</b>.<br>
            - Si R<sub>xy</sub> est proche de <b style="color: #b32222;">-1</b>, il y a une correlation linéaire forte <b style="color: #b32222;">(décroissante)</b>.</p>"""

            qualif = "nulle"
            if abs(r) > 0.8:
                qualif = "forte " + ("(croissante)" if r > 0 else "(décroissante)")
            elif abs(r) > 0.5:
                qualif = "moyenne"
            html += f"<p>Ici R<sub>xy</sub> = <b>{r:.3f}</b>, donc il semble y avoir une corrélation linéaire <b>{qualif}</b>.</p>"

            html += f"""<p>Nous avons calculé le coefficient de correlation pour les données de l'échantillon. Nous pouvons maintenant tester si le coefficient de corrélation est significativement différent de 0. Dans cette partie, on notera R<sub>xy</sub> = r. On pose les hypothèses suivantes :<br><br>
            <b>H<sub>0</sub></b> : r = 0 donc il n'y a pas de corrélation.<br>
            <b>H<sub>1</sub></b> : r &ne; 0 donc il y a une corrélation.</p>"""

            html += f"<p>Nous allons mener un test de student à n-2 = <b>{df}</b> degrés de liberté. On calcule d'abord la statistique t suivante :</p>"

            t_formula = f"""
            <table cellspacing="0" cellpadding="0" style="display: inline-table; vertical-align: middle; font-family: 'Times New Roman';">
                <tr>
                    <td rowspan="2" style="vertical-align: middle; padding-right: 5px;">t = </td>
                    <td style="border-bottom: 1px solid black; text-align: center; padding: 0 5px;">r &radic;(n - 2)</td>
                    <td rowspan="2" style="vertical-align: middle; padding-left: 5px;"> = {r:.3f} &times; &radic;{df} / &radic;(1 - {r:.3f}<sup>2</sup>) = <b>{t_stat:.3f}</b></td>
                </tr>
                <tr>
                    <td style="text-align: center; padding: 0 5px;">&radic;(1 - r<sup>2</sup>)</td>
                </tr>
            </table>
            """
            html += f"<div>{t_formula}</div>"

            html += f"<p>on regarde la valeur critique t<sub>{alpha}, {df}</sub> dans la table de Student suivante :</p>"
            alphas_std = [0.2, 0.1, 0.05, 0.025, 0.01]
            html += f"""<table border="1" cellspacing="0" cellpadding="5" style="border-collapse: collapse; text-align: center;">
                <tr style="background: #ecf0f1;"><th>&alpha;</th>""" + "".join(
                [f"<th>{v_alpha}</th>" for v_alpha in alphas_std]) + "</tr>"
            html += "<tr><td style='font-weight: bold;'>t<sub>crit</sub></td>"
            for v_alpha in alphas_std:
                tc = stats.t.ppf(1 - v_alpha / 2, df)
                bg = "background: #fff3cd; font-weight: bold;" if abs(v_alpha - alpha) < 0.001 else ""
                html += f"<td style='{bg}'>{tc:.3f}</td>"
            html += "</tr></table>"

            symb = "&gt;" if abs(t_stat) > t_crit else "&lt;"
            decision = "peut" if abs(t_stat) > t_crit else "ne peut pas"
            verdict = "r est significativement supérieur à zéro, il y a une corrélation" if abs(
                t_stat) > t_crit else "r n'est pas significativement différent de 0, X et y ne sont pas corrélés"

            html += f"""<p>On trouve t<sub>{alpha}, {df}</sub> = <b>{t_crit:.3f}</b>.<br>Si |t| &gt; t<sub>{alpha},{df}</sub>, alors on peut rejeter l'hypothèse nulle, mais si |t| &lt; t<sub>{alpha},{df}</sub>, alors on ne peut pas rejetter l'hypothèse nulle.<br>
            Or, ici |{t_stat:.3f}| {symb} {t_crit:.3f}, donc on <b>{decision}</b> rejeter l'hypothèse H<sub>0</sub> au seuil alpha = {alpha} : {verdict}.</p>"""

            html += f"<p>On ajoute : le carré du coefficient de corrélation linéaire R<sub>xy</sub> est le coefficient de détermination <b>R<sup>2</sup></b>. Il représente la proportion de la variance de y reconstituée (corrélée) à partir de X.<br> Ici on a R<sup>2</sup> = <b>{r2:.3f}</b>, donc <b>{r2 * 100:.1f}%</b> des différences entre les y sont expliquées par les valeurs de X (important : l'explication est numérique et non causale).</p>"

            html += "<h2 style='color: #27ae60; font-size: 1.3em;'>Régression Linéaire</h2>"
            html += "<p>Lorsque le coefficient de corrélation R<sub>xy</sub> est proche de 1 ou -1, on cherche à exprimer la relation linéaire liant X et y. C'est-à-dire qu'on cherche la <b>droite de régression linéaire de y en x</b> passant le plus proche possible de tous les points (méthode des moindres carrés). L'équation de cette droite est de la forme : y = <b style='color: #db3b3b;'>a</b>x + <b style='color: #02c449;'>b</b>, avec :</p>"

            html += f"<div>{self.make_complex_fraction(f'C<sub>xy</sub>', f'&sigma;<sub>x</sub><sup>2</sup>', f'{a:.3f}', 'a')}</div>"
            html += f"<div>b = ȳ - a x̄ = {my:.3f} - ({a:.3f} &times; {mx:.3f}) = <b>{b:.3f}</b></div>"

            html += f"<p style='font-size: 18px; text-align: center; border: 2px solid #27ae60; padding: 10px; margin: 15px;'><b>(D) : y = <b style='color: #db3b3b;'>{a:.3f}</b>x {'+' if b >= 0 else ''} <b style='color: #02c449;'>{b:.3f}</b></b></p>"

            img_reg = self.get_plot_b64(X, Y, a, b)
            html += f"<div style='text-align: center;'><img src='data:image/png;base64,{img_reg}' width='450'></div>"

            html += "</div>"
            self.log_area.setHtml(html)

        except Exception as e:
            self.log_area.setHtml(f"<b style='color:red;'>Erreur :</b> {str(e)}")

    def run_exponential_analysis(self):
        try:
            n_rows = self.spin_n.value()
            x_raw, y_raw = [], []
            for i in range(1, n_rows + 1):
                item_x = self.table.item(i, 0)
                item_y = self.table.item(i, 1)
                if item_x and item_y and item_x.text().strip() and item_y.text().strip():
                    val_y = float(item_y.text().replace(',', '.'))
                    if val_y <= 0:
                        raise ValueError("Le modèle exponentiel nécessite des valeurs de y strictement positives.")
                    x_raw.append(float(item_x.text().replace(',', '.')))
                    y_raw.append(val_y)

            n = len(x_raw)
            if n < 3: raise ValueError("Le test nécessite au moins 3 couples de données.")

            X = np.array(x_raw)
            y_orig = np.array(y_raw)
            Y_trans = np.log(y_orig)
            alpha = float(self.input_alpha.text().replace(',', '.'))

            mx, mY = np.mean(X), np.mean(Y_trans)
            vx, vY = np.var(X), np.var(Y_trans)
            sx, sY = np.sqrt(vx), np.sqrt(vY)
            cxY = np.mean(X * Y_trans) - (mx * mY)

            r = cxY / (sx * sY) if (sx * sY) != 0 else 0
            r2 = r ** 2

            df = n - 2
            t_stat = r * np.sqrt(df) / np.sqrt(1 - r2) if abs(r) < 1 else 0
            t_crit = stats.t.ppf(1 - alpha / 2, df)

            A_slope, B_intercept, _, _, _ = stats.linregress(X, Y_trans)

            a_final = np.exp(A_slope)
            b_final = np.exp(B_intercept)

            html = "<div style='font-family: Segoe UI; color: black; line-height: 1.6;'>"
            html += "<h1 style='color: #2980b9; border-bottom: 2px solid #2980b9;'>Test de Corrélation : Modèle Exponentiel <br>(y = ba<sup>x</sup>)</h1>"

            html += f"""<p>On cherche à modéliser la relation entre X et y par une fonction exponentielle. Pour cela, on utilise la méthode de <b>linéarisation</b> :<br><br>
            En prenant le logarithme népérien, l'équation y = ba<sup>x</sup> devient : <b>ln(y) = ln(b) + x &middot; ln(a)</b>.<br>
            On pose <b>Y = ln(y)</b>, <b>B = ln(b)</b> (ordonnée à l'origine) et <b>A = ln(a)</b> (pente).<br>
            On étudiera alors la droite de régression : <b>Y = Ax + B</b>.</p>"""

            html += f"""
            <table border="1" cellspacing="0" cellpadding="8" style="border-collapse: collapse; text-align: center; width: 100%; margin-bottom: 15px;">
                <tr style="background: #ecf0f1;"><td><b>X</b></td>""" + "".join(
                [f"<td>{v:.2f}</td>" for v in X]) + "</tr>"
            html += f"""<tr style="color: #2980b9;"><td><b>Y = ln(y)</b></td>""" + "".join(
                [f"<td>{v:.3f}</td>" for v in Y_trans]) + "</tr></table>"

            img_cloud = self.get_plot_b64(X, y_orig)
            html += f"<div style='text-align: center; margin-bottom: 20px;'><img src='data:image/png;base64,{img_cloud}' width='350'></div>"

            html += "<p>On calcule les paramètres descriptifs pour X et la variable transformée Y :</p>"
            html += f"<div>X : x̄ = <b>{mx:.4f}</b> ; V<sub>x</sub> = <b>{vx:.4f}</b> ; &sigma;<sub>x</sub> = <b>{sx:.4f}</b></div>"
            html += f"<div>Y : Ȳ = <b>{mY:.4f}</b> ; V<sub>Y</sub> = <b>{vY:.4f}</b> ; &sigma;<sub>Y</sub> = <b>{sY:.4f}</b></div>"

            html += "<p>On calcule ensuite la covariance C<sub>xY</sub> et le coefficient de corrélation linéaire R<sub>xY</sub> :</p>"
            html += f"<div style='margin-bottom: 10px;'>{self.make_summation_formula(n, cxY)}</div>"
            html += f"<div>{self.make_complex_fraction(f'{cxY:.4f}', f'{sx:.3f} &times; {sY:.3f}', f'{r:.4f}', 'R<sub>xY</sub> = C<sub>xY</sub> / (&sigma;<sub>x</sub>&sigma;<sub>Y</sub>)')}</div>"

            qualif = "quasi-parfaite" if abs(r) > 0.95 else "forte" if abs(r) > 0.8 else "modérée" if abs(
                r) > 0.5 else "faible"
            html += f"<p><b>Interprétation :</b> Le coefficient r = <b>{r:.4f}</b> indique une liaison exponentielle <b>{qualif}</b>.</p>"

            html += f"""<p><b>Test de significativité :</b> On vérifie si r est significativement différent de 0.<br>
            <b>H<sub>0</sub></b> : r = 0 (Pas de relation exponentielle).<br>
            <b>H<sub>1</sub></b> : r &ne; 0 (Relation exponentielle significative).</p>"""

            t_formula = f"""<table cellspacing="0" cellpadding="0" style="display: inline-table; vertical-align: middle; font-family: 'Times New Roman';">
                <tr><td rowspan="2" style="vertical-align: middle; padding-right: 5px;">t = </td><td style="border-bottom: 1px solid black; text-align: center; padding: 0 5px;">r &radic;(n - 2)</td><td rowspan="2" style="vertical-align: middle; padding-left: 5px;"> = <b>{t_stat:.4f}</b></td></tr>
                <tr><td style="text-align: center; padding: 0 5px;">&radic;(1 - r<sup>2</sup>)</td></tr>
            </table>"""
            html += f"<div>Statistique observée : {t_formula}</div>"

            html += f"<p>Comparaison avec t<sub>{alpha}, {df}</sub> :</p>"
            alphas_std = [0.2, 0.1, 0.05, 0.025, 0.01]
            html += f"""<table border="1" cellspacing="0" cellpadding="5" style="border-collapse: collapse; text-align: center;">
                <tr style="background: #ecf0f1;"><th>&alpha;</th>""" + "".join(
                [f"<th>{va}</th>" for va in alphas_std]) + "</tr><tr><td>t<sub>crit</sub></td>"
            for va in alphas_std:
                tc = stats.t.ppf(1 - va / 2, df)
                bg = "background: #fff3cd; font-weight: bold;" if abs(va - alpha) < 0.001 else ""
                html += f"<td style='{bg}'>{tc:.3f}</td>"
            html += "</tr></table>"

            symb = "&gt;" if abs(t_stat) > t_crit else "&lt;"
            decision = "rejetons" if abs(t_stat) > t_crit else "ne pouvons pas rejeter"
            html += f"<p>Puisque |{t_stat:.3f}| {symb} {t_crit:.3f}, nous <b>{decision}</b> H<sub>0</sub> au seuil {alpha}.</p>"

            html += "<h2 style='color: #27ae60; font-size: 1.3em;'>Équation du modèle</h2>"
            html += "<p>On détermine les paramètres de la droite transformée Y = Ax + B :</p>"

            html += f"<div>{self.make_complex_fraction('C<sub>xY</sub>', '&sigma;<sub>x</sub><sup>2</sup>', f'{A_slope:.4f}', 'A')}</div>"
            html += f"<div>B = Ȳ - Ax̄ = {mY:.4f} - ({A_slope:.4f} &times; {mx:.4f}) = <b>{B_intercept:.4f}</b></div>"

            html += f"""<p>On revient maintenant aux paramètres originaux du modèle <b>y = ba<sup>x</sup></b> :<br><br>
            &bull; <b>b = e<sup>B</sup></b> = e<sup>{B_intercept:.4f}</sup> = <b>{b_final:.4f}</b><br>
            &bull; <b>a = e<sup>A</sup></b> = e<sup>{A_slope:.4f}</sup> = <b>{a_final:.4f}</b></p>"""

            html += f"<p style='text-align: center; border: 2px solid #27ae60; padding: 10px; font-size: 18px;'><b>Modèle : y = {b_final:.4f} &middot; ({a_final:.4f})<sup>x</sup></b></p>"

            img_reg = self.get_plot_exp_curved_b64(X, y_orig, a_final, b_final)
            html += f"<div style='text-align: center;'><img src='data:image/png;base64,{img_reg}' width='450'></div>"

            html += "</div>"
            self.log_area.setHtml(html)

        except Exception as e:
            self.log_area.setHtml(f"<b style='color:red;'>Erreur :</b> {str(e)}")

    def get_plot_exp_curved_b64(self, x, y, a_val, b_val):
        plt.figure(figsize=(5, 3.5))
        plt.scatter(x, y, color='#2980b9', s=40)
        x_smooth = np.linspace(min(x), max(x), 100)
        y_curve = b_val * (a_val ** x_smooth)
        plt.plot(x_smooth, y_curve, color='#e74c3c', linewidth=2)
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        plt.close()
        return base64.b64encode(buf.getvalue()).decode('utf-8')

    def run_power_analysis(self):
        try:
            n_rows = self.spin_n.value()
            x_raw, y_raw = [], []
            for i in range(1, n_rows + 1):
                item_x = self.table.item(i, 0)
                item_y = self.table.item(i, 1)
                if item_x and item_y and item_x.text().strip() and item_y.text().strip():
                    val_x = float(item_x.text().replace(',', '.'))
                    val_y = float(item_y.text().replace(',', '.'))
                    if val_x <= 0 or val_y <= 0:
                        raise ValueError("Le modèle puissance nécessite des valeurs de X et y strictement positives.")
                    x_raw.append(val_x)
                    y_raw.append(val_y)

            n = len(x_raw)
            if n < 3: raise ValueError("Le test nécessite au moins 3 couples de données.")

            x_orig = np.array(x_raw)
            y_orig = np.array(y_raw)

            X_trans = np.log(x_orig)
            Y_trans = np.log(y_orig)
            alpha = float(self.input_alpha.text().replace(',', '.'))

            mX, mY = np.mean(X_trans), np.mean(Y_trans)
            vX, vY = np.var(X_trans), np.var(Y_trans)
            sX, sY = np.sqrt(vX), np.sqrt(vY)
            cXY = np.mean(X_trans * Y_trans) - (mX * mY)

            r = cXY / (sX * sY) if (sX * sY) != 0 else 0
            r2 = r ** 2

            df = n - 2
            t_stat = r * np.sqrt(df) / np.sqrt(1 - r2) if abs(r) < 1 else 0
            t_crit = stats.t.ppf(1 - alpha / 2, df)

            A_slope, B_intercept, _, _, _ = stats.linregress(X_trans, Y_trans)

            a_final = A_slope
            b_final = np.exp(B_intercept)

            html = "<div style='font-family: Segoe UI; color: black; line-height: 1.6;'>"
            html += "<h1 style='color: #2980b9; border-bottom: 2px solid #2980b9;'>Test de Corrélation : Modèle Puissance <br>(y = bx<sup>a</sup>)</h1>"

            html += f"""<p>On cherche à modéliser la relation entre X et y par une fonction puissance. Pour cela, on utilise une <b>double linéarisation</b> :<br><br>
            En prenant le logarithme népérien, l'équation y = bx<sup>a</sup> devient : <b>ln(y) = ln(b) + a &middot; ln(x)</b>.<br>
            On pose <b>Y = ln(y)</b>, <b>X' = ln(x)</b>, <b>B = ln(b)</b> (ordonnée à l'origine) et <b>A = a</b> (pente).<br>
            On étudiera alors la droite de régression : <b>Y = AX' + B</b>.</p>"""

            html += f"""
            <table border="1" cellspacing="0" cellpadding="8" style="border-collapse: collapse; text-align: center; width: 100%; margin-bottom: 15px;">
                <tr style="background: #ecf0f1; color: #2980b9;"><td><b>X' = ln(x)</b></td>""" + "".join(
                [f"<td>{v:.3f}</td>" for v in X_trans]) + "</tr>"
            html += f"""<tr style="color: #2980b9;"><td><b>Y = ln(y)</b></td>""" + "".join(
                [f"<td>{v:.3f}</td>" for v in Y_trans]) + "</tr></table>"

            img_cloud = self.get_plot_b64(x_orig, y_orig)
            html += f"<div style='text-align: center; margin-bottom: 20px;'><img src='data:image/png;base64,{img_cloud}' width='350'></div>"

            html += "<p>On calcule les paramètres descriptifs pour les variables transformées X' et Y :</p>"
            html += f"<div>X' : x̄' = <b>{mX:.4f}</b> ; V<sub>x'</sub> = <b>{vX:.4f}</b> ; &sigma;<sub>x'</sub> = <b>{sX:.4f}</b></div>"
            html += f"<div>Y : Ȳ = <b>{mY:.4f}</b> ; V<sub>Y</sub> = <b>{vY:.4f}</b> ; &sigma;<sub>Y</sub> = <b>{sY:.4f}</b></div>"

            html += "<p>On calcule ensuite la covariance C<sub>x'Y</sub> et le coefficient de corrélation linéaire R<sub>x'Y</sub> :</p>"
            html += f"<div style='margin-bottom: 10px;'>{self.make_summation_formula(n, cXY)}</div>"
            html += f"<div>{self.make_complex_fraction(f'{cXY:.4f}', f'{sX:.3f} &times; {sY:.3f}', f'{r:.4f}', 'R<sub>x\'Y</sub> = C<sub>x\'Y</sub> / (&sigma;<sub>x\'</sub>&sigma;<sub>Y</sub>)')}</div>"

            qualif = "quasi-parfaite" if abs(r) > 0.95 else "forte" if abs(r) > 0.8 else "modérée" if abs(
                r) > 0.5 else "faible"
            html += f"<p><b>Interprétation :</b> Le coefficient r = <b>{r:.4f}</b> indique une liaison de type puissance <b>{qualif}</b>.</p>"

            html += f"""<p><b>Test de significativité :</b> On vérifie si r est significativement différent de 0.<br>
            <b>H<sub>0</sub></b> : r = 0 (Pas de relation de puissance).<br>
            <b>H<sub>1</sub></b> : r &ne; 0 (Relation de puissance significative).</p>"""

            t_formula = f"""<table cellspacing="0" cellpadding="0" style="display: inline-table; vertical-align: middle; font-family: 'Times New Roman';">
                <tr><td rowspan="2" style="vertical-align: middle; padding-right: 5px;">t = </td><td style="border-bottom: 1px solid black; text-align: center; padding: 0 5px;">r &radic;(n - 2)</td><td rowspan="2" style="vertical-align: middle; padding-left: 5px;"> = <b>{t_stat:.4f}</b></td></tr>
                <tr><td style="text-align: center; padding: 0 5px;">&radic;(1 - r<sup>2</sup>)</td></tr>
            </table>"""
            html += f"<div>Statistique observée : {t_formula}</div>"

            html += f"<p>Comparaison avec t<sub>{alpha}, {df}</sub> :</p>"
            alphas_std = [0.2, 0.1, 0.05, 0.025, 0.01]
            html += f"""<table border="1" cellspacing="0" cellpadding="5" style="border-collapse: collapse; text-align: center;">
                <tr style="background: #ecf0f1;"><th>&alpha;</th>""" + "".join(
                [f"<th>{va}</th>" for va in alphas_std]) + "</tr><tr><td>t<sub>crit</sub></td>"
            for va in alphas_std:
                tc = stats.t.ppf(1 - va / 2, df)
                bg = "background: #fff3cd; font-weight: bold;" if abs(va - alpha) < 0.001 else ""
                html += f"<td style='{bg}'>{tc:.3f}</td>"
            html += "</tr></table>"

            symb = "&gt;" if abs(t_stat) > t_crit else "&lt;"
            decision = "rejetons" if abs(t_stat) > t_crit else "ne pouvons pas rejeter"
            html += f"<p>Puisque |{t_stat:.3f}| {symb} {t_crit:.3f}, nous <b>{decision}</b> H<sub>0</sub> au seuil {alpha}.</p>"

            html += "<h2 style='color: #27ae60; font-size: 1.3em;'>Équation du modèle</h2>"
            html += "<p>On détermine les paramètres de la droite transformée Y = AX' + B :</p>"

            html += f"<div>{self.make_complex_fraction('C<sub>x\'Y</sub>', '&sigma;<sub>x\'</sub><sup>2</sup>', f'{A_slope:.4f}', 'A')}</div>"
            html += f"<div>B = Ȳ - Ax̄' = {mY:.4f} - ({A_slope:.4f} &times; {mX:.4f}) = <b>{B_intercept:.4f}</b></div>"

            html += f"""<p>On revient maintenant aux paramètres originaux du modèle <b>y = bx<sup>a</sup></b> :<br><br>
            &bull; <b>a = A</b> = <b>{a_final:.4f}</b><br>
            &bull; <b>b = e<sup>B</sup></b> = e<sup>{B_intercept:.4f}</sup> = <b>{b_final:.4f}</b></p>"""

            html += f"<p style='text-align: center; border: 2px solid #27ae60; padding: 10px; font-size: 18px;'><b>Modèle final : y = {b_final:.4f} &middot; x<sup>{a_final:.4f}</sup></b></p>"

            img_reg = self.get_plot_power_curved_b64(x_orig, y_orig, a_final, b_final)
            html += f"<div style='text-align: center;'><img src='data:image/png;base64,{img_reg}' width='450'></div>"

            html += "</div>"
            self.log_area.setHtml(html)

        except Exception as e:
            self.log_area.setHtml(f"<b style='color:red;'>Erreur :</b> {str(e)}")

    def get_plot_power_curved_b64(self, x, y, a_val, b_val):
        """Trace la courbe y = b * (x^a)"""
        plt.figure(figsize=(5, 3.5))
        plt.scatter(x, y, color='#2980b9', s=40)

        x_smooth = np.linspace(min(x), max(x), 100)
        y_curve = b_val * (x_smooth ** a_val)

        plt.plot(x_smooth, y_curve, color='#e74c3c', linewidth=2)
        plt.xlabel('X')
        plt.ylabel('y')
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        plt.close()
        return base64.b64encode(buf.getvalue()).decode('utf-8')

    def run_logarithmic_analysis(self):
        try:
            n_rows = self.spin_n.value()
            x_raw, y_raw = [], []
            for i in range(1, n_rows + 1):
                item_x = self.table.item(i, 0)
                item_y = self.table.item(i, 1)
                if item_x and item_y and item_x.text().strip() and item_y.text().strip():
                    val_x = float(item_x.text().replace(',', '.'))
                    val_y = float(item_y.text().replace(',', '.'))
                    if val_x <= 0:
                        raise ValueError("Le modèle logarithmique nécessite des valeurs de X strictement positives.")
                    x_raw.append(val_x)
                    y_raw.append(val_y)

            n = len(x_raw)
            if n < 3: raise ValueError("Le test nécessite au moins 3 couples de données.")

            x_orig = np.array(x_raw)
            y_data = np.array(y_raw)

            X_trans = np.log(x_orig)
            alpha = float(self.input_alpha.text().replace(',', '.'))

            mX, my = np.mean(X_trans), np.mean(y_data)
            vX, vy = np.var(X_trans), np.var(y_data)
            sX, sy = np.sqrt(vX), np.sqrt(vy)
            cXy = np.mean(X_trans * y_data) - (mX * my)

            r = cXy / (sX * sy) if (sX * sy) != 0 else 0
            r2 = r ** 2

            df = n - 2
            t_stat = r * np.sqrt(df) / np.sqrt(1 - r2) if abs(r) < 1 else 0
            t_crit = stats.t.ppf(1 - alpha / 2, df)

            a_coeff, b_const, _, _, _ = stats.linregress(X_trans, y_data)

            html = "<div style='font-family: Segoe UI; color: black; line-height: 1.6;'>"
            html += "<h1 style='color: #2980b9; border-bottom: 2px solid #2980b9;'>Test de Corrélation : Modèle Logarithmique <br>(y = a &middot; ln(x) + b)</h1>"

            html += f"""<p>On cherche à modéliser la relation entre X et y par une fonction logarithmique. On utilise la méthode de <b>linéarisation</b> :<br><br>
            L'équation y = a &middot; ln(x) + b est déjà linéaire par rapport au logarithme de x.<br>
            On pose <b>X' = ln(x)</b> et <b>Y = y</b>. <br>
            On étudiera alors la droite de régression : <b>y = aX' + b</b>.</p>"""

            html += f"""
            <table border="1" cellspacing="0" cellpadding="8" style="border-collapse: collapse; text-align: center; width: 100%; margin-bottom: 15px;">
                <tr style="background: #ecf0f1; color: #2980b9;"><td><b>X' = ln(x)</b></td>""" + "".join(
                [f"<td>{v:.3f}</td>" for v in X_trans]) + "</tr>"
            html += f"""<tr><td><b>y (original)</b></td>""" + "".join(
                [f"<td>{v:.2f}</td>" for v in y_data]) + "</tr></table>"

            img_cloud = self.get_plot_b64(x_orig, y_data)
            html += f"<div style='text-align: center; margin-bottom: 20px;'><img src='data:image/png;base64,{img_cloud}' width='350'></div>"

            html += "<p>On calcule les paramètres descriptifs pour la variable transformée X' et y :</p>"
            html += f"<div>X' : x̄' = <b>{mX:.4f}</b> ; V<sub>x'</sub> = <b>{vX:.4f}</b> ; &sigma;<sub>x'</sub> = <b>{sX:.4f}</b></div>"
            html += f"<div>y : ȳ = <b>{my:.4f}</b> ; V<sub>y</sub> = <b>{vy:.4f}</b> ; &sigma;<sub>y</sub> = <b>{sy:.4f}</b></div>"

            html += "<p>On calcule ensuite la covariance C<sub>x'y</sub> et le coefficient de corrélation linéaire R<sub>x'y</sub> :</p>"
            html += f"<div style='margin-bottom: 10px;'>{self.make_summation_formula(n, cXy)}</div>"
            html += f"<div>{self.make_complex_fraction(f'{cXy:.4f}', f'{sX:.3f} &times; {sy:.3f}', f'{r:.4f}', 'R<sub>x\'y</sub> = C<sub>x\'y</sub> / (&sigma;<sub>x\'</sub>&sigma;<sub>y</sub>)')}</div>"

            qualif = "forte" if abs(r) > 0.8 else "moyenne" if abs(r) > 0.5 else "faible"
            html += f"<p><b>Interprétation :</b> Le coefficient r = <b>{r:.4f}</b> indique une liaison logarithmique <b>{qualif}</b>.</p>"

            html += f"""<p><b>Test de Student :</b> On vérifie la significativité de cette liaison.<br>
            <b>H<sub>0</sub></b> : r = 0 ; <b>H<sub>1</sub></b> : r &ne; 0.</p>"""

            t_formula = f"""<table cellspacing="0" cellpadding="0" style="display: inline-table; vertical-align: middle; font-family: 'Times New Roman';">
                <tr><td rowspan="2" style="vertical-align: middle; padding-right: 5px;">t = </td><td style="border-bottom: 1px solid black; text-align: center; padding: 0 5px;">r &radic;(n - 2)</td><td rowspan="2" style="vertical-align: middle; padding-left: 5px;"> = <b>{t_stat:.4f}</b></td></tr>
                <tr><td style="text-align: center; padding: 0 5px;">&radic;(1 - r<sup>2</sup>)</td></tr>
            </table>"""
            html += f"<div>Statistique observée : {t_formula}</div>"

            html += f"<p>Comparaison avec t<sub>{alpha}, {df}</sub> :</p>"
            alphas_std = [0.2, 0.1, 0.05, 0.025, 0.01]
            html += f"""<table border="1" cellspacing="0" cellpadding="5" style="border-collapse: collapse; text-align: center;">
                <tr style="background: #ecf0f1;"><th>&alpha;</th>""" + "".join(
                [f"<th>{va}</th>" for va in alphas_std]) + "</tr><tr><td>t<sub>crit</sub></td>"
            for va in alphas_std:
                tc = stats.t.ppf(1 - va / 2, df)
                bg = "background: #fff3cd; font-weight: bold;" if abs(va - alpha) < 0.001 else ""
                html += f"<td style='{bg}'>{tc:.3f}</td>"
            html += "</tr></table>"

            decision = "rejetons" if abs(t_stat) > t_crit else "ne pouvons pas rejeter"
            html += f"<p>Au seuil {alpha}, nous <b>{decision}</b> l'hypothèse nulle H<sub>0</sub>.</p>"

            html += "<h2 style='color: #27ae60; font-size: 1.3em;'>Équation du modèle</h2>"
            html += "<p>On détermine les coefficients de la droite y = aX' + b :</p>"

            html += f"<div>{self.make_complex_fraction('C<sub>x\'y</sub>', '&sigma;<sub>x\'</sub><sup>2</sup>', f'{a_coeff:.4f}', 'a')}</div>"
            html += f"<div>b = ȳ - ax̄' = {my:.4f} - ({a_coeff:.4f} &times; {mX:.4f}) = <b>{b_const:.4f}</b></div>"

            html += f"<p style='text-align: center; border: 2px solid #27ae60; padding: 10px; font-size: 18px; margin: 15px;'><b>Modèle : y = {a_coeff:.4f} &middot; ln(x) {'+' if b_const >= 0 else ''} {b_const:.4f}</b></p>"

            img_reg = self.get_plot_log_curved_b64(x_orig, y_data, a_coeff, b_const)
            html += f"<div style='text-align: center;'><img src='data:image/png;base64,{img_reg}' width='450'></div>"

            html += "</div>"
            self.log_area.setHtml(html)

        except Exception as e:
            self.log_area.setHtml(f"<b style='color:red;'>Erreur :</b> {str(e)}")

    def get_plot_log_curved_b64(self, x, y, a_val, b_val):
        """Trace la courbe y = a * ln(x) + b"""
        plt.figure(figsize=(5, 3.5))
        plt.scatter(x, y, color='#2980b9', s=40)

        x_smooth = np.linspace(min(x), max(x), 100)
        y_curve = a_val * np.log(x_smooth) + b_val

        plt.plot(x_smooth, y_curve, color='#e74c3c', linewidth=2)
        plt.xlabel('X')
        plt.ylabel('y')
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        plt.close()
        return base64.b64encode(buf.getvalue()).decode('utf-8')