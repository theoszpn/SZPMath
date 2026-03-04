import numpy as np
from scipy import stats
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                               QPushButton, QTextEdit, QLabel,
                               QSpinBox, QTableWidgetItem, QLineEdit)
from PySide6.QtCore import Qt


class ChiSquareIndependancePage(QWidget):
    def __init__(self):
        super().__init__()
        self.cell_size = 65
        self.init_ui()

    def init_ui(self):
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(20)

        left_column = QVBoxLayout()
        left_column.setAlignment(Qt.AlignmentFlag.AlignTop)

        dims_layout = QHBoxLayout()
        self.spin_rows = QSpinBox()
        self.spin_rows.setRange(2, 10)
        self.spin_rows.setValue(2)
        self.spin_rows.setFixedWidth(55)
        self.spin_cols = QSpinBox()
        self.spin_cols.setRange(2, 10)
        self.spin_cols.setValue(2)
        self.spin_cols.setFixedWidth(55)

        lbl_x = QLabel("Lignes (X) :")
        lbl_x.setStyleSheet("font-weight: bold; color: #2f3640;")
        lbl_y = QLabel("Colonnes (Y) :")
        lbl_y.setStyleSheet("font-weight: bold; color: #2f3640;")

        dims_layout.addWidget(lbl_x)
        dims_layout.addWidget(self.spin_rows)
        dims_layout.addSpacing(5)
        dims_layout.addWidget(lbl_y)
        dims_layout.addWidget(self.spin_cols)
        dims_layout.addStretch()
        left_column.addLayout(dims_layout)
        left_column.addSpacing(15)

        self.table = QTableWidget(3, 3)
        self.setup_table_style()
        self.refresh_table_headers()
        left_column.addWidget(self.table)
        left_column.addSpacing(10)

        alpha_layout = QHBoxLayout()
        lbl_alpha = QLabel("Seuil alpha (α) :")
        lbl_alpha.setStyleSheet("font-weight: bold; color: #2f3640;")
        self.input_alpha = QLineEdit("0.05")
        self.input_alpha.setFixedWidth(60)
        self.input_alpha.setStyleSheet("padding: 5px; font-weight: bold;")
        alpha_layout.addWidget(lbl_alpha)
        alpha_layout.addWidget(self.input_alpha)
        alpha_layout.addStretch()
        left_column.addLayout(alpha_layout)

        btn_style = """
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
        """
        self.btn_run = QPushButton("➜ Test d'indépendance du χ²")
        self.btn_run.setStyleSheet(btn_style)
        left_column.addWidget(self.btn_run)
        left_column.addStretch()

        right_column = QVBoxLayout()
        lbl_steps = QLabel("Étapes de résolution & Analyse")
        lbl_steps.setStyleSheet("font-weight: bold; font-size: 16px; color: black;")
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setStyleSheet(
            "background-color: white; color: black; border: 2px solid #bdc3c7; border-radius: 5px; font-size: 18px; padding: 10px;")
        right_column.addWidget(lbl_steps)
        right_column.addWidget(self.log_area)

        self.main_layout.addLayout(left_column, 1)
        self.main_layout.addLayout(right_column, 5)

        self.spin_rows.valueChanged.connect(self.update_table_dims)
        self.spin_cols.valueChanged.connect(self.update_table_dims)
        self.btn_run.clicked.connect(self.run_chi2_test)

    def setup_table_style(self):
        self.table.horizontalHeader().setVisible(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setStyleSheet("""
            QTableWidget { background-color: white; color: black; border: 2px solid #34495e; gridline-color: #bdc3c7; font-weight: bold; font-size: 16px; selection-background-color: #ecf0f1; selection-color: black; }
            QTableWidget QLineEdit { background-color: white; color: black; border: none; text-align: center; }
        """)
        self.table.itemChanged.connect(self.align_cell_text)

    def align_cell_text(self, item):
        self.table.blockSignals(True)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.blockSignals(False)

    def to_subscript(self, n):
        sub_map = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
        return str(n).translate(sub_map)

    def refresh_table_headers(self):
        self.table.blockSignals(True)
        rows, cols = self.table.rowCount(), self.table.columnCount()
        item_corner = QTableWidgetItem("X \\ Y")
        item_corner.setFlags(Qt.ItemFlag.ItemIsEnabled)
        item_corner.setBackground(Qt.GlobalColor.lightGray)
        self.table.setItem(0, 0, item_corner)
        for j in range(1, cols):
            item = QTableWidgetItem(f"Y{self.to_subscript(j)}")
            item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            item.setBackground(Qt.GlobalColor.lightGray)
            self.table.setItem(0, j, item)
        for i in range(1, rows):
            item = QTableWidgetItem(f"X{self.to_subscript(i)}")
            item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            item.setBackground(Qt.GlobalColor.lightGray)
            self.table.setItem(i, 0, item)
        self.table.blockSignals(False)
        self.adjust_table_size()

    def update_table_dims(self):
        r, c = self.spin_rows.value(), self.spin_cols.value()
        self.table.setRowCount(r + 1)
        self.table.setColumnCount(c + 1)
        self.refresh_table_headers()

    def adjust_table_size(self):
        cols, rows = self.table.columnCount(), self.table.rowCount()
        total_width = (cols * self.cell_size) + 2
        total_height = (rows * 45) + 2
        max_band_width = 400
        for j in range(cols): self.table.setColumnWidth(j, self.cell_size)
        for i in range(rows): self.table.setRowHeight(i, 45)
        self.table.setFixedHeight(total_height + 5)
        self.table.setFixedWidth(min(total_width + 5, max_band_width))


    def matrix_to_html(self, data, row_labels, col_labels, title=""):
        html = f"<div style='margin-bottom: 10px; text-align: center;'><b>{title}</b></div><br>"
        html += "<table style='border-collapse: collapse; border: 2px solid black; text-align: center; margin-bottom: 20px;'>"
        html += "<tr><td style='border: 1px solid black; background: #ecf0f1; padding: 5px;'>X \\ Y</td>"
        for label in col_labels:
            html += f"<td style='border: 1px solid black; background: #ecf0f1; font-weight: bold; padding: 5px;'>{label}</td>"
        html += "</tr>"
        for i, row in enumerate(data):
            html += f"<tr><td style='border: 1px solid black; background: #ecf0f1; font-weight: bold; padding: 5px;'>{row_labels[i]}</td>"
            for val in row:
                v_str = f"{val:.2f}" if isinstance(val, float) else str(val)
                html += f"<td style='border: 1px solid black; padding: 5px;'>{v_str}</td>"
            html += "</tr>"
        html += "</table>"
        return html

    def run_chi2_test(self):
        try:
            alpha = float(self.input_alpha.text().replace(',', '.'))
            p = self.spin_rows.value()
            q = self.spin_cols.value()

            obs = np.zeros((p, q))
            for i in range(p):
                for j in range(q):
                    item = self.table.item(i + 1, j + 1)
                    obs[i, j] = float(item.text()) if item and item.text() else 0

            row_sums = obs.sum(axis=1)
            col_sums = obs.sum(axis=0)
            n = obs.sum()

            self.log_area.clear()
            self.log_area.insertHtml("<h2>Test d'indépendance du Khi-deux</h2>")

            self.log_area.append(
                f"On cherche ici à mesurer l'indépendance entre deux variables statistiques X et Y au seuil de confiance <b>α = {alpha}</b>. Pour représenter nos données on utilise un tableau de contingence.<br><br>")

            obs_plus_totals = np.zeros((p + 1, q + 1))
            obs_plus_totals[:p, :q] = obs
            obs_plus_totals[:p, q] = row_sums
            obs_plus_totals[p, :q] = col_sums
            obs_plus_totals[p, q] = n
            r_labels = [f"X{self.to_subscript(i + 1)}" for i in range(p)] + ["Total"]
            c_labels = [f"Y{self.to_subscript(j + 1)}" for j in range(q)] + ["Total"]
            self.log_area.insertHtml(self.matrix_to_html(obs_plus_totals, r_labels, c_labels,
                                                         "Tableau de contingence : Effectifs observés nᵢⱼ et totaux"))

            self.log_area.insertHtml(
                "<br>On pose les hypothèses suivantes :<br><b>H₀</b> : X et Y sont indépendantes.<br><b>H₁</b> : X et Y ne sont pas indépendantes.<br><br>")
            self.log_area.append(
                "Pour évaluer ces hypothèses, on compare les <b>effectifs observés nᵢⱼ</b> aux <b>effectifs théoriques eᵢⱼ</b> correspondants à l'hypothèse d'indépendance.")

            formula_e = "<table style='margin: 10px;'><tr><td>eᵢⱼ = </td><td style='border-bottom: 2px solid black; text-align: center;'>nᵢ. × n.ⱼ</td></tr><tr><td></td><td style='text-align: center;'>n</td></tr></table>"
            self.log_area.insertHtml(f"<br>On calcule ces effectifs théoriques : {formula_e}")

            expected = np.outer(row_sums, col_sums) / n
            exp_plus_totals = np.zeros((p + 1, q + 1))
            exp_plus_totals[:p, :q] = expected
            exp_plus_totals[:p, q] = row_sums
            exp_plus_totals[p, :q] = col_sums
            exp_plus_totals[p, q] = n

            self.log_area.append("On dresse le tableau contenant les effectifs théoriques :<br><br>")
            self.log_area.insertHtml(
                self.matrix_to_html(exp_plus_totals, r_labels, c_labels, "Tableau des effectifs théoriques eᵢⱼ"))

            self.log_area.append(
                "La question est donc de savoir si les différences entre ces deux tableaux sont significatives ou non.")
            formula_d2 = "<table style='margin: 10px;'><tr><td rowspan='2' style='font-size: 25px;'>d² = Σ<sub>i,j</sub> </td><td style='border-bottom: 2px solid black; text-align: center;'>(nᵢⱼ - eᵢⱼ)²</td></tr><tr><td style='text-align: center;'>eᵢⱼ</td></tr></table>"
            self.log_area.insertHtml(f"<br>Pour cela on calcule la distance suivante : {formula_d2}")

            d2 = ((obs - expected) ** 2 / expected).sum()
            self.log_area.append(f"<br><b>On trouve donc d² = {d2:.3f}</b>")

            k = (p - 1) * (q - 1)
            t_alpha_k = stats.chi2.ppf(1 - alpha, k)
            self.log_area.append(
                f"<br>Ensuite on détermine :<br> -le seuil <b>t<sub>α,k</sub></b> avec <b>α = {alpha}</b><br> -le degré de liberté <b>k</b> = (i - 1)(j - 1), k = ({p} - 1)({q} - 1) = <b>{k}</b>.<br> En regardant dans la table des valeurs critiques du Khi-deux on trouve <b>t<sub>{alpha},{k}</sub> = {t_alpha_k:.3f}</b>.<br>")

            verdict = "rejette" if d2 > t_alpha_k else "ne rejette pas"
            symb = ">" if d2 > t_alpha_k else "≤"
            self.log_area.append("<h3>Conclusion</h3>")
            self.log_area.append(
                f"<br>Si d² > t<sub>α,k</sub>, alors on rejette H₀ au seuil α = {alpha}. Or, <b>{d2:.3f} {symb} {t_alpha_k:.3f}</b> donc on <b>{verdict}</b> l'hypothèse H₀ au seuil α = {alpha}.")

            v_cramer = np.sqrt(d2 / (n * (min(p, q) - 1)))

            if v_cramer < 0.10:
                interp = "Liaison très faible (&lt;0.1)"
            elif v_cramer < 0.30:
                interp = "Liaison faible (&lt;0.3)"
            elif v_cramer < 0.50:
                interp = "Liaison moyenne (&lt;0.5)"
            else:
                interp = "Liaison forte (&gt;0.5)"

            self.log_area.append(
                "<br>On peut également quantifier la liaison de ces variables avec le V de Cramer :")

            formula_v = f"""
                        <table style='margin: 10px; border-collapse: collapse;'>
                            <tr>
                                <td rowspan='2' style='vertical-align: middle; font-size: 22px; padding-right: 2px;'>V = </td>
                                <td rowspan='2' style='vertical-align: top; horizontal-align: right; font-size: 50px; line-height: 42px; padding-top: 2px;'>&radic;</td>
                                <td style='border-top: 2px solid black; border-bottom: 1px solid black; text-align: center; padding: 2px 10px;'>d²</td>
                            </tr>
                            <tr>
                                <td style='text-align: center; padding: 2px 10px;'>n &times; (min(p, q) - 1)</td>
                            </tr>
                        </table>
                        """

            self.log_area.insertHtml(formula_v)
            self.log_area.insertHtml(
                f"<p style='font-size: 20px;'><b>V = {v_cramer:.3f}</b> <span style='color: #2980b9;'> {interp}</span></p>")

        except Exception as e:
            self.log_area.append(f"<br><b style='color: red;'>Erreur : {str(e)}</b>")