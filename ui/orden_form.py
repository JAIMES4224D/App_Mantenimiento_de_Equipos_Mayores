"""Formulario de ingreso / edición de Orden de Compra."""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QComboBox, QDoubleSpinBox,
    QPushButton, QTextEdit, QDateEdit, QFrame, QScrollArea, QWidget
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
from ui.theme import C
from ui.widgets import lbl, hline, msg_err
import db.database as db_
from datetime import datetime


class OrdenFormDialog(QDialog):
    def __init__(self, usuario, orden_data=None, parent=None):
        super().__init__(parent)
        self.usuario  = usuario
        self.edit_data = orden_data  # None = nueva, dict = edición
        is_edit = orden_data is not None
        self.setWindowTitle("Editar Orden de Compra" if is_edit else "Nueva Orden de Compra")
        self.setMinimumSize(760, 680)
        self.setStyleSheet(f"background:{C['panel']};")
        self._build()
        if is_edit:
            self._fill(orden_data)

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        # Título
        hdr = QFrame()
        hdr.setStyleSheet(f"background:{C['sidebar']}; border-bottom:1px solid {C['border']};")
        hdr.setFixedHeight(54)
        hl = QHBoxLayout(hdr)
        hl.setContentsMargins(24, 0, 24, 0)
        titulo_txt = "✏  Editar Orden" if self.edit_data else "➕  Nueva Orden de Compra"
        hl.addWidget(lbl(titulo_txt, 14, bold=True, color=C["accent"]))
        root.addWidget(hdr)

        # Scroll body
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea{border:none;}")
        body = QWidget()
        body.setStyleSheet(f"background:{C['panel']};")
        bl = QVBoxLayout(body)
        bl.setContentsMargins(28, 22, 28, 16)
        bl.setSpacing(18)

        # ── Sección 1: Identificación ─────────────────────────
        bl.addWidget(lbl("Identificación", 11, bold=True, color=C["text2"]))
        bl.addWidget(hline())
        g1 = QGridLayout(); g1.setSpacing(12)

        self.inp_nro   = QLineEdit(); self.inp_nro.setPlaceholderText("Ej: 4700099001")
        self.inp_fecha = QDateEdit(); self.inp_fecha.setCalendarPopup(True)
        self.inp_fecha.setDate(QDate.currentDate())
        self.inp_fecha.setDisplayFormat("dd/MM/yyyy")

        self.cb_obra   = QComboBox()
        self.cb_equipo = QComboBox()

        obras   = db_.get_obras()
        equipos = db_.get_equipos()
        self._obra_map   = {o["nombre"]: o["id"] for o in obras}
        self._equipo_map = {e["nombre"]: e["id"] for e in equipos}
        self.cb_obra.addItems(list(self._obra_map.keys()))
        self.cb_equipo.addItems(list(self._equipo_map.keys()))

        g1.addWidget(lbl("N° Orden *"),    0, 0); g1.addWidget(self.inp_nro,   0, 1)
        g1.addWidget(lbl("Fecha *"),       0, 2); g1.addWidget(self.inp_fecha, 0, 3)
        g1.addWidget(lbl("Obra *"),        1, 0); g1.addWidget(self.cb_obra,   1, 1)
        g1.addWidget(lbl("Equipo *"),      1, 2); g1.addWidget(self.cb_equipo, 1, 3)
        bl.addLayout(g1)

        # ── Sección 2: Mantenimiento ──────────────────────────
        bl.addSpacing(4)
        bl.addWidget(lbl("Tipo de Mantenimiento", 11, bold=True, color=C["text2"]))
        bl.addWidget(hline())
        g2 = QGridLayout(); g2.setSpacing(12)

        self.cb_tipo  = QComboBox()
        tipos = db_.get_tipos()
        self._tipo_map = {t["nombre"]: t["id"] for t in tipos}
        self.cb_tipo.addItems(list(self._tipo_map.keys()))

        self.cb_clase = QComboBox()
        self.cb_clase.addItems(["Servicios", "Materiales"])

        self.cb_estado = QComboBox()
        self.cb_estado.addItems(["Activo", "Cerrado", "Anulado"])

        self.cb_fact = QComboBox()
        self.cb_fact.addItems(["Pendiente", "Totalmente Facturado", "Facturado Parcial"])

        g2.addWidget(lbl("Tipo *"),             0, 0); g2.addWidget(self.cb_tipo,   0, 1)
        g2.addWidget(lbl("Clase"),              0, 2); g2.addWidget(self.cb_clase,  0, 3)
        g2.addWidget(lbl("Estado OC"),          1, 0); g2.addWidget(self.cb_estado, 1, 1)
        g2.addWidget(lbl("Estado Facturación"), 1, 2); g2.addWidget(self.cb_fact,   1, 3)
        bl.addLayout(g2)

        # ── Sección 3: Proveedor y Recurso ────────────────────
        bl.addSpacing(4)
        bl.addWidget(lbl("Proveedor y Descripción", 11, bold=True, color=C["text2"]))
        bl.addWidget(hline())
        g3 = QGridLayout(); g3.setSpacing(12)

        self.cb_prov = QComboBox()
        provs = db_.get_proveedores()
        self._prov_map = {p["nombre"]: p["id"] for p in provs}
        self.cb_prov.addItems(list(self._prov_map.keys()))

        self.inp_gestor = QLineEdit(); self.inp_gestor.setPlaceholderText("Nombre del gestor")
        self.inp_recurso = QLineEdit(); self.inp_recurso.setPlaceholderText("Descripción del trabajo o material")
        self.inp_obs = QTextEdit(); self.inp_obs.setPlaceholderText("Observaciones adicionales...")
        self.inp_obs.setFixedHeight(68)

        g3.addWidget(lbl("Proveedor *"),    0, 0); g3.addWidget(self.cb_prov,      0, 1, 1, 3)
        g3.addWidget(lbl("Gestor Compra"),  1, 0); g3.addWidget(self.inp_gestor,   1, 1, 1, 3)
        g3.addWidget(lbl("Recurso / Desc.*"),2,0); g3.addWidget(self.inp_recurso,  2, 1, 1, 3)
        g3.addWidget(lbl("Observación"),    3, 0); g3.addWidget(self.inp_obs,      3, 1, 1, 3)
        bl.addLayout(g3)

        # ── Sección 4: Valores ────────────────────────────────
        bl.addSpacing(4)
        bl.addWidget(lbl("Valores Económicos", 11, bold=True, color=C["text2"]))
        bl.addWidget(hline())
        g4 = QGridLayout(); g4.setSpacing(12)

        self.cb_moneda = QComboBox(); self.cb_moneda.addItems(["USD", "PEN"])
        self.cb_unidad = QComboBox(); self.cb_unidad.addItems(["glb","und","m","m²","m³","kg","día","hr","mes"])
        self.cb_pago   = QComboBox(); self.cb_pago.addItems(["Crédito 30d","Crédito 45d","Crédito 60d","Contado","Adelanto 50%"])

        def spin(mn=0, mx=9_999_999, dec=2, prefix=""):
            s = QDoubleSpinBox(); s.setRange(mn, mx); s.setDecimals(dec)
            s.setSingleStep(100); s.setGroupSeparatorShown(True)
            if prefix: s.setPrefix(prefix)
            return s

        self.sp_cant   = spin(0.001, 9999, 3); self.sp_cant.setValue(1)
        self.sp_precio = spin(prefix="$ "); self.sp_precio.setValue(0)
        self.sp_dcto   = spin(prefix="$ ")
        self.lbl_igv   = lbl("IGV (18%): $ 0.00", 10, color=C["text2"])
        self.lbl_total = lbl("TOTAL: $ 0.00", 13, bold=True, color=C["accent"])

        self.sp_precio.valueChanged.connect(self._calc)
        self.sp_cant.valueChanged.connect(self._calc)
        self.sp_dcto.valueChanged.connect(self._calc)

        g4.addWidget(lbl("Moneda"),         0,0); g4.addWidget(self.cb_moneda,  0,1)
        g4.addWidget(lbl("Unidad"),         0,2); g4.addWidget(self.cb_unidad,  0,3)
        g4.addWidget(lbl("Forma de Pago"),  0,4); g4.addWidget(self.cb_pago,    0,5)
        g4.addWidget(lbl("Cantidad *"),     1,0); g4.addWidget(self.sp_cant,    1,1)
        g4.addWidget(lbl("Precio s/IGV *"), 1,2); g4.addWidget(self.sp_precio,  1,3)
        g4.addWidget(lbl("Descuento"),      1,4); g4.addWidget(self.sp_dcto,    1,5)
        g4.addWidget(self.lbl_igv,          2,0,1,3)
        g4.addWidget(self.lbl_total,        2,3,1,3)
        bl.addLayout(g4)

        scroll.setWidget(body)
        root.addWidget(scroll, 1)

        # Footer botones
        footer = QFrame()
        footer.setStyleSheet(f"background:{C['sidebar']};border-top:1px solid {C['border']};")
        footer.setFixedHeight(58)
        fl = QHBoxLayout(footer)
        fl.setContentsMargins(24, 0, 24, 0)

        self.lbl_footer_err = lbl("", 10, color=C["red"])
        btn_cancel = QPushButton("Cancelar"); btn_cancel.clicked.connect(self.reject)
        self.btn_save = QPushButton("  Guardar Orden"); self.btn_save.setObjectName("btn_primary")
        self.btn_save.setFixedWidth(180); self.btn_save.clicked.connect(self._save)

        fl.addWidget(self.lbl_footer_err)
        fl.addStretch()
        fl.addWidget(btn_cancel); fl.addSpacing(10); fl.addWidget(self.btn_save)
        root.addWidget(footer)

    def _calc(self):
        precio  = self.sp_precio.value()
        cant    = self.sp_cant.value()
        dcto    = self.sp_dcto.value()
        parcial = round(precio * cant, 2)
        igv     = round(parcial * 0.18, 2)
        total   = round(parcial + igv - dcto, 2)
        self.lbl_igv.setText(f"IGV (18%): ${igv:,.2f}   |   Parcial: ${parcial:,.2f}")
        self.lbl_total.setText(f"TOTAL: ${total:,.2f}")

    def _fill(self, d):
        self.inp_nro.setText(d.get("nro_orden", ""))
        fecha = d.get("fecha", "")
        if fecha:
            dt = QDate.fromString(fecha[:10], "yyyy-MM-dd")
            self.inp_fecha.setDate(dt)
        # Obra
        obra_n = d.get("obra", "")
        idx = self.cb_obra.findText(obra_n)
        if idx >= 0: self.cb_obra.setCurrentIndex(idx)
        # Equipo
        eq_n = d.get("equipo", "")
        idx = self.cb_equipo.findText(eq_n)
        if idx >= 0: self.cb_equipo.setCurrentIndex(idx)
        # Tipo
        tipo_n = d.get("tipo", "")
        idx = self.cb_tipo.findText(tipo_n)
        if idx >= 0: self.cb_tipo.setCurrentIndex(idx)
        # Clase
        idx = self.cb_clase.findText(d.get("clase", ""))
        if idx >= 0: self.cb_clase.setCurrentIndex(idx)
        # Estado
        idx = self.cb_estado.findText(d.get("estado", ""))
        if idx >= 0: self.cb_estado.setCurrentIndex(idx)
        # Fact
        idx = self.cb_fact.findText(d.get("estado_facturacion", ""))
        if idx >= 0: self.cb_fact.setCurrentIndex(idx)
        # Proveedor
        prov_n = d.get("proveedor", "")
        idx = self.cb_prov.findText(prov_n)
        if idx >= 0: self.cb_prov.setCurrentIndex(idx)

        self.inp_gestor.setText(d.get("gestor_compra", "") or "")
        self.inp_recurso.setText(d.get("recurso", "") or "")
        self.inp_obs.setPlainText(d.get("observacion", "") or "")
        idx = self.cb_moneda.findText(d.get("moneda", "USD"))
        if idx >= 0: self.cb_moneda.setCurrentIndex(idx)
        idx = self.cb_unidad.findText(d.get("unidad", "glb"))
        if idx >= 0: self.cb_unidad.setCurrentIndex(idx)
        self.sp_cant.setValue(float(d.get("cantidad", 1) or 1))
        self.sp_precio.setValue(float(d.get("precio_sin_igv", 0) or 0))
        self.sp_dcto.setValue(float(d.get("dcto_total", 0) or 0))
        self._calc()

    def _save(self):
        nro     = self.inp_nro.text().strip()
        recurso = self.inp_recurso.text().strip()
        if not nro:
            self.lbl_footer_err.setText("⚠ El N° de Orden es obligatorio"); return
        if not recurso:
            self.lbl_footer_err.setText("⚠ El campo Recurso/Descripción es obligatorio"); return

        fecha = self.inp_fecha.date().toString("yyyy-MM-dd")
        data = {
            "nro_orden":          nro,
            "fecha":              fecha,
            "obra_id":            self._obra_map.get(self.cb_obra.currentText()),
            "equipo_id":          self._equipo_map.get(self.cb_equipo.currentText()),
            "tipo_id":            self._tipo_map.get(self.cb_tipo.currentText()),
            "proveedor_id":       self._prov_map.get(self.cb_prov.currentText()),
            "clase":              self.cb_clase.currentText(),
            "estado":             self.cb_estado.currentText(),
            "estado_facturacion": self.cb_fact.currentText(),
            "moneda":             self.cb_moneda.currentText(),
            "unidad":             self.cb_unidad.currentText(),
            "forma_pago":         self.cb_pago.currentText(),
            "recurso":            recurso,
            "observacion":        self.inp_obs.toPlainText().strip(),
            "gestor_compra":      self.inp_gestor.text().strip(),
            "cantidad":           self.sp_cant.value(),
            "precio_sin_igv":     self.sp_precio.value(),
            "dcto_total":         self.sp_dcto.value(),
        }
        try:
            if self.edit_data:
                db_.actualizar_orden(self.edit_data["id"], data, self.usuario["id"])
            else:
                db_.insertar_orden(data, self.usuario["id"])
            self.accept()
        except Exception as e:
            self.lbl_footer_err.setText(f"⚠ Error: {e}")
