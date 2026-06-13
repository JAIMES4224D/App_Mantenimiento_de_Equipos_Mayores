"""Gráficos matplotlib embebidos en PyQt6."""
import matplotlib
matplotlib.use("QtAgg")
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
import numpy as np
from ui.theme import C, PIE_COLORS, LINE_COLORS, MESES_CORTO

BG   = C["bg"]
PAN  = C["card"]
GRID = C["border"]
TXT  = C["text"]
TXT2 = C["text2"]
ACC  = C["accent"]
ACC2 = C["accent2"]


def _fig(w=10, h=4.6):
    fig = Figure(figsize=(w, h), facecolor=BG, tight_layout=True)
    return fig

def _ax(fig, title="", xlabel="", ylabel=""):
    ax = fig.add_subplot(111)
    ax.set_facecolor(PAN)
    ax.tick_params(colors=TXT, labelsize=9)
    for s in ax.spines.values():
        s.set_edgecolor(GRID)
    ax.grid(True, color=GRID, lw=0.5, alpha=0.6, zorder=0)
    if title:  ax.set_title(title,  color=ACC,  fontsize=12, fontweight="bold", pad=10)
    if xlabel: ax.set_xlabel(xlabel, color=TXT2, fontsize=9)
    if ylabel: ax.set_ylabel(ylabel, color=TXT2, fontsize=9)
    return ax

def _canvas(fig): return FigureCanvas(fig)

def _fmt(v):
    if v >= 1_000_000: return f"${v/1_000_000:.1f}M"
    if v >= 1_000:     return f"${v/1_000:.0f}K"
    return f"${v:.0f}"


# ══ 1. LÍNEA ANUAL ═══════════════════════════════════════════
def linea_anual(datos):
    """datos: [{'anio':int,'total':float}]"""
    fig = _fig(10, 4.4)
    ax  = _ax(fig, "Evolución Anual de Costos de Mantenimiento", "Año", "Costo (USD)")
    if not datos:
        ax.text(0.5, 0.5, "Sin datos", transform=ax.transAxes,
                ha="center", va="center", color=TXT2, fontsize=13)
        return _canvas(fig)
    x = [d["anio"] for d in datos]
    y = [d["total"] for d in datos]
    ax.fill_between(x, y, alpha=0.13, color=ACC)
    ax.plot(x, y, color=ACC, lw=2.4, marker="o", ms=7,
            markerfacecolor=ACC2, markeredgecolor="white", mew=1.5, zorder=5)
    for xi, yi in zip(x, y):
        ax.annotate(_fmt(yi), (xi, yi), textcoords="offset points",
                    xytext=(0, 10), ha="center", fontsize=8, color=TXT)
    ax.set_xticks(x)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: _fmt(v)))
    return _canvas(fig)


# ══ 2. BARRAS MENSUALES ══════════════════════════════════════
def barras_mensual(datos, titulo="Costos Mensuales"):
    """datos: [{'mes':int,'total':float,'anio':int}]"""
    fig = _fig(11, 4.4)
    ax  = _ax(fig, titulo, "", "Costo (USD)")
    if not datos:
        ax.text(0.5, 0.5, "Sin datos", transform=ax.transAxes, ha="center", va="center", color=TXT2, fontsize=13)
        return _canvas(fig)
    labels = [MESES_CORTO.get(d["mes"], d["mes"]) for d in datos]
    y = [d["total"] for d in datos]
    cols = [ACC if i%2==0 else ACC2 for i in range(len(y))]
    bars = ax.bar(range(len(y)), y, color=cols, width=0.68,
                  zorder=3, edgecolor=BG, lw=0.4)
    mx = max(y) if y else 1
    for bar, yi in zip(bars, y):
        ax.text(bar.get_x()+bar.get_width()/2, yi+mx*0.012,
                _fmt(yi), ha="center", va="bottom",
                fontsize=7.5, color=TXT, rotation=35)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, fontsize=9)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: _fmt(v)))
    return _canvas(fig)


# ══ 3. PASTEL TIPO ═══════════════════════════════════════════
# ══ 3. PASTEL TIPO ═══════════════════════════════════════════
def pastel_tipo(datos, titulo="Distribución por Tipo de Mantenimiento"):
    """datos: [{'tipo':str,'total':float,'num':int}]"""
    fig = _fig(9.5, 5)
    fig.patch.set_facecolor(BG)
    ax = fig.add_subplot(111)
    ax.set_facecolor(BG)
    # Corrección: Se cambió title=titulo por label=titulo
    ax.set_title(label=titulo, color=ACC, fontsize=12, fontweight="bold", pad=14)
    if not datos:
        ax.text(0.5, 0.5, "Sin datos", transform=ax.transAxes, ha="center", va="center", color=TXT2)
        return _canvas(fig)
    tipos  = [d["tipo"] or "Sin tipo" for d in datos]
    totals = [d["total"] for d in datos]
    cols   = [PIE_COLORS[i % len(PIE_COLORS)] for i in range(len(tipos))]
    explode= [0.04 if i==0 else 0 for i in range(len(tipos))]
    wedges, _, autotexts = ax.pie(
        totals, labels=None, autopct="%1.1f%%", colors=cols,
        explode=explode, startangle=130, pctdistance=0.76,
        wedgeprops=dict(edgecolor=BG, lw=1.4)
    )
    for at in autotexts:
        at.set_color("white")
        at.set_fontsize(9)
        at.set_fontweight("bold")
    legend_labels = [f"{t}  ({_fmt(c)})" for t, c in zip(tipos, totals)]
    ax.legend(wedges, legend_labels, loc="center left",
              bbox_to_anchor=(1, 0.5), fontsize=8.5,
              framealpha=0, labelcolor=TXT)
    return _canvas(fig)


# ══ 4. TRIMESTRAL ════════════════════════════════════════════
def barras_trimestral(datos):
    """datos: [{'anio':int,'trimestre':int,'total':float}]"""
    fig = _fig(10, 4.4)
    ax  = _ax(fig, "Costos Trimestrales", "", "Costo (USD)")
    if not datos:
        ax.text(0.5, 0.5, "Sin datos", transform=ax.transAxes, ha="center", va="center", color=TXT2)
        return _canvas(fig)
    labels = [f"Q{d['trimestre']}  {d['anio']}" for d in datos]
    y      = [d["total"] for d in datos]
    qcols  = ["#00C8FF", "#22C55E", "#F59E0B", "#FB7185"]
    cols   = [qcols[(d["trimestre"]-1)%4] for d in datos]
    bars = ax.bar(range(len(y)), y, color=cols, width=0.65,
                  zorder=3, edgecolor=BG, lw=0.4)
    mx = max(y) if y else 1
    for bar, yi in zip(bars, y):
        ax.text(bar.get_x()+bar.get_width()/2, yi+mx*0.012,
                _fmt(yi), ha="center", va="bottom", fontsize=8.5,
                color=TXT, fontweight="bold")
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, fontsize=8.5, rotation=30, ha="right")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: _fmt(v)))
    patches = [mpatches.Patch(fc=qcols[i], label=f"Q{i+1}") for i in range(4)]
    ax.legend(handles=patches, fontsize=9, framealpha=0,
              labelcolor=TXT, loc="upper right")
    return _canvas(fig)


# ══ 5. SEMESTRAL ═════════════════════════════════════════════
def barras_semestral(datos):
    fig = _fig(9, 4.4)
    ax  = _ax(fig, "Costos Semestrales", "", "Costo (USD)")
    if not datos:
        ax.text(0.5, 0.5, "Sin datos", transform=ax.transAxes, ha="center", va="center", color=TXT2)
        return _canvas(fig)
    labels = [f"S{d['semestre']}  {d['anio']}" for d in datos]
    y      = [d["total"] for d in datos]
    cols   = [ACC if d["semestre"]==1 else ACC2 for d in datos]
    bars = ax.bar(range(len(y)), y, color=cols, width=0.62,
                  zorder=3, edgecolor=BG, lw=0.4)
    mx = max(y) if y else 1
    for bar, yi in zip(bars, y):
        ax.text(bar.get_x()+bar.get_width()/2, yi+mx*0.012,
                _fmt(yi), ha="center", va="bottom",
                fontsize=9, color=TXT, fontweight="bold")
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, fontsize=9)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: _fmt(v)))
    patches = [mpatches.Patch(fc=ACC, label="1er Semestre"),
               mpatches.Patch(fc=ACC2, label="2do Semestre")]
    ax.legend(handles=patches, fontsize=9, framealpha=0, labelcolor=TXT)
    return _canvas(fig)


# ══ 6. COMPARATIVO MULTI-AÑO ════════════════════════════════
def linea_multiAnio(datos_mensuales, anios):
    """datos_mensuales: [{'anio','mes','total'}]"""
    fig = _fig(11, 4.6)
    ax  = _ax(fig, "Comparativo Mensual por Año", "Mes", "Costo (USD)")
    meses = list(range(1, 13))
    mlabels = [MESES_CORTO[m] for m in meses]
    for i, anio in enumerate(anios):
        sub = {d["mes"]: d["total"] for d in datos_mensuales if d["anio"]==anio}
        y = [sub.get(m, 0) for m in meses]
        col = LINE_COLORS[i % len(LINE_COLORS)]
        ax.plot(meses, y, color=col, lw=2, marker="o", ms=5,
                label=str(anio), zorder=5)
        ax.fill_between(meses, y, alpha=0.04, color=col)
    ax.set_xticks(meses)
    ax.set_xticklabels(mlabels, fontsize=9)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: _fmt(v)))
    ax.legend(fontsize=9, framealpha=0.2, facecolor=PAN,
              labelcolor=TXT, loc="upper left")
    return _canvas(fig)


# ══ 7. PROVEEDORES HORIZONTAL ════════════════════════════════
def barras_proveedores(datos):
    fig = _fig(10, 4.8)
    ax  = _ax(fig, "Top Proveedores por Costo Total", "Costo (USD)", "")
    ax.grid(axis="x", color=GRID, lw=0.5, alpha=0.6)
    ax.grid(axis="y", visible=False)
    if not datos:
        ax.text(0.5, 0.5, "Sin datos", transform=ax.transAxes, ha="center", va="center", color=TXT2)
        return _canvas(fig)
    labels = [p["proveedor"][:32] if p["proveedor"] else "?" for p in datos]
    y      = [p["total"] for p in datos]
    n      = len(y)
    import matplotlib.pyplot as plt
    cmap   = plt.get_cmap("cool")
    cols   = [cmap(i/max(n-1,1)) for i in range(n)]
    bars   = ax.barh(range(n), y, color=cols, height=0.62,
                     zorder=3, edgecolor=BG)
    mx = max(y) if y else 1
    for bar, yi in zip(bars, y):
        ax.text(yi+mx*0.01, bar.get_y()+bar.get_height()/2,
                _fmt(yi), va="center", fontsize=9, color=TXT)
    ax.set_yticks(range(n))
    ax.set_yticklabels(labels, fontsize=9)
    ax.invert_yaxis()
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: _fmt(v)))
    return _canvas(fig)


# ══ 8. SEMANAL (estimado) ════════════════════════════════════
def barras_semanal(datos, titulo="Distribución Semanal"):
    fig = _fig(8, 4)
    ax  = _ax(fig, titulo, "Semana", "Costo (USD)")
    if not datos:
        ax.text(0.5, 0.5, "Sin datos", transform=ax.transAxes, ha="center", va="center", color=TXT2)
        return _canvas(fig)
    labels = [d["semana"] for d in datos]
    y      = [d["total"]  for d in datos]
    cols   = [ACC, ACC2, C["green"], C["amber"]]
    bars   = ax.bar(range(len(y)), y, color=cols[:len(y)],
                    width=0.58, zorder=3, edgecolor=BG)
    mx = max(y) if y else 1
    for bar, yi in zip(bars, y):
        ax.text(bar.get_x()+bar.get_width()/2, yi+mx*0.02,
                _fmt(yi), ha="center", va="bottom",
                fontsize=10, color=TXT, fontweight="bold")
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, fontsize=10)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: _fmt(v)))
    return _canvas(fig)