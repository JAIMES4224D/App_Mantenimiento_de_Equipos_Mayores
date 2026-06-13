"""Ventana de Login."""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QWidget
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QKeyEvent
from ui.theme import C
import db.database as db_


class LoginWindow(QDialog):
    login_ok = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("MantenimientoApp — Iniciar Sesión")
        self.setFixedSize(440, 540)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self._build()
        self._drag_pos = None

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        # Cabecera
        header = QFrame()
        header.setFixedHeight(160)
        header.setStyleSheet(f"background: qlineargradient(x1:0,y1:0,x2:1,y2:1,"
                             f"stop:0 {C['sidebar']}, stop:1 {C['card']});")
        hl = QVBoxLayout(header)
        hl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon = QLabel("⚙")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet(f"font-size:48px; color:{C['accent']};")

        titulo = QLabel("MantenimientoApp")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        f = QFont(); f.setPointSize(17); f.setBold(True)
        titulo.setFont(f)
        titulo.setStyleSheet(f"color:{C['accent']};")

        sub = QLabel("Sistema de Gestión de Costos")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setStyleSheet(f"color:{C['text2']}; font-size:11px;")

        hl.addWidget(icon); hl.addWidget(titulo); hl.addWidget(sub)
        root.addWidget(header)

        # Formulario
        form = QFrame()
        form.setStyleSheet(f"background:{C['panel']};")
        fl = QVBoxLayout(form)
        fl.setContentsMargins(40, 32, 40, 32)
        fl.setSpacing(14)

        # User
        lbl_u = QLabel("Usuario")
        lbl_u.setStyleSheet(f"color:{C['text2']}; font-size:11px; font-weight:bold;")
        self.inp_user = QLineEdit()
        self.inp_user.setPlaceholderText("Ingrese su usuario")
        self.inp_user.setFixedHeight(42)
        self.inp_user.setText("admin")

        # Password
        lbl_p = QLabel("Contraseña")
        lbl_p.setStyleSheet(f"color:{C['text2']}; font-size:11px; font-weight:bold;")
        self.inp_pass = QLineEdit()
        self.inp_pass.setPlaceholderText("Ingrese su contraseña")
        self.inp_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.inp_pass.setFixedHeight(42)
        self.inp_pass.setText("admin123")
        self.inp_pass.returnPressed.connect(self._do_login)

        # Error label
        self.lbl_err = QLabel("")
        self.lbl_err.setStyleSheet(f"color:{C['red']}; font-size:11px;")
        self.lbl_err.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Botón
        self.btn_login = QPushButton("  Iniciar Sesión")
        self.btn_login.setObjectName("btn_primary")
        self.btn_login.setFixedHeight(46)
        f2 = QFont(); f2.setPointSize(13); f2.setBold(True)
        self.btn_login.setFont(f2)
        
        self.btn_login.clicked.connect(self._do_login)

        # Credenciales por defecto (hint)
        hint = QLabel("Usuario por defecto:  admin / admin123")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint.setStyleSheet(f"color:{C['text2']}; font-size:10px;")

        # Botón cerrar
        btn_x = QPushButton("✕ Cerrar")
        btn_x.setStyleSheet(f"background:transparent;color:{C['text2']};border:none;font-size:11px;")
        btn_x.clicked.connect(self.reject)
        btn_x_row = QHBoxLayout()
        btn_x_row.addStretch(); btn_x_row.addWidget(btn_x)

        fl.addWidget(lbl_u);        fl.addWidget(self.inp_user)
        fl.addWidget(lbl_p);        fl.addWidget(self.inp_pass)
        fl.addWidget(self.lbl_err)
        fl.addSpacing(6)
        fl.addWidget(self.btn_login)
        fl.addSpacing(6)
        fl.addWidget(hint)
        fl.addStretch()
        fl.addLayout(btn_x_row)

        root.addWidget(form, 1)

    def _do_login(self):
        u = self.inp_user.text().strip()
        p = self.inp_pass.text()
        if not u or not p:
            self.lbl_err.setText("Complete todos los campos")
            return
        self.btn_login.setText("Verificando...")
        self.btn_login.setEnabled(False)
        user = db_.login(u, p)
        if user:
            self.lbl_err.setText("")
            self.login_ok.emit(user)
            self.accept()
        else:
            self.lbl_err.setText("⚠  Usuario o contraseña incorrectos")
            self.btn_login.setText("  Iniciar Sesión")
            self.btn_login.setEnabled(True)
            self.inp_pass.clear()
            self.inp_pass.setFocus()

    # Drag sin barra de título
    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = e.globalPosition().toPoint()

    def mouseMoveEvent(self, e):
        if self._drag_pos and e.buttons() == Qt.MouseButton.LeftButton:
            self.move(self.pos() + e.globalPosition().toPoint() - self._drag_pos)
            self._drag_pos = e.globalPosition().toPoint()

    def mouseReleaseEvent(self, e):
        self._drag_pos = None
