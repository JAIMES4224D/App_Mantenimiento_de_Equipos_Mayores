"""Paleta de colores dinámicos y generador de stylesheet global."""

# ── PALETA MODO OSCURO (ORIGINAL) ──────────────────────────────────────────
C_DARK = dict(
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

# ── PALETA MODO CLARO (ARMONIZADA) ─────────────────────────────────────────
C_LIGHT = dict(
    bg      = "#F0F4F8",
    panel   = "#FFFFFF",
    sidebar = "#E1E8ED",
    card    = "#F8FAFC",
    accent  = "#0088CC",  
    accent2 = "#E65100",
    green   = "#16A34A",
    amber   = "#D97706",
    purple  = "#7C3AED",
    red     = "#DC2626",
    text    = "#1E293B",  
    text2   = "#64748B",
    border  = "#CBD5E1",
    input   = "#F1F5F9",
)


C = C_DARK.copy()


def obtener_stylesheet(colores):
    """Genera la hoja de estilos inyectando la paleta de colores seleccionada."""
    
    color_texto_primario = "#FFFFFF" if colores == C_LIGHT else "#000000"
    
    return f"""
    * {{ font-family: 'Segoe UI', 'DejaVu Sans', sans-serif; }}

    QMainWindow, QDialog, QWidget {{
        background: {colores['bg']};
        color: {colores['text']};
        font-size: 13px;
    }}

    /* ── Sidebar ── */
    QFrame#sidebar {{
        background: {colores['sidebar']};
        border-right: 1px solid {colores['border']};
    }}
    QPushButton#nav_btn {{
        background: transparent;
        color: {colores['text2']};
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
        border-left: 3px solid {colores['accent']};
        color: {colores['accent']};
    }}
    QPushButton#nav_btn[active="true"] {{
        background: rgba(0,200,255,0.12);
        border-left: 3px solid {colores['accent']};
        color: {colores['accent']};
        font-weight: bold;
    }}

    /* ── Botones generales ── */
    QPushButton {{
        background: {colores['card']};
        color: {colores['text']};
        border: 1px solid {colores['border']};
        border-radius: 7px;
        padding: 8px 18px;
        font-size: 12px;
        font-weight: 500;
    }}
    QPushButton:hover {{
        background: rgba(0,200,255,0.1);
        border: 1px solid {colores['accent']};
        color: {colores['accent']};
    }}
    QPushButton:pressed {{ background: {colores['accent']}; color: #000; }}
    
    QPushButton#btn_primary {{
        background: {colores['accent']};
        color: {color_texto_primario};
        font-weight: bold;
        border: none;
    }}
    QPushButton#btn_primary:hover {{ background: #33D6FF; color: #000; }}
    
    QPushButton#btn_danger {{
        background: {colores['red']}22;
        color: {colores['red']};
        border: 1px solid {colores['red']}55;
    }}
    QPushButton#btn_danger:hover {{ background: {colores['red']}44; }}
    
    QPushButton#btn_success {{
        background: {colores['green']}22;
        color: {colores['green']};
        border: 1px solid {colores['green']}55;
    }}
    QPushButton#btn_success:hover {{ background: {colores['green']}44; }}

    /* ── Botones de acción pequeños en tablas */
    QPushButton#table_action {{
        background: transparent;
        color: {colores['text']};
        border: 1px solid transparent;
        min-width: 28px;
        min-height: 24px;
        padding: 2px;
        border-radius: 4px;
    }}
    QPushButton#table_action:hover {{
        background: {colores['card']};
        border: 1px solid {colores['border']};
        color: {colores['accent']};
    }}

    /* ── Cards ── */
    QFrame#card {{
        background: {colores['card']};
        border: 1px solid {colores['border']};
        border-radius: 10px;
    }}
    QFrame#card_accent {{
        background: {colores['card']};
        border: 1px solid {colores['accent']}44;
        border-radius: 10px;
    }}

    /* ── Inputs ── */
    QLineEdit, QTextEdit, QPlainTextEdit {{
        background: {colores['input']};
        color: {colores['text']};
        border: 1px solid {colores['border']};
        border-radius: 6px;
        padding: 7px 12px;
        font-size: 13px;
        selection-background-color: {colores['accent']}55;
    }}
    QLineEdit:focus, QTextEdit:focus {{
        border: 1px solid {colores['accent']};
    }}
    QComboBox {{
        background: {colores['input']};
        color: {colores['text']};
        border: 1px solid {colores['border']};
        border-radius: 6px;
        padding: 7px 12px;
        font-size: 13px;
        min-width: 140px;
    }}
    QComboBox:focus {{ border: 1px solid {colores['accent']}; }}
    QComboBox::drop-down {{ border: none; width: 24px; }}
    QComboBox::down-arrow {{ width: 10px; height: 10px; }}
    QComboBox QAbstractItemView {{
        background: {colores['card']};
        color: {colores['text']};
        selection-background-color: {colores['accent']}44;
        selection-color: {colores['accent']};
        border: 1px solid {colores['border']};
    }}
    QDateEdit {{
        background: {colores['input']};
        color: {colores['text']};
        border: 1px solid {colores['border']};
        border-radius: 6px;
        padding: 7px 10px;
    }}
    QDateEdit:focus {{ border: 1px solid {colores['accent']}; }}
    QDoubleSpinBox, QSpinBox {{
        background: {colores['input']};
        color: {colores['text']};
        border: 1px solid {colores['border']};
        border-radius: 6px;
        padding: 7px 10px;
    }}
    QDoubleSpinBox:focus, QSpinBox:focus {{ border: 1px solid {colores['accent']}; }}

    /* ── Tabla ── */
    QTableWidget {{
        background: {colores['panel']};
        color: {colores['text']};
        gridline-color: {colores['border']};
        border: 1px solid {colores['border']};
        border-radius: 8px;
        font-size: 12px;
        alternate-background-color: {colores['sidebar']};
    }}
    QTableWidget::item {{ padding: 5px 8px; }}
    QTableWidget::item:selected {{
        background: {colores['accent']}25;
        color: {colores['accent']};
    }}
    QHeaderView::section {{
        background: {colores['sidebar']};
        color: {colores['accent']};
        border: none;
        border-bottom: 1px solid {colores['border']};
        padding: 7px 10px;
        font-weight: bold;
        font-size: 11px;
        text-transform: uppercase;
    }}

    /* ── Scrollbar ── */
    QScrollBar:vertical {{ background:{colores['bg']}; width:7px; border-radius:4px; }}
    QScrollBar::handle:vertical {{ background:{colores['border']}; border-radius:4px; min-height:24px; }}
    QScrollBar:horizontal {{ background:{colores['bg']}; height:7px; border-radius:4px; }}
    QScrollBar::handle:horizontal {{ background:{colores['border']}; border-radius:4px; }}

    /* ── Tabs ── */
    QTabWidget::pane {{
        border: 1px solid {colores['border']};
        background: {colores['panel']};
        border-radius: 8px;
    }}
    QTabBar::tab {{
        background: {colores['sidebar']};
        color: {colores['text2']};
        padding: 9px 22px;
        margin-right: 2px;
        border-top-left-radius: 7px;
        border-top-right-radius: 7px;
        font-size: 12px;
    }}
    QTabBar::tab:selected {{
        background: {colores['card']};
        color: {colores['accent']};
        font-weight: bold;
    }}

    /* ── GroupBox ── */
    QGroupBox {{
        color: {colores['accent']};
        border: 1px solid {colores['border']};
        border-radius: 8px;
        margin-top: 14px;
        padding: 12px 10px 10px 10px;
        font-weight: bold;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin; left: 14px; padding: 0 6px;
    }}

    /* ── Label ── */
    QLabel#title {{ color: {colores['accent']}; font-size: 20px; font-weight: bold; }}
    QLabel#subtitle {{ color: {colores['text2']}; font-size: 11px; }}
    QLabel#kpi_val {{ font-size: 24px; font-weight: bold; color: {colores['accent']}; }}
    QLabel#section {{ color: {colores['accent']}; font-size: 15px; font-weight: bold; }}

    /* ── Dialog ── */
    QDialog {{
        background: {colores['panel']};
        border: 1px solid {colores['border']};
        border-radius: 10px;
    }}

    /* ── MessageBox ── */
    QMessageBox {{ background: {colores['panel']}; }}
    QMessageBox QLabel {{ color: {colores['text']}; }}
    """

STYLESHEET = obtener_stylesheet(C)


MESES = {1:"Enero",2:"Febrero",3:"Marzo",4:"Abril",5:"Mayo",6:"Junio",
         7:"Julio",8:"Agosto",9:"Septiembre",10:"Octubre",11:"Noviembre",12:"Diciembre"}
MESES_CORTO = {1:"Ene",2:"Feb",3:"Mar",4:"Abr",5:"May",6:"Jun",
               7:"Jul",8:"Ago",9:"Sep",10:"Oct",11:"Nov",12:"Dic"}

PIE_COLORS  = ["#00C8FF","#FF6B35","#22C55E","#F59E0B","#A78BFA",
               "#FB7185","#34D399","#60A5FA","#FBBF24","#C084FC"]
LINE_COLORS = ["#00C8FF","#FF6B35","#22C55E","#F59E0B","#A78BFA","#FB7185"]