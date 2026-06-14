"""Ventana principal con sidebar y navegación por páginas."""
import pandas as pd
from PyQt6.QtCore import QThread, QObject, pyqtSignal, Qt, QTimer
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QFrame, 
    QLabel, QPushButton, QStackedWidget, QSizePolicy, QFileDialog, 
    QMessageBox, QInputDialog, QProgressDialog, QApplication 
)
from PyQt6.QtGui import QAction
from ui.theme import C, STYLESHEET
from ui.widgets import lbl, hline
from ui.pages import DashboardPage, OrdenesPage, ReportesPage, CatalogosPage, AdminPage
import db.database as db_

# ═════════════════════════════════════════════════════════════════════════
#  1. HILO TRABAJADOR PARA LA BASE DE DATOS (CORREGIDO PARA FECHAS RÁPIDAS)
# ═════════════════════════════════════════════════════════════════════════
class ImportarExcelWorker(QObject):
    progreso = pyqtSignal(int)
    finalizado = pyqtSignal(int, list)

    def __init__(self, df, usuario_id):
        super().__init__()
        self.df = df
        self.usuario_id = usuario_id

    def run(self):
        import pandas as pd
        from datetime import datetime
        import db.database as database_

        conn = database_.get_conn()
        c = conn.cursor()
        insertados = 0
        actualizados = 0
        errores = []
        total_filas = len(self.df)

        for idx, row in self.df.iterrows():
            try:
                nro_orden = str(row.get("Nro. Orden de Compra", "")).strip()
                if not nro_orden or nro_orden.lower() in ["nan", "none", ""]:
                    continue

                fecha_raw = row.get("Fecha")
                if pd.notna(fecha_raw):
                    try: 
                        fecha = pd.to_datetime(fecha_raw, dayfirst=True).strftime("%Y-%m-%d")
                    except: 
                        fecha = datetime.now().strftime("%Y-%m-%d")
                else:
                    fecha = datetime.now().strftime("%Y-%m-%d")
                    
                anio = int(fecha[:4])
                mes = int(fecha[5:7])

                recurso_str = str(row.get("Recurso", "Mantenimiento General")).strip()
                equipo_nombre = database_._identificar_equipo_por_recurso(recurso_str)

                obra_id = database_.get_or_create_obra(str(row.get("Proyecto", "Sin Obra")), conn)
                equipo_id = database_.get_or_create_equipo(equipo_nombre, conn)
                proveedor_id = database_.get_or_create_proveedor(str(row.get("Proveedor", "Sin Proveedor")), conn)
                tipo_id = database_.get_or_create_tipo(str(row.get("Clase Esp.", "Mantenimiento General")), str(row.get("Clase", "Servicios")), conn)

                def to_float(val):
                    if pd.isna(val) or str(val).strip().lower() in ["nan", "none", ""]: return 0.0
                    try: return float(val)
                    except: return 0.0

                estado = str(row.get("Estado", "Activo")).strip()
                clase = str(row.get("Clase", "Servicios")).strip()
                clase_esp = str(row.get("Clase Esp.", "")).strip()
                observacion = str(row.get("Observación", "")).strip()
                moneda = str(row.get("Moneda", "USD")).strip()
                forma_pago = str(row.get("Forma de pago", "")).strip()
                unidad = str(row.get("Unidad", "glb")).strip()
                gestor = str(row.get("Gestor de Compra", "")).strip()
                estado_fact = str(row.get("Estado Facturación", "Pendiente")).strip()

                cantidad = to_float(row.get("Cantidad", 1.0))
                precio_sin_igv = to_float(row.get("Precio Sin I.G.V.", 0.0))
                valor_igv = to_float(row.get("Valor del I.G.V.", 0.0))
                parcial_calc = to_float(row.get("Parcial Calculado", 0.0))
                parcial_igv = to_float(row.get("Parcial Con I.G.V.", 0.0))
                dcto = to_float(row.get("Dcto Total.(%)", 0.0))
                valor_total = to_float(row.get("Valor Total", 0.0))

                if parcial_calc == 0.0 and precio_sin_igv > 0.0: parcial_calc = round(cantidad * precio_sin_igv, 2)
                if valor_igv == 0.0 and precio_sin_igv > 0.0: valor_igv = round(precio_sin_igv * 0.18, 2)
                if parcial_igv == 0.0: parcial_igv = round(parcial_calc + (valor_igv * cantidad), 2)
                if valor_total == 0.0: valor_total = round(parcial_igv - (parcial_igv * (dcto / 100.0)), 2)

                existe = c.execute("SELECT id FROM ordenes WHERE nro_orden=?", (nro_orden,)).fetchone()

                if existe:
                    c.execute("""UPDATE ordenes SET obra_id=?, equipo_id=?, proveedor_id=?, tipo_id=?, fecha=?, anio=?, mes=?, estado=?, clase=?, clase_esp=?, recurso=?, observacion=?, moneda=?, forma_pago=?, unidad=?, cantidad=?, precio_sin_igv=?, valor_igv=?, parcial_calculado=?, parcial_con_igv=?, dcto_total=?, valor_total=?, estado_facturacion=?, gestor_compra=?, updated_at=datetime('now','localtime') WHERE id=?""", 
                              (obra_id, equipo_id, proveedor_id, tipo_id, fecha, anio, mes, estado, clase, clase_esp, recurso_str, observacion, moneda, forma_pago, unidad, cantidad, precio_sin_igv, valor_igv, parcial_calc, parcial_igv, dcto, valor_total, estado_fact, gestor, existe["id"]))
                    actualizados += 1
                else:
                    c.execute("""INSERT INTO ordenes (nro_orden, obra_id, equipo_id, proveedor_id, tipo_id, fecha, anio, mes, estado, clase, clase_esp, recurso, observacion, moneda, forma_pago, unidad, cantidad, precio_sin_igv, valor_igv, parcial_calculado, parcial_con_igv, dcto_total, valor_total, estado_facturacion, gestor_compra, creado_por) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", 
                              (nro_orden, obra_id, equipo_id, proveedor_id, tipo_id, fecha, anio, mes, estado, clase, clase_esp, recurso_str, observacion, moneda, forma_pago, unidad, cantidad, precio_sin_igv, valor_igv, parcial_calc, parcial_igv, dcto, valor_total, estado_fact, gestor, self.usuario_id))
                    insertados += 1

                pct = int(((idx + 1) / total_filas) * 100)
                self.progreso.emit(pct)

            except Exception as e:
                errores.append(f"Fila {idx+2}: {str(e)}")

        conn.commit()
        database_.log_actividad(self.usuario_id, "IMPORT_EXCEL", f"Total: {insertados+actualizados} registros", conn)
        conn.commit()
        conn.close()
        self.finalizado.emit((insertados + actualizados), errores)


# ═════════════════════════════════════════════════════════════════════════
#  2. INTERFAZ PRINCIPAL CON REFRESCO INTEGRAL DE PÁGINAS
# ═════════════════════════════════════════════════════════════════════════
class MainWindow(QMainWindow):
    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario
        self.setWindowTitle(f"MantenimientoApp — {usuario['nombre']} [{usuario['rol'].upper()}]")
        self.setMinimumSize(1340, 820)
        self.setStyleSheet(STYLESHEET)
        self._pages = []
        self._nav_btns = []
        self._build()
        self._setup_menu()
        self._nav(0)

    def _setup_menu(self):
        menubar = self.menuBar()
        archivo_menu = menubar.addMenu("Archivo")
        import_action = QAction("Importar desde Excel (Base)", self)
        import_action.triggered.connect(self.importar_excel)
        archivo_menu.addAction(import_action)

    def importar_excel(self):
        archivo, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar archivo Excel", "", "Archivos Excel o CSV (*.xlsx *.xls *.csv)"
        )
        if not archivo:
            return

        try:
            if archivo.endswith('.csv'):
                df = pd.read_csv(archivo, dayfirst=True)
            else:
                df = pd.read_excel(archivo)
        except Exception as e:
            QMessageBox.critical(self, "Error al leer archivo", f"No se pudo cargar el archivo:\n{str(e)}")
            return

        self.progress_dialog = QProgressDialog("Procesando e importando registros a SQLite...", "Cancelar", 0, 100, self)
        self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress_dialog.setValue(0)
        self.progress_dialog.show()

        self.import_thread = QThread()
        self.import_worker = ImportarExcelWorker(df, self.usuario["id"])
        self.import_worker.moveToThread(self.import_thread)

        self.import_thread.started.connect(self.import_worker.run)
        self.import_worker.progreso.connect(self.progress_dialog.setValue)
        self.import_worker.finalizado.connect(self._on_import_completo)
        
        self.import_worker.finalizado.connect(self.import_thread.quit)
        self.import_worker.finalizado.connect(self.import_worker.deleteLater)
        self.import_thread.finished.connect(self.import_thread.deleteLater)

        self.import_thread.start()

    def _on_import_completo(self, total, errores):
        self.progress_dialog.close()
        if errores:
            msg = f"Importación completada con {len(errores)} observaciones.\nSe registraron {total} órdenes con éxito."
            QMessageBox.warning(self, "Importación con Advertencias", msg)
        else:
            QMessageBox.information(self, "Éxito", f"Se importaron correctamente {total} registros sin errores.")
        
        for page in self._pages:
            if hasattr(page, "refresh"):
                try:
                    page.refresh()
                except Exception:
                    pass

    def _build(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0); root.setSpacing(0)
        root.addWidget(self._build_sidebar())
        root.addWidget(self._build_content(), 1)

    def _build_sidebar(self):
        bar = QFrame(); bar.setObjectName("sidebar"); bar.setFixedWidth(230)
        lay = QVBoxLayout(bar); lay.setContentsMargins(0, 0, 0, 0); lay.setSpacing(0)
        
        hdr = QWidget(); hdr.setFixedHeight(72); hdr.setStyleSheet(f"background:{C['sidebar']};")
        hl = QVBoxLayout(hdr); hl.setContentsMargins(18,0,18,0); hl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hl.addWidget(lbl("⚙ MantenimientoApp", 12, bold=True, color=C["accent"]))
        hl.addWidget(lbl(f"v1.0 | {self.usuario['rol'].capitalize()}", 9, color=C["text2"]))
        lay.addWidget(hdr); lay.addWidget(hline())

        nav_items = [("🏠 Dashboard", 0), ("📋 Órdenes de Compra", 1), ("📊 Reportes", 2), ("📁 Catálogos", 3)]
        if self.usuario["rol"] == "admin": nav_items.append(("⚙ Administración", 4))

        for label, idx in nav_items:
            btn = QPushButton(label); btn.setObjectName("nav_btn")
            btn.clicked.connect(lambda _, i=idx: self._nav(i))
            lay.addWidget(btn); self._nav_btns.append((idx, btn))

        lay.addStretch(); lay.addWidget(hline())
        
        # ── NUEVO: BOTÓN DE CAMBIO DE FORMATO (OSCURO / CLARO) ──
        self.es_modo_oscuro = True
        self.btn_tema = QPushButton("☀️ Modo Claro")
        self.btn_tema.setStyleSheet(f"QPushButton {{background:transparent;color:{C['text2']};border:none;padding:12px;text-align:left;}} QPushButton:hover {{background:rgba(0,200,255,0.07);color:{C['accent']};}}")
        self.btn_tema.clicked.connect(self.alternar_tema)
        lay.addWidget(self.btn_tema)
        
        user_frame = QFrame(); user_frame.setStyleSheet(f"background:{C['sidebar']};padding:4px;")
        ul = QVBoxLayout(user_frame); ul.setSpacing(3)
        ul.addWidget(lbl(f"👤 {self.usuario['nombre']}", 10, bold=True, color=C["text"]))
        ul.addWidget(lbl(self.usuario["username"], 9, color=C["text2"]))
        lay.addWidget(user_frame)

        btn_logout = QPushButton("⏻ Cerrar Sesión")
        btn_logout.setStyleSheet(f"QPushButton {{background:transparent;color:{C['text2']};border:none;padding:12px;text-align:left;}} QPushButton:hover {{background:{C['red']}22;}}")
        btn_logout.clicked.connect(self._logout)
        lay.addWidget(btn_logout)
        return bar

    def _build_content(self):
        self.stack = QStackedWidget()
        self._pages = [DashboardPage(self.usuario), OrdenesPage(self.usuario), 
                       ReportesPage(self.usuario), CatalogosPage(self.usuario), 
                       AdminPage(self.usuario) if self.usuario["rol"]=="admin" else QWidget()]
        for p in self._pages: self.stack.addWidget(p)
        self._timer = QTimer(); self._timer.timeout.connect(self._auto_refresh); self._timer.start(60_000)
        return self.stack

    def _nav(self, idx):
        self.stack.setCurrentIndex(idx)
        for nav_idx, btn in self._nav_btns:
            btn.setProperty("active", nav_idx == idx); btn.style().unpolish(btn); btn.style().polish(btn)
        page = self._pages[idx]
        if hasattr(page, "refresh"): page.refresh()

    def _auto_refresh(self):
        page = self._pages[self.stack.currentIndex()]
        if hasattr(page, "refresh"): page.refresh()

    def _logout(self):
        self._timer.stop(); self.close()
        from ui.login import LoginWindow
        login = LoginWindow()
        login.show()
    
    def alternar_tema(self):
        """Alterna las paletas de colores globales y refresca la aplicación completa."""
        import ui.theme as theme_mod
        
        if self.es_modo_oscuro:
            theme_mod.C = theme_mod.C_LIGHT.copy()
            self.btn_tema.setText("🌙 Modo Oscuro")
            self.es_modo_oscuro = False
        else:
            theme_mod.C = theme_mod.C_DARK.copy()
            self.btn_tema.setText("☀️ Modo Claro")
            self.es_modo_oscuro = True
            
        nuevo_style = theme_mod.obtener_stylesheet(theme_mod.C)
        QApplication.instance().setStyleSheet(nuevo_style)
        
        import ui.charts as charts_mod
        charts_mod.BG   = theme_mod.C["bg"]
        charts_mod.PAN  = theme_mod.C["card"]
        charts_mod.GRID = theme_mod.C["border"]
        charts_mod.TXT  = theme_mod.C["text"]
        charts_mod.TXT2 = theme_mod.C["text2"]
        charts_mod.ACC  = theme_mod.C["accent"]
        charts_mod.ACC2 = theme_mod.C["accent2"]
        
        self._auto_refresh()