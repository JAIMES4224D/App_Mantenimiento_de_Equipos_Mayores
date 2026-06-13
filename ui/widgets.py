"""Widgets reutilizables de la UI."""
from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QWidget, QSizePolicy, QDialog, QLineEdit,
    QMessageBox, QSplitter, QSpacerItem
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QColor
from ui.theme import C


def lbl(text, size=13, bold=False, color=None, wrap=False):
    l = QLabel(text)
    f = QFont(); f.setPointSize(size); f.setBold(bold)
    l.setFont(f)
    if color: l.setStyleSheet(f"color:{color};background:transparent;")
    if wrap:  l.setWordWrap(True)
    return l


def hline():
    f = QFrame(); f.setFrameShape(QFrame.Shape.HLine)
    f.setStyleSheet(f"color:{C['border']};max-height:1px;"); return f


def vline():
    f = QFrame(); f.setFrameShape(QFrame.Shape.VLine)
    f.setStyleSheet(f"color:{C['border']};max-width:1px;"); return f


def spacer_h():
    sp = QWidget(); sp.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
    return sp


def scroll_area(widget):
    sc = QScrollArea()
    sc.setWidgetResizable(True)
    sc.setStyleSheet("QScrollArea{border:none;background:transparent;}")
    sc.setWidget(widget)
    return sc


class Card(QFrame):
    def __init__(self, parent=None, accent=False):
        super().__init__(parent)
        self.setObjectName("card_accent" if accent else "card")
        self._lay = QVBoxLayout(self)
        self._lay.setContentsMargins(16, 14, 16, 14)
        self._lay.setSpacing(10)

    def layout(self): return self._lay
    def add(self, w): self._lay.addWidget(w)
    def add_layout(self, l): self._lay.addLayout(l)


class KPICard(QFrame):
    def __init__(self, titulo, valor, subtitulo="", color=None, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setMinimumSize(160, 105)
        self.setMaximumHeight(130)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(18, 14, 18, 14)
        lay.setSpacing(4)
        col = color or C["accent"]
        t = lbl(titulo, 9, color=C["text2"]); t.setObjectName("subtitle")
        v = lbl(valor, 22, bold=True, color=col)
        v.setObjectName("kpi_val")
        v.setWordWrap(True)
        s = lbl(subtitulo, 9, color=C["text2"])
        lay.addWidget(t); lay.addWidget(v); lay.addWidget(s)

    def update_val(self, valor, color=None):
        for i in range(self.layout().count()):
            w = self.layout().itemAt(i).widget()
            if w and w.objectName() == "kpi_val":
                w.setText(valor)
                if color: w.setStyleSheet(f"color:{color};font-size:22px;font-weight:bold;")
                break


class ChartCard(QFrame):
    def __init__(self, canvas, min_h=340, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(6, 6, 6, 6)
        canvas.setMinimumHeight(min_h)
        lay.addWidget(canvas)


class PageBase(QWidget):
    """Base para todas las páginas — scroll + layout vertical."""
    def __init__(self, parent=None):
        super().__init__(parent)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        inner = QWidget()
        self._lay = QVBoxLayout(inner)
        self._lay.setContentsMargins(24, 22, 24, 24)
        self._lay.setSpacing(16)
        sc = scroll_area(inner)
        outer.addWidget(sc)

    def lay(self): return self._lay

    def _clear(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
            elif item.layout(): self._clear(item.layout())


class ConfirmDialog(QDialog):
    def __init__(self, titulo, mensaje, parent=None):
        super().__init__(parent)
        self.setWindowTitle(titulo)
        self.setFixedSize(380, 160)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 20, 24, 20); lay.setSpacing(16)
        lay.addWidget(lbl(mensaje, 12, wrap=True))
        btns = QHBoxLayout()
        btn_ok  = QPushButton("Confirmar"); btn_ok.setObjectName("btn_danger")
        btn_no  = QPushButton("Cancelar")
        btn_ok.clicked.connect(self.accept)
        btn_no.clicked.connect(self.reject)
        btns.addWidget(spacer_h()); btns.addWidget(btn_no); btns.addWidget(btn_ok)
        lay.addLayout(btns)


def msg_ok(parent, titulo, texto):
    QMessageBox.information(parent, titulo, texto)

def msg_err(parent, titulo, texto):
    QMessageBox.critical(parent, titulo, texto)
