"""Paleta de colores y stylesheet global."""

C = dict(
    bg      = "#0D1B2A",
    panel   = "#132032",
    sidebar = "#0A1520",
    card    = "#162840",
    accent  = "#00C8FF",
    accent2 = "#FF6B35",
    green   = "#22C55E",
    amber   = "#F59E0B",
    purple  = "#A78BFA",
    red     = "#EF4444",
    text    = "#D0E4F4",
    text2   = "#5A7A9A",
    border  = "#1C3550",
    input   = "#0F2035",
)

STYLESHEET = f"""
* {{ font-family: 'Segoe UI', 'DejaVu Sans', sans-serif; }}

QMainWindow, QDialog, QWidget {{
    background: {C['bg']};
    color: {C['text']};
    font-size: 13px;
}}

/* ── Sidebar ── */
QFrame#sidebar {{
    background: {C['sidebar']};
    border-right: 1px solid {C['border']};
}}
QPushButton#nav_btn {{
    background: transparent;
    color: {C['text2']};
    border: none;
    border-left: 3px solid transparent;
    border-radius: 0;
    text-align: left;
    padding: 13px 22px;
    font-size: 13px;
    font-weight: 500;
}}
QPushButton#nav_btn:hover {{
    background: rgba(0,200,255,0.07);
    border-left: 3px solid {C['accent']};
    color: {C['accent']};
}}
QPushButton#nav_btn[active="true"] {{
    background: rgba(0,200,255,0.12);
    border-left: 3px solid {C['accent']};
    color: {C['accent']};
    font-weight: bold;
}}

/* ── Botones generales ── */
QPushButton {{
    background: {C['card']};
    color: {C['text']};
    border: 1px solid {C['border']};
    border-radius: 7px;
    padding: 8px 18px;
    font-size: 12px;
    font-weight: 500;
}}
QPushButton:hover {{
    background: rgba(0,200,255,0.1);
    border: 1px solid {C['accent']};
    color: {C['accent']};
}}
QPushButton:pressed {{ background: {C['accent']}; color: #000; }}
QPushButton#btn_primary {{
    background: {C['accent']};
    color: #000;
    font-weight: bold;
    border: none;
}}
QPushButton#btn_primary:hover {{ background: #33D6FF; color: #000; }}
QPushButton#btn_danger {{
    background: {C['red']}22;
    color: {C['red']};
    border: 1px solid {C['red']}55;
}}
QPushButton#btn_danger:hover {{ background: {C['red']}44; }}
QPushButton#btn_success {{
    background: {C['green']}22;
    color: {C['green']};
    border: 1px solid {C['green']}55;
}}
QPushButton#btn_success:hover {{ background: {C['green']}44; }}

/* ── Botones de acción pequeños en tablas */
QPushButton#table_action {{
    background: transparent;
    color: {C['text']};
    border: 1px solid transparent;
    min-width: 28px;
    min-height: 24px;
    padding: 2px;
    border-radius: 4px;
}}
QPushButton#table_action:hover {{
    background: {C['card']};
    border: 1px solid {C['border']};
    color: {C['accent']};
}}

/* ── Cards ── */
QFrame#card {{
    background: {C['card']};
    border: 1px solid {C['border']};
    border-radius: 10px;
}}
QFrame#card_accent {{
    background: {C['card']};
    border: 1px solid {C['accent']}44;
    border-radius: 10px;
}}

/* ── Inputs ── */
QLineEdit, QTextEdit, QPlainTextEdit {{
    background: {C['input']};
    color: {C['text']};
    border: 1px solid {C['border']};
    border-radius: 6px;
    padding: 7px 12px;
    font-size: 13px;
    selection-background-color: {C['accent']}55;
}}
QLineEdit:focus, QTextEdit:focus {{
    border: 1px solid {C['accent']};
}}
QComboBox {{
    background: {C['input']};
    color: {C['text']};
    border: 1px solid {C['border']};
    border-radius: 6px;
    padding: 7px 12px;
    font-size: 13px;
    min-width: 140px;
}}
QComboBox:focus {{ border: 1px solid {C['accent']}; }}
QComboBox::drop-down {{ border: none; width: 24px; }}
QComboBox::down-arrow {{ width: 10px; height: 10px; }}
QComboBox QAbstractItemView {{
    background: {C['card']};
    color: {C['text']};
    selection-background-color: {C['accent']}44;
    selection-color: {C['accent']};
    border: 1px solid {C['border']};
}}
QDateEdit {{
    background: {C['input']};
    color: {C['text']};
    border: 1px solid {C['border']};
    border-radius: 6px;
    padding: 7px 10px;
}}
QDateEdit:focus {{ border: 1px solid {C['accent']}; }}
QDoubleSpinBox, QSpinBox {{
    background: {C['input']};
    color: {C['text']};
    border: 1px solid {C['border']};
    border-radius: 6px;
    padding: 7px 10px;
}}
QDoubleSpinBox:focus, QSpinBox:focus {{ border: 1px solid {C['accent']}; }}

/* ── Tabla ── */
QTableWidget {{
    background: {C['panel']};
    color: {C['text']};
    gridline-color: {C['border']};
    border: 1px solid {C['border']};
    border-radius: 8px;
    font-size: 12px;
    alternate-background-color: {C['sidebar']};
}}
QTableWidget::item {{ padding: 5px 8px; }}
QTableWidget::item:selected {{
    background: {C['accent']}25;
    color: {C['accent']};
}}
QHeaderView::section {{
    background: {C['sidebar']};
    color: {C['accent']};
    border: none;
    border-bottom: 1px solid {C['border']};
    padding: 7px 10px;
    font-weight: bold;
    font-size: 11px;
    text-transform: uppercase;
}}

/* ── Scrollbar ── */
QScrollBar:vertical {{ background:{C['bg']}; width:7px; border-radius:4px; }}
QScrollBar::handle:vertical {{ background:{C['border']}; border-radius:4px; min-height:24px; }}
QScrollBar:horizontal {{ background:{C['bg']}; height:7px; border-radius:4px; }}
QScrollBar::handle:horizontal {{ background:{C['border']}; border-radius:4px; }}

/* ── Tabs ── */
QTabWidget::pane {{
    border: 1px solid {C['border']};
    background: {C['panel']};
    border-radius: 8px;
}}
QTabBar::tab {{
    background: {C['sidebar']};
    color: {C['text2']};
    padding: 9px 22px;
    margin-right: 2px;
    border-top-left-radius: 7px;
    border-top-right-radius: 7px;
    font-size: 12px;
}}
QTabBar::tab:selected {{
    background: {C['card']};
    color: {C['accent']};
    font-weight: bold;
}}

/* ── GroupBox ── */
QGroupBox {{
    color: {C['accent']};
    border: 1px solid {C['border']};
    border-radius: 8px;
    margin-top: 14px;
    padding: 12px 10px 10px 10px;
    font-weight: bold;
}}
QGroupBox::title {{
    subcontrol-origin: margin; left: 14px; padding: 0 6px;
}}

/* ── Label ── */
QLabel#title {{ color: {C['accent']}; font-size: 20px; font-weight: bold; }}
QLabel#subtitle {{ color: {C['text2']}; font-size: 11px; }}
QLabel#kpi_val {{ font-size: 24px; font-weight: bold; color: {C['accent']}; }}
QLabel#section {{ color: {C['accent']}; font-size: 15px; font-weight: bold; }}

/* ── Dialog ── */
QDialog {{
    background: {C['panel']};
    border: 1px solid {C['border']};
    border-radius: 10px;
}}

/* ── MessageBox ── */
QMessageBox {{ background: {C['panel']}; }}
QMessageBox QLabel {{ color: {C['text']}; }}
"""

MESES = {1:"Enero",2:"Febrero",3:"Marzo",4:"Abril",5:"Mayo",6:"Junio",
         7:"Julio",8:"Agosto",9:"Septiembre",10:"Octubre",11:"Noviembre",12:"Diciembre"}
MESES_CORTO = {1:"Ene",2:"Feb",3:"Mar",4:"Abr",5:"May",6:"Jun",
               7:"Jul",8:"Ago",9:"Sep",10:"Oct",11:"Nov",12:"Dic"}

PIE_COLORS  = ["#00C8FF","#FF6B35","#22C55E","#F59E0B","#A78BFA",
               "#FB7185","#34D399","#60A5FA","#FBBF24","#C084FC"]
LINE_COLORS = ["#00C8FF","#FF6B35","#22C55E","#F59E0B","#A78BFA","#FB7185"]