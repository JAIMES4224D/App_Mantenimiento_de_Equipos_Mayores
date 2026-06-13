"""Páginas principales del sistema."""
import sys
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
    QComboBox, QLineEdit, QDialog, QGridLayout, QCheckBox,
    QScrollArea, QSizePolicy, QTabWidget, QTextEdit,
    QGroupBox, QFormLayout, QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QObject
from PyQt6.QtGui import QFont, QColor
import db.database as db_
from ui.theme import C, MESES, MESES_CORTO
from ui.widgets import (lbl, hline, Card, KPICard, ChartCard,
                         PageBase, ConfirmDialog, msg_ok, msg_err, spacer_h)
import ui.charts as charts_mod
from ui.orden_form import OrdenFormDialog

# ══════════════════════════════════════════════════════════════
#  HILO TRABAJADOR EN SEGUNDO PLANO PARA CARGAR TABLA DE ÓRDENES
# ══════════════════════════════════════════════════════════════
class CargarOrdenesWorker(QObject):
    datos_cargados = pyqtSignal(list)

    def __init__(self, filtros):
        super().__init__()
        self.filtros = filtros

    def run(self):
        ordenes = db_.get_ordenes(self.filtros)
        self.datos_cargados.emit(ordenes)


# ══════════════════════════════════════════════════════════════
#  PÁGINA: DASHBOARD
# ══════════════════════════════════════════════════════════════
class DashboardPage(PageBase):
    def __init__(self, usuario, parent=None):
        super().__init__(parent)
        self.usuario = usuario
        self._build()

    def _build(self):
        L = self.lay()
        L.addWidget(lbl("Dashboard", 20, bold=True, color=C["accent"]))
        L.addWidget(lbl("Resumen general del sistema de costos de mantenimiento", 10, color=C["text2"]))

        # KPIs
        self.kpi_row = QHBoxLayout(); self.kpi_row.setSpacing(12)
        self.kpi_total   = KPICard("Costo Total Histórico", "$0", "Todas las órdenes", C["accent"])
        self.kpi_anio    = KPICard("Costo Año Actual",      "$0", "—", C["green"])
        self.kpi_ordenes = KPICard("Órdenes Registradas",   "0",  "total", C["accent2"])
        self.kpi_provs   = KPICard("Proveedores Activos",   "0",  "empresas", C["amber"])
        self.kpi_obras   = KPICard("Obras Activas",         "0",  "proyectos", C["purple"])
        for k in [self.kpi_total, self.kpi_anio, self.kpi_ordenes,
                  self.kpi_provs, self.kpi_obras]:
            self.kpi_row.addWidget(k)
        L.addLayout(self.kpi_row)

        # Gráficos
        self.chart_anual_holder = QVBoxLayout()
        L.addLayout(self.chart_anual_holder)

        row2 = QHBoxLayout(); row2.setSpacing(14)
        self.chart_pie_holder  = QVBoxLayout()
        self.chart_prov_holder = QVBoxLayout()
        row2.addLayout(self.chart_pie_holder, 1)
        row2.addLayout(self.chart_prov_holder, 1)
        L.addLayout(row2)
        L.addStretch()
        self.refresh()

    def refresh(self):
        kpis = db_.kpis_dashboard()
        self.kpi_total.update_val(f"${kpis['total_historico']:,.0f}")
        self.kpi_anio.update_val(f"${kpis['total_anio']:,.0f}", C["green"])
        self.kpi_ordenes.update_val(str(kpis["total_ordenes"]))
        self.kpi_provs.update_val(str(kpis["num_proveedores"]))
        self.kpi_obras.update_val(str(kpis["num_obras"]))

        self._clear(self.chart_anual_holder)
        self._clear(self.chart_pie_holder)
        self._clear(self.chart_prov_holder)

        datos_anual = db_.stats_anual()
        c1 = charts_mod.linea_anual(datos_anual)
        c1.setMinimumHeight(310)
        self.chart_anual_holder.addWidget(ChartCard(c1, 310))

        datos_tipo = db_.stats_por_tipo()
        c2 = charts_mod.pastel_tipo(datos_tipo)
        c2.setMinimumHeight(300)
        self.chart_pie_holder.addWidget(ChartCard(c2, 300))

        datos_prov = db_.stats_por_proveedor()
        c3 = charts_mod.barras_proveedores(datos_prov)
        c3.setMinimumHeight(300)
        self.chart_prov_holder.addWidget(ChartCard(c3, 300))


# ══════════════════════════════════════════════════════════════
#  PÁGINA: ÓRDENES DE COMPRA (CON PAGINACIÓN ULTRA RÁPIDA)
# ══════════════════════════════════════════════════════════════
class OrdenesPage(PageBase):
    def __init__(self, usuario, parent=None):
        super().__init__(parent)
        self.usuario = usuario
        # Variables de control de paginación para evitar congelamientos
        self.todas_las_ordenes = []
        self.pagina_actual = 0
        self.filas_por_pagina = 50
        self._build()

    def _build(self):
        L = self.lay()
        L.addWidget(lbl("Órdenes de Compra", 20, bold=True, color=C["accent"]))

        # Barra de herramientas
        toolbar = QHBoxLayout(); toolbar.setSpacing(10)
        self.inp_buscar = QLineEdit()
        self.inp_buscar.setPlaceholderText("🔍  Buscar por N° orden, recurso o proveedor...")
        self.inp_buscar.setFixedHeight(38)
        self.inp_buscar.setMinimumWidth(280)
        self.inp_buscar.textChanged.connect(self.refresh)

        self.cb_anio = QComboBox(); self.cb_anio.setFixedHeight(38)
        self.cb_anio.addItem("Todos los años")
        for a in db_.get_anios(): self.cb_anio.addItem(str(a))
        self.cb_anio.currentIndexChanged.connect(self.refresh)

        self.cb_obra = QComboBox(); self.cb_obra.setFixedHeight(38)
        self.cb_obra.addItem("Todas las obras")
        self._obra_map = {}
        for o in db_.get_obras():
            self.cb_obra.addItem(o["nombre"])
            self._obra_map[o["nombre"]] = o["id"]
        self.cb_obra.currentIndexChanged.connect(self.refresh)

        btn_new = QPushButton("➕  Nueva Orden"); btn_new.setObjectName("btn_success")
        btn_new.setFixedHeight(38); btn_new.clicked.connect(self._nueva_orden)

        btn_export = QPushButton("⬇  Exportar"); btn_export.setFixedHeight(38)
        btn_export.clicked.connect(self._exportar)

        toolbar.addWidget(self.inp_buscar)
        toolbar.addWidget(self.cb_anio)
        toolbar.addWidget(self.cb_obra)
        toolbar.addStretch()
        toolbar.addWidget(btn_export)
        toolbar.addWidget(btn_new)
        L.addLayout(toolbar)

        # Tabla
        cols = ["ID","N° Orden","Fecha","Obra","Equipo","Tipo","Proveedor",
                "Recurso","Cantidad","Precio s/IGV","Total","Estado","Acciones"]
        self.tabla = QTableWidget(0, len(cols))
        self.tabla.setHorizontalHeaderLabels(cols)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.tabla.horizontalHeader().setStretchLastSection(False)
        self.tabla.setShowGrid(True)
        L.addWidget(self.tabla)

        # ── CONTROLES DE PAGINACIÓN VISUALES ──
        pag_layout = QHBoxLayout()
        self.btn_ant = QPushButton("◀ Anterior")
        self.btn_ant.setFixedHeight(32)
        self.btn_ant.clicked.connect(self._pagina_anterior)
        
        self.lbl_paginacion = lbl("Página 1 de 1", 11, bold=True, color=C["text"])
        self.lbl_paginacion.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.btn_sig = QPushButton("Siguiente ▶")
        self.btn_sig.setFixedHeight(32)
        self.btn_sig.clicked.connect(self._pagina_siguiente)
        
        pag_layout.addWidget(self.btn_ant)
        pag_layout.addWidget(self.lbl_paginacion, 1)
        pag_layout.addWidget(self.btn_sig)
        L.addLayout(pag_layout)

        self.lbl_total_row = lbl("Cargando...", 10, color=C["text2"])
        L.addWidget(self.lbl_total_row)
        
        self.refresh()

    def refresh(self):
        """Lanza la consulta en segundo plano de manera asíncrona."""
        filtros = {}
        busq = self.inp_buscar.text().strip()
        if busq: filtros["busqueda"] = busq
            
        anio_txt = self.cb_anio.currentText()
        if anio_txt and anio_txt != "Todos los años": 
            try: filtros["anio"] = int(anio_txt)
            except ValueError: pass
                
        obra_txt = self.cb_obra.currentText()
        if obra_txt and obra_txt != "Todas las obras":
            filtros["obra_id"] = self._obra_map.get(obra_txt)

        # Evitar bloquear reiniciando la página actual a cero al buscar
        if self.sender() == self.inp_buscar or self.sender() == self.cb_anio or self.sender() == self.cb_obra:
            self.pagina_actual = 0

        self.lbl_total_row.setText("🔍 Buscando registros en segundo plano...")
        
        self.load_thread = QThread()
        self.load_worker = CargarOrdenesWorker(filtros)
        self.load_worker.moveToThread(self.load_thread)

        self.load_thread.started.connect(self.load_worker.run)
        self.load_worker.datos_cargados.connect(self._recibir_datos)
        
        self.load_worker.datos_cargados.connect(self.load_thread.quit)
        self.load_worker.datos_cargados.connect(self.load_worker.deleteLater)
        self.load_thread.finished.connect(self.load_thread.deleteLater)

        self.load_thread.start()

    def _recibir_datos(self, ordenes):
        """Guarda la lista completa y gatilla el renderizado veloz de la página actual."""
        self.todas_las_ordenes = ordenes
        self._renderizar_pagina_actual()

    def _renderizar_pagina_actual(self):
        """Renderiza únicamente un bloque pequeño de 50 filas de forma instantánea."""
        self.tabla.setUpdatesEnabled(False)
        self.tabla.setRowCount(0)
        
        total_registros = len(self.todas_las_ordenes)
        
        # Calcular límites de índices
        start_idx = self.pagina_actual * self.filas_por_pagina
        end_idx = min(start_idx + self.filas_por_pagina, total_registros)
        
        # Extraer el subconjunto de datos (Chunking)
        bloque_ordenes = self.todas_las_ordenes[start_idx:end_idx]
        
        total_costo_historico = sum(r.get("parcial_calculado") or 0 for r in self.todas_las_ordenes)

        for r in bloque_ordenes:
            row = self.tabla.rowCount()
            self.tabla.insertRow(row)
            costo = r.get("parcial_calculado") or 0
            vals = [
                str(r["id"]),
                r.get("nro_orden",""),
                (r.get("fecha","") or "")[:10],
                r.get("obra","") or "",
                r.get("equipo","") or "",
                r.get("tipo","") or "",
                (r.get("proveedor","") or "")[:28],
                (r.get("recurso","") or "")[:35],
                f"{r.get('cantidad',1):.2f}",
                f"${r.get('precio_sin_igv',0):,.2f}",
                f"${costo:,.2f}",
                r.get("estado",""),
            ]
            for col, val in enumerate(vals):
                item = QTableWidgetItem(val)
                item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                if col == 10:
                    item.setForeground(QColor(C["accent"]))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.tabla.setItem(row, col, item)

            # Botones de acciones por celda
            cell = QWidget()
            cl = QHBoxLayout(cell); cl.setContentsMargins(4,2,4,2); cl.setSpacing(6)
            cl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            btn_e = QPushButton("✏"); btn_e.setObjectName("table_action"); btn_e.setFixedSize(30,26)
            btn_d = QPushButton("🗑"); btn_d.setObjectName("table_action"); btn_d.setFixedSize(30,26)
            
            oid = r["id"]
            btn_e.clicked.connect(lambda _, i=oid: self._editar(i))
            btn_d.clicked.connect(lambda _, i=oid: self._eliminar(i))
            cl.addWidget(btn_e); cl.addWidget(btn_d)
            self.tabla.setCellWidget(row, 12, cell)

        self.tabla.setUpdatesEnabled(True)
        
        # Actualizar estado e interfaz de botones
        total_paginas = max(1, (total_registros + self.filas_por_pagina - 1) // self.filas_por_pagina)
        self.lbl_paginacion.setText(f"Página {self.pagina_actual + 1} de {total_paginas}")
        
        self.btn_ant.setEnabled(self.pagina_actual > 0)
        self.btn_sig.setEnabled(self.pagina_actual < total_paginas - 1)
        
        self.lbl_total_row.setText(
            f"  Mostrando {start_idx + 1}-{end_idx} de {total_registros} registros  |  Total General Filtrado: ${total_costo_historico:,.2f}"
        )

    def _pagina_anterior(self):
        if self.pagina_actual > 0:
            self.pagina_actual -= 1
            self._renderizar_pagina_actual()

    def _pagina_siguiente(self):
        total_paginas = (len(self.todas_las_ordenes) + self.filas_por_pagina - 1) // self.filas_por_pagina
        if self.pagina_actual < total_paginas - 1:
            self.pagina_actual += 1
            self._renderizar_pagina_actual()

    def _nueva_orden(self):
        dlg = OrdenFormDialog(self.usuario, parent=self)
        if dlg.exec(): self.refresh()

    def _editar(self, orden_id):
        data = db_.get_orden(orden_id)
        if not data: return
        dlg = OrdenFormDialog(self.usuario, orden_data=data, parent=self)
        if dlg.exec(): self.refresh()

    def _eliminar(self, orden_id):
        data = db_.get_orden(orden_id)
        if not data: return
        dlg = ConfirmDialog("Eliminar Orden", f"¿Eliminar la orden {data['nro_orden']}?\n\nEsta acción no se puede deshacer.", self)
        if dlg.exec():
            db_.eliminar_orden(orden_id, self.usuario["id"])
            self.refresh()

    def _exportar(self):
        path, _ = QFileDialog.getSaveFileName(self, "Exportar órdenes", "ordenes_mantenimiento.xlsx", "Excel (*.xlsx)")
        if not path: return
        try:
            import pandas as pd
            ordenes = db_.get_ordenes()
            cols = ["id","nro_orden","fecha","obra","equipo","tipo","proveedor",
                    "recurso","cantidad","precio_sin_igv","parcial_calculado",
                    "valor_total","estado","estado_facturacion","created_at"]
            rows = [{c: o.get(c,"") for c in cols} for o in ordenes]
            df = pd.DataFrame(rows)
            df.to_excel(path, index=False)
            msg_ok(self, "Exportado", f"Archivo guardado:\n{path}")
        except Exception as e:
            msg_err(self, "Error", str(e))


# ══════════════════════════════════════════════════════════════
#  PÁGINA: REPORTES Y GRÁFICOS 
# ══════════════════════════════════════════════════════════════
class ReportesPage(PageBase):
    def __init__(self, usuario, parent=None):
        super().__init__(parent)
        self.usuario = usuario
        self._build()

    def _build(self):
        L = self.lay()
        L.addWidget(lbl("Reportes y Gráficos", 20, bold=True, color=C["accent"]))

        filt = QHBoxLayout(); filt.setSpacing(12)
        self.inp_buscar = QLineEdit()
        self.inp_buscar.setPlaceholderText("🔍  Filtrar gráficos por texto o proveedor...")
        self.inp_buscar.setFixedHeight(36)
        self.inp_buscar.setMinimumWidth(240)
        self.inp_buscar.textChanged.connect(self._refresh_all)
        filt.addWidget(self.inp_buscar)

        filt.addWidget(lbl("Año:"))
        self.cb_anio = QComboBox(); self.cb_anio.setFixedHeight(36)
        self.cb_anio.addItem("Todos")
        for a in db_.get_anios(): self.cb_anio.addItem(str(a))
        self.cb_anio.currentIndexChanged.connect(self._refresh_all)
        filt.addWidget(self.cb_anio)

        filt.addWidget(lbl("Obra:"))
        self.cb_obra = QComboBox(); self.cb_obra.setFixedHeight(36)
        self.cb_obra.addItem("Todas las obras")
        self._obra_map = {}
        for o in db_.get_obras():
            self.cb_obra.addItem(o["nombre"])
            self._obra_map[o["nombre"]] = o["id"]
        self.cb_obra.currentIndexChanged.connect(self._refresh_all)
        filt.addWidget(self.cb_obra)

        filt.addStretch()
        L.addLayout(filt)

        self.comp_row_widget = QWidget()
        comp_lay = QHBoxLayout(self.comp_row_widget); comp_lay.setContentsMargins(0,0,0,0)
        comp_lay.addWidget(lbl("Comparar años activos:"))
        self.chk_anios = {}
        for a in db_.get_anios():
            cb = QCheckBox(str(a))
            cb.setChecked(True)
            cb.stateChanged.connect(self._refresh_comparativo)
            comp_lay.addWidget(cb)
            self.chk_anios[a] = cb
        comp_lay.addStretch()
        L.addWidget(self.comp_row_widget)
        self.comp_row_widget.hide() 

        self.tabs = QTabWidget()
        L.addWidget(self.tabs)

        self.tab_anual = QWidget()
        tl1 = QVBoxLayout(self.tab_anual); tl1.setContentsMargins(8,8,8,8)
        self.h_anual = QVBoxLayout(); tl1.addLayout(self.h_anual); tl1.addStretch()
        self.tabs.addTab(self.tab_anual, "📈 Anual")

        self.tab_mensual = QWidget()
        tl2 = QVBoxLayout(self.tab_mensual); tl2.setContentsMargins(8,8,8,8)
        self.h_mensual = QVBoxLayout(); tl2.addLayout(self.h_mensual); tl2.addStretch()
        self.tabs.addTab(self.tab_mensual, "📅 Mesnuanl")

        self.tab_tri = QWidget()
        tl3 = QVBoxLayout(self.tab_tri); tl3.setContentsMargins(8,8,8,8)
        self.h_tri = QVBoxLayout(); tl3.addLayout(self.h_tri); tl3.addStretch()
        self.tabs.addTab(self.tab_tri, "🔢 Trimestral")

        self.tab_sem = QWidget()
        tl4 = QVBoxLayout(self.tab_sem); tl4.setContentsMargins(8,8,8,8)
        self.h_sem = QVBoxLayout(); tl4.addLayout(self.h_sem); tl4.addStretch()
        self.tabs.addTab(self.tab_sem, "📊 Semestral")

        self.tab_tipo = QWidget()
        tl5 = QVBoxLayout(self.tab_tipo); tl5.setContentsMargins(8,8,8,8)
        self.h_tipo = QVBoxLayout(); tl5.addLayout(self.h_tipo); tl5.addStretch()
        self.tabs.addTab(self.tab_tipo, "🔵 Por Tipo")

        self.tab_prov = QWidget()
        tl6 = QVBoxLayout(self.tab_prov); tl6.setContentsMargins(8,8,8,8)
        self.h_prov = QVBoxLayout(); tl6.addLayout(self.h_prov); tl6.addStretch()
        self.tabs.addTab(self.tab_prov, "🏭 Proveedores")

        self.tab_comp = QWidget()
        tl7 = QVBoxLayout(self.tab_comp); tl7.setContentsMargins(8,8,8,8)
        self.h_comp = QVBoxLayout(); tl7.addLayout(self.h_comp); tl7.addStretch()
        self.tabs.addTab(self.tab_comp, "🔀 Comparativo")

        self.tabs.currentChanged.connect(self._on_tab)
        self._refresh_all()

    def _get_filtros_actuales(self):
        filtros = {}
        busq = self.inp_buscar.text().strip()
        if busq: filtros["busqueda"] = busq
        t_anio = self.cb_anio.currentText()
        if t_anio and t_anio != "Todos": filtros["anio"] = int(t_anio)
        t_obra = self.cb_obra.currentText()
        if t_obra and t_obra != "Todas las obras":
            filtros["obra_id"] = self._obra_map.get(t_obra)
        return filtros

    def _refresh_all(self):
        for h in [self.h_anual, self.h_mensual, self.h_tri, self.h_sem, self.h_tipo, self.h_prov]:
            self._clear(h)
        self._on_tab(self.tabs.currentIndex())

    def _on_tab(self, idx):
        if idx == 6: self.comp_row_widget.show()
        else: self.comp_row_widget.hide()

        if idx == 0:   self._draw_anual()
        elif idx == 1: self._draw_mensual()
        elif idx == 2: self._draw_tri()
        elif idx == 3: self._draw_sem()
        elif idx == 4: self._draw_tipo()
        elif idx == 5: self._draw_prov()
        elif idx == 6: self._refresh_comparativo()

    def _add_chart(self, holder, canvas, h=360):
        self._clear(holder)
        canvas.setMinimumHeight(h)
        holder.addWidget(ChartCard(canvas, h))

    def _draw_anual(self):
        filtros = self._get_filtros_actuales()
        datos = db_.stats_anual(filtros)
        c = charts_mod.linea_anual(datos)
        self._add_chart(self.h_anual, c, 380)

    def _draw_mensual(self):
        filtros = self._get_filtros_actuales()
        datos = db_.stats_mensual(filtros)
        anio = filtros.get("anio")
        titulo = f"Costos Mensuales {anio}" if anio else "Costos Mensuales — Histórico"
        c = charts_mod.barras_mensual(datos, titulo)
        self._add_chart(self.h_mensual, c, 380)

    def _draw_tri(self):
        filtros = self._get_filtros_actuales()
        datos = db_.stats_trimestral(filtros)
        c = charts_mod.barras_trimestral(datos)
        self._add_chart(self.h_tri, c, 380)

    def _draw_sem(self):
        filtros = self._get_filtros_actuales()
        datos = db_.stats_semestral(filtros)
        c = charts_mod.barras_semestral(datos)
        self._add_chart(self.h_sem, c, 380)

    def _draw_tipo(self):
        filtros = self._get_filtros_actuales()
        datos = db_.stats_por_tipo(filtros)
        c = charts_mod.pastel_tipo(datos)
        self._add_chart(self.h_tipo, c, 400)

    def _draw_prov(self):
        filtros = self._get_filtros_actuales()
        datos = db_.stats_por_proveedor(filtros)
        c = charts_mod.barras_proveedores(datos)
        self._add_chart(self.h_prov, c, 400)

    def _refresh_comparativo(self):
        self._clear(self.h_comp)
        anios = [a for a, cb in self.chk_anios.items() if cb.isChecked()]
        if len(anios) < 2:
            self.h_comp.addWidget(lbl("Selecciona al menos 2 años para comparar", 11, color=C["text2"]))
            return
        filtros = self._get_filtros_actuales()
        datos = db_.stats_mensual(filtros)
        c = charts_mod.linea_multiAnio(datos, sorted(anios))
        c.setMinimumHeight(400)
        self.h_comp.addWidget(ChartCard(c, 400))

    def refresh(self):
        anios = db_.get_anios()
        for a in anios:
            if a not in self.chk_anios:
                cb = QCheckBox(str(a))
                cb.setChecked(True)
                cb.stateChanged.connect(self._refresh_comparativo)
                self.chk_anios[a] = cb
                
        self.cb_anio.blockSignals(True)
        anio_sel = self.cb_anio.currentText()
        self.cb_anio.clear()
        self.cb_anio.addItem("Todos")
        for a in anios: self.cb_anio.addItem(str(a))
        idx = self.cb_anio.findText(anio_sel)
        if idx >= 0: self.cb_anio.setCurrentIndex(idx)
        self.cb_anio.blockSignals(False)
        
        self.cb_obra.blockSignals(True)
        obra_sel = self.cb_obra.currentText()
        self.cb_obra.clear()
        self.cb_obra.addItem("Todas las obras")
        self._obra_map = {}
        for o in db_.get_obras():
            self.cb_obra.addItem(o["nombre"])
            self._obra_map[o["nombre"]] = o["id"]
        idx_o = self.cb_obra.findText(obra_sel)
        if idx_o >= 0: self.cb_obra.setCurrentIndex(idx_o)
        self.cb_obra.blockSignals(False)
        
        self._refresh_all()


# ══════════════════════════════════════════════════════════════
#  PÁGINA: CATÁLOGOS
# ══════════════════════════════════════════════════════════════
class CatalogosPage(PageBase):
    def __init__(self, usuario, parent=None):
        super().__init__(parent)
        self.usuario = usuario
        self._build()

    def _build(self):
        L = self.lay()
        L.addWidget(lbl("Catálogos del Sistema", 20, bold=True, color=C["accent"]))
        L.addWidget(lbl("Gestiona obras, equipos, proveedores y tipos de mantenimiento", 10, color=C["text2"]))

        tabs = QTabWidget()
        tabs.addTab(self._tab_obras(),       "🏗 Obras")
        tabs.addTab(self._tab_equipos(),     "⚙ Equipos")
        tabs.addTab(self._tab_proveedores(), "🏭 Proveedores")
        tabs.addTab(self._tab_tipos(),       "🔧 Tipos Mtto")
        L.addWidget(tabs)

    def _catalogo_tab(self, titulo, get_fn, tabla_cols, add_fn):
        tabla_name = titulo.lower()
        if titulo == "Obra": tabla_name = "obras"
        elif titulo == "Equipo": tabla_name = "equipos"
        elif titulo == "Proveedor": tabla_name = "proveedores"
        elif titulo == "Tipo": tabla_name = "tipos_mantenimiento"
        w = QWidget()
        lay = QVBoxLayout(w); lay.setContentsMargins(12,12,12,12); lay.setSpacing(10)

        row = QHBoxLayout(); row.setSpacing(8)
        inp = QLineEdit(); inp.setPlaceholderText(f"Nombre de {titulo.lower()}...")
        inp.setFixedHeight(36)
        inp_extra = None
        if titulo in ("Proveedor", "Tipo"):
            inp_extra = QLineEdit()
            inp_extra.setPlaceholderText("RUC" if titulo=="Proveedor" else "Clase (Servicios/Materiales)")
            inp_extra.setFixedHeight(36)
            row.addWidget(inp_extra)
        btn_add = QPushButton(f"➕ Agregar {titulo}")
        btn_add.setObjectName("btn_success"); btn_add.setFixedHeight(36)

        row.insertWidget(0, inp)
        row.addWidget(btn_add)
        lay.addLayout(row)

        tabla = QTableWidget(0, len(tabla_cols) + 1)
        tabla.setHorizontalHeaderLabels(tabla_cols + ["Acciones"])
        tabla.setAlternatingRowColors(True)
        tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        tabla.verticalHeader().setVisible(False)
        tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        lay.addWidget(tabla)

        def refresh():
            items = get_fn()
            tabla.setRowCount(0)
            for it in items:
                r = tabla.rowCount(); tabla.insertRow(r)
                keys = list(it.keys())
                for col, key in enumerate(tabla_cols):
                    k = keys[col] if col < len(keys) else key.lower()
                    v = it.get(k, it.get(key.lower(),""))
                    item = QTableWidgetItem(str(v) if v is not None else "")
                    item.setFlags(Qt.ItemFlag.ItemIsSelectable|Qt.ItemFlag.ItemIsEnabled)
                    tabla.setItem(r, col, item)

                cell = QWidget()
                cl = QHBoxLayout(cell); cl.setContentsMargins(4,2,4,2); cl.setSpacing(6)
                cl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                btn_e = QPushButton("✏"); btn_e.setObjectName("table_action"); btn_e.setFixedSize(30,26)
                btn_d = QPushButton("🗑"); btn_d.setObjectName("table_action"); btn_d.setFixedSize(30,26)

                item_id = it.get("id")
                item_name = it.get("nombre", "")
                item_ruc = it.get("ruc", "")
                item_clase = it.get("clase", "")
                
                def make_edit_handler(iid, iname, iruc, iclass, ttl):
                    def make_edit():
                        dlg = QDialog(self)
                        dlg.setWindowTitle(f"Editar {ttl}")
                        dlg.setMinimumWidth(400)
                        form = QFormLayout(dlg)
                        inp_name = QLineEdit(iname)
                        inp_name.setFixedHeight(36)
                        form.addRow("Nombre:", inp_name)
                        inp_extra = None
                        if ttl == "Proveedor":
                            inp_extra = QLineEdit(iruc)
                            inp_extra.setFixedHeight(36)
                            form.addRow("RUC:", inp_extra)
                        elif ttl == "Tipo":
                            inp_extra = QLineEdit(iclass)
                            inp_extra.setFixedHeight(36)
                            form.addRow("Clase:", inp_extra)
                        btns = QHBoxLayout(); btns.addStretch()
                        ok = QPushButton("Guardar"); ok.setObjectName("btn_primary")
                        cancel = QPushButton("Cancelar")
                        btns.addWidget(cancel); btns.addWidget(ok)
                        form.addRow(btns)

                        def do_save():
                            new_name = inp_name.text().strip()
                            new_extra = inp_extra.text().strip() if inp_extra else None
                            if not new_name:
                                msg_err(dlg, "Error", "El nombre no puede quedar vacío.")
                                return
                            try:
                                import db.database as dbw
                                dbw.update_catalogo(tabla_name, iid, new_name, new_extra, self.usuario.get("id"))
                                msg_ok(dlg, "Actualizado", f"{ttl} actualizado correctamente.")
                                dlg.accept()
                                refresh()
                            except Exception as e:
                                msg_err(dlg, "Error al guardar", f"No se pudo actualizar: {str(e)}")

                        ok.clicked.connect(do_save)
                        cancel.clicked.connect(dlg.reject)
                        dlg.exec()
                    return make_edit

                def make_delete_handler(iid, iname, ttl):
                    def do_delete():
                        dlg = ConfirmDialog(f"Eliminar {ttl}", f"¿Eliminar '{iname}'?\n\nEsta acción no se puede deshacer.", self)
                        if dlg.exec():
                            try:
                                import db.database as dbw
                                ok, msg = dbw.delete_catalogo(tabla_name, iid, self.usuario.get("id"))
                                if ok:
                                    msg_ok(self, "Eliminado", msg)
                                    refresh()
                                else:
                                    msg_err(self, "Error", msg)
                            except Exception as e:
                                msg_err(self, "Error al eliminar", f"No se pudo eliminar: {str(e)}")
                    return do_delete

                btn_e.clicked.connect(make_edit_handler(item_id, item_name, item_ruc, item_clase, titulo))
                btn_d.clicked.connect(make_delete_handler(item_id, item_name, titulo))
                cl.addWidget(btn_e); cl.addWidget(btn_d)
                tabla.setCellWidget(r, len(tabla_cols), cell)

        def do_add():
            nombre = inp.text().strip()
            if not nombre: return
            extra = inp_extra.text().strip() if inp_extra else None
            ok = add_fn(nombre, extra)
            if ok:
                inp.clear()
                if inp_extra: inp_extra.clear()
                refresh()
            else:
                msg_err(w, "Error", f"'{nombre}' ya existe en el catálogo.")

        btn_add.clicked.connect(do_add)
        refresh()
        return w

    def _tab_obras(self):
        return self._catalogo_tab(
            "Obra",
            lambda: [{"id":o["id"],"nombre":o["nombre"]} for o in db_.get_obras(False)],
            ["ID","Nombre"],
            lambda n, e: db_.add_catalogo("obras", n)
        )

    def _tab_equipos(self):
        return self._catalogo_tab(
            "Equipo",
            lambda: [{"id":e["id"],"nombre":e["nombre"]} for e in db_.get_equipos(False)],
            ["ID","Nombre"],
            lambda n, e: db_.add_catalogo("equipos", n)
        )

    def _tab_proveedores(self):
        return self._catalogo_tab(
            "Proveedor",
            lambda: [{"id":p["id"],"nombre":p["nombre"],"ruc":p.get("ruc","")} for p in db_.get_proveedores(False)],
            ["ID","Nombre","RUC"],
            lambda n, e: db_.add_catalogo("proveedores", n, e)
        )

    def _tab_tipos(self):
        return self._catalogo_tab(
            "Tipo",
            lambda: [{"id":t["id"],"nombre":t["nombre"],"clase":t["clase"]} for t in db_.get_tipos()],
            ["ID","Nombre","Clase"],
            lambda n, e: db_.add_catalogo("tipos_mantenimiento", n, e or "Servicios")
        )

    def refresh(self): pass


# ══════════════════════════════════════════════════════════════
#  PÁGINA: ADMINISTRACIÓN 
# ══════════════════════════════════════════════════════════════
class AdminPage(PageBase):
    def __init__(self, usuario, parent=None):
        super().__init__(parent)
        self.usuario = usuario
        self._build()

    def _build(self):
        header = self.lay()
        header.addWidget(lbl("Administración", 20, bold=True, color=C["accent"]))

        tabs = QTabWidget()
        tabs.addTab(self._tab_usuarios(), "👥 Usuarios")
        tabs.addTab(self._tab_actividad(),"📋 Log de Actividad")
        header.addWidget(tabs)

    def _tab_usuarios(self):
        w = QWidget()
        lay = QVBoxLayout(w); lay.setContentsMargins(14,14,14,14); lay.setSpacing(12)
        lay.addWidget(lbl("Gestión de Usuarios", 14, bold=True, color=C["accent"]))

        grp = QGroupBox("Crear nuevo usuario")
        grp.setStyleSheet(f"QGroupBox{{color:{C['accent']};border:1px solid {C['border']};border-radius:8px;margin-top:12px;padding:12px;}}")
        gl = QGridLayout(grp); gl.setSpacing(10)
        self.inp_u_user  = QLineEdit(); self.inp_u_user.setPlaceholderText("username")
        self.inp_u_nombre= QLineEdit(); self.inp_u_nombre.setPlaceholderText("Nombre completo")
        self.inp_u_pass  = QLineEdit(); self.inp_u_pass.setPlaceholderText("Contraseña")
        self.inp_u_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.cb_u_rol    = QComboBox(); self.cb_u_rol.addItems(["operador","supervisor","admin"])

        btn_crear = QPushButton("➕ Crear Usuario"); btn_crear.setObjectName("btn_success")
        btn_crear.clicked.connect(self._crear_usuario)
        self.lbl_u_err = lbl("", 10, color=C["red"])

        gl.addWidget(lbl("Usuario:"),        0,0); gl.addWidget(self.inp_u_user,  0,1)
        gl.addWidget(lbl("Nombre:"),         0,2); gl.addWidget(self.inp_u_nombre,0,3)
        gl.addWidget(lbl("Contraseña:"),     1,0); gl.addWidget(self.inp_u_pass,  1,1)
        gl.addWidget(lbl("Rol:"),            1,2); gl.addWidget(self.cb_u_rol,    1,3)
        gl.addWidget(self.lbl_u_err,         2,0,1,3)
        gl.addWidget(btn_crear,              2,3)
        lay.addWidget(grp)

        cols = ["ID","Usuario","Nombre","Rol","Activo","Creado","Último Acceso"]
        self.tabla_users = QTableWidget(0, len(cols))
        self.tabla_users.setHorizontalHeaderLabels(cols)
        self.tabla_users.setAlternatingRowColors(True)
        self.tabla_users.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla_users.verticalHeader().setVisible(False)
        self.tabla_users.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        lay.addWidget(self.tabla_users)
        self._refresh_users()
        return w

    def _crear_usuario(self):
        u = self.inp_u_user.text().strip()
        n = self.inp_u_nombre.text().strip()
        p = self.inp_u_pass.text()
        r = self.cb_u_rol.currentText()
        if not u or not n or not p:
            self.lbl_u_err.setText("Todos los campos son obligatorios"); return
        ok, msg = db_.crear_usuario(u, p, n, r)
        if ok:
            self.lbl_u_err.setStyleSheet(f"color:{C['green']};")
            self.lbl_u_err.setText("✔ Usuario creado correctamente")
            self.inp_u_user.clear(); self.inp_u_nombre.clear(); self.inp_u_pass.clear()
            self._refresh_users()
        else:
            self.lbl_u_err.setStyleSheet(f"color:{C['red']};")
            self.lbl_u_err.setText(f"⚠ {msg}")

    def _refresh_users(self):
        usuarios = db_.get_usuarios()
        self.tabla_users.setRowCount(0)
        for u in usuarios:
            r = self.tabla_users.rowCount(); self.tabla_users.insertRow(r)
            vals = [str(u["id"]), u["username"], u["nombre"], u["rol"],
                    "✔ Activo" if u["activo"] else "✘ Inactivo",
                    (u["created_at"] or "")[:10], (u["last_login"] or "—")[:16]]
            for col, val in enumerate(vals):
                item = QTableWidgetItem(val)
                item.setFlags(Qt.ItemFlag.ItemIsSelectable|Qt.ItemFlag.ItemIsEnabled)
                if col == 4:
                    item.setForeground(QColor(C["green"] if u["activo"] else C["red"]))
                self.tabla_users.setItem(r, col, item)

    def _tab_actividad(self):
        w = QWidget()
        lay = QVBoxLayout(w); lay.setContentsMargins(14,14,14,14); lay.setSpacing(10)
        lay.addWidget(lbl("Log de Actividad del Sistema", 14, bold=True, color=C["accent"]))
        cols = ["Fecha","Usuario","Acción","Detalle"]
        self.tabla_log = QTableWidget(0, len(cols))
        self.tabla_log.setHorizontalHeaderLabels(cols)
        self.tabla_log.setAlternatingRowColors(True)
        self.tabla_log.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla_log.verticalHeader().setVisible(False)
        self.tabla_log.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        lay.addWidget(self.tabla_log)
        self._refresh_log()
        return w

    def _refresh_log(self):
        logs = db_.get_actividad(200)
        self.tabla_log.setRowCount(0)
        for lg in logs:
            r = self.tabla_log.rowCount(); self.tabla_log.insertRow(r)
            vals = [lg["fecha"][:16], lg["usuario"] or "—", lg["accion"], lg["detalle"] or ""]
            for col, val in enumerate(vals):
                item = QTableWidgetItem(val)
                item.setFlags(Qt.ItemFlag.ItemIsSelectable|Qt.ItemFlag.ItemIsEnabled)
                self.tabla_log.setItem(r, col, item)

    def refresh(self):
        self._refresh_users()
        self._refresh_log()