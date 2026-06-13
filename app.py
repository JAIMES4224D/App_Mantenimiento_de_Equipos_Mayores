#!/usr/bin/env python3
"""
MantenimientoApp — Sistema de Gestión de Costos de Mantenimiento
Equipos Mayores

Ejecutar:
    python app.py
"""
import sys
import os

def obtener_ruta_recurso(ruta_relativa):
    """ Obtiene la ruta absoluta para recursos, compatible con el modo de desarrollo y con PyInstaller """
    try:
        # PyInstaller crea una carpeta temporal y guarda la ruta en _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, ruta_relativa)

# Asegurar que el directorio raíz está en el path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

# Cambiar directorio de trabajo al del script (para que SQLite cree el .db aquí)
os.chdir(BASE_DIR)

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont, QIcon  
import db.database as db_
from ui.theme import STYLESHEET
from ui.login import LoginWindow
from ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("MantenimientoApp")
    app.setOrganizationName("GestionMantenimiento")
    app.setStyleSheet(STYLESHEET)

    # ── ASIGNAR ICONO GLOBAL A TODAS LAS VENTANAS ──────────────────────────
    # Usamos obtener_ruta_recurso para que PyInstaller lo encuentre en el .exe
    ruta_icono = obtener_ruta_recurso("icon.ico") # <-- Cambia por el nombre real de tu archivo .ico
    app.setWindowIcon(QIcon(ruta_icono))
    # ───────────────────────────────────────────────────────────────────────

    font = QFont("Segoe UI", 10)
    app.setFont(font)

    # Inicializar BD (crea tablas y datos semilla si no existe)
    db_.init_db()

    # Abrir login
    login = LoginWindow()

    def on_login(usuario):
        window = MainWindow(usuario)
        window.show()
        app._main_window = window  # evitar GC

    login.login_ok.connect(on_login)

    if login.exec() == 0 and not hasattr(app, "_main_window"):
        sys.exit(0)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()