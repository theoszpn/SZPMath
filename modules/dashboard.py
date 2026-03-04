from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QFrame, QGridLayout)
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve, QRect


class DashboardCard(QWidget):
    clicked = Signal()

    def __init__(self, title, description, color="#0097e6"):
        super().__init__()

        self.slot_size = (300, 250)
        self.normal_geo = QRect(25, 25, 250, 200)
        self.hover_geo = QRect(15, 15, 270, 220)

        self.setFixedSize(300, 250)

        self.inner_frame = QFrame(self)
        self.inner_frame.setGeometry(self.normal_geo)
        self.inner_frame.setObjectName("Card")
        self.inner_frame.setCursor(Qt.CursorShape.PointingHandCursor)

        self.color = color
        self.style_normal = f"#Card {{ background-color: white; border-radius: 15px; border: 2px solid #dcdde1; }}"
        self.style_hover = f"#Card {{ background-color: #f8f9fa; border-radius: 15px; border: 2px solid {color}; }}"
        self.inner_frame.setStyleSheet(self.style_normal)

        layout = QVBoxLayout(self.inner_frame)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lbl_title = QLabel(title)
        self.lbl_title.setStyleSheet("font-size: 22px; font-weight: bold; color: #2f3640;")
        self.lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lbl_desc = QLabel(description)
        self.lbl_desc.setStyleSheet("font-size: 12px; color: #7f8c8d; qproperty-alignment: AlignCenter;")
        self.lbl_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_desc.setWordWrap(True)

        layout.addWidget(self.lbl_title)
        layout.addWidget(self.lbl_desc)

        self.anim = QPropertyAnimation(self.inner_frame, b"geometry")
        self.anim.setDuration(200)
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    def enterEvent(self, event):
        self.inner_frame.setStyleSheet(self.style_hover)
        self.anim.stop()
        self.anim.setEndValue(self.hover_geo)
        self.anim.start()
        self.raise_()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.inner_frame.setStyleSheet(self.style_normal)
        self.anim.stop()
        self.anim.setEndValue(self.normal_geo)
        self.anim.start()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if self.inner_frame.geometry().contains(event.pos()):
            if event.button() == Qt.MouseButton.LeftButton:
                self.clicked.emit()
        super().mousePressEvent(event)


class DashboardPage(QWidget):
    module_selected = Signal(int)

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(0)

        self.lbl_logo = QLabel()
        html_content = """
        <div align='center'>
            <table border='0' cellpadding='0' cellspacing='0' style='margin: auto;'>
                <tr>
                    <td style='font-size: 98px; color: #2f3640; vertical-align: middle;'>Σ</td>
                    <td style='font-size: 68px; color: #2f3640; font-weight: bold; vertical-align: middle;'>&nbsp;SZPMath</td>
                </tr>
            </table>
        </div>
        """
        self.lbl_logo.setText(html_content)
        self.lbl_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_logo)

        grid = QGridLayout()
        grid.setSpacing(20)

        modules = [
            ("Algèbre Linéaire", "Systèmes linéaires, Espaces vectoriels, Visualisation 3D", 1),
            ("Statistiques", "Analyse descriptive, Estimations et Tests paramétriques", 2),
            ("Probabilités", "Outils d'études de lois de probabilité", 3),
            ("Calculus", "Visualisations, Limites, Dérivées, Intégrales", 4)
        ]

        for i, (name, desc, idx) in enumerate(modules):
            card = DashboardCard(name, desc)
            card.clicked.connect(lambda index=idx: self.module_selected.emit(index))
            grid.addWidget(card, i // 2, i % 2)

        layout.addLayout(grid)