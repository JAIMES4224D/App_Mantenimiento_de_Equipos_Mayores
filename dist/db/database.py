"""
Base de datos local SQLite.
Se crea automáticamente en la primera ejecución.
"""
import sqlite3
import os
import bcrypt
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mantenimiento.db")


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_conn()
    c = conn.cursor()

    # ── Usuarios ────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            username    TEXT UNIQUE NOT NULL,
            password    TEXT NOT NULL,
            nombre      TEXT NOT NULL,
            rol         TEXT NOT NULL DEFAULT 'operador',
            activo      INTEGER NOT NULL DEFAULT 1,
            created_at  TEXT NOT NULL DEFAULT (datetime('now','localtime')),
            last_login  TEXT
        )
    """)

    # ── Catálogos ────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS obras (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre  TEXT UNIQUE NOT NULL,
            activa  INTEGER NOT NULL DEFAULT 1
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS equipos (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre  TEXT UNIQUE NOT NULL,
            activo  INTEGER NOT NULL DEFAULT 1
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS proveedores (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre  TEXT UNIQUE NOT NULL,
            ruc     TEXT,
            activo  INTEGER NOT NULL DEFAULT 1
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS tipos_mantenimiento (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre  TEXT UNIQUE NOT NULL,
            clase   TEXT NOT NULL DEFAULT 'Servicios'
        )
    """)

    # ── Órdenes de compra ────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS ordenes (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            nro_orden           TEXT NOT NULL,
            obra_id             INTEGER REFERENCES obras(id),
            equipo_id           INTEGER REFERENCES equipos(id),
            proveedor_id        INTEGER REFERENCES proveedores(id),
            tipo_id             INTEGER REFERENCES tipos_mantenimiento(id),
            fecha               TEXT NOT NULL,
            anio                INTEGER NOT NULL,
            mes                 INTEGER NOT NULL,
            estado              TEXT DEFAULT 'Activo',
            clase               TEXT,
            clase_esp           TEXT,
            recurso             TEXT,
            observacion         TEXT,
            moneda              TEXT DEFAULT 'USD',
            forma_pago          TEXT,
            unidad              TEXT DEFAULT 'glb',
            cantidad            REAL DEFAULT 1,
            precio_sin_igv      REAL DEFAULT 0,
            valor_igv           REAL DEFAULT 0,
            parcial_calculado   REAL DEFAULT 0,
            parcial_con_igv     REAL DEFAULT 0,
            dcto_total          REAL DEFAULT 0,
            valor_total         REAL DEFAULT 0,
            estado_facturacion  TEXT DEFAULT 'Pendiente',
            gestor_compra       TEXT,
            creado_por          INTEGER REFERENCES usuarios(id),
            created_at          TEXT DEFAULT (datetime('now','localtime')),
            updated_at          TEXT DEFAULT (datetime('now','localtime'))
        )
    """)

    # ── Log de actividad ─────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS actividad (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id  INTEGER REFERENCES usuarios(id),
            accion      TEXT NOT NULL,
            detalle     TEXT,
            fecha       TEXT DEFAULT (datetime('now','localtime'))
        )
    """)

    conn.commit()
    _seed(conn)
    conn.close()


def _seed(conn):
    """Datos iniciales si la BD está vacía."""
    c = conn.cursor()

    # Usuario admin por defecto
    if not c.execute("SELECT 1 FROM usuarios WHERE username='admin'").fetchone():
        pw = bcrypt.hashpw(b"admin123", bcrypt.gensalt()).decode()
        c.execute("""INSERT INTO usuarios (username,password,nombre,rol)
                     VALUES (?,?,?,?)""", ("admin", pw, "Administrador", "admin"))

    # Obras
    for o in ["CHALLAPAMPA", "VILLANOVA", "ANDALUCÍA"]:
        c.execute("INSERT OR IGNORE INTO obras (nombre) VALUES (?)", (o,))

    # Equipos
    for e in ["Grúa Torre Potain", "Retroexcavadora JCB", "Planta de Concreto",
              "Camión Grúa", "Generador Eléctrico"]:
        c.execute("INSERT OR IGNORE INTO equipos (nombre) VALUES (?)", (e,))

    # Tipos
    for t, cl in [
        ("Mtto Preventivo",       "Servicios"),
        ("Mtto Correctivo",       "Servicios"),
        ("Mtto Preventivo Mayor", "Servicios"),
        ("Repuesto",              "Materiales"),
        ("Repuestos",             "Materiales"),
        ("Camb. Posición",        "Servicios"),
        ("Traslado",              "Servicios"),
        ("Aditamiento",           "Servicios"),
    ]:
        c.execute("INSERT OR IGNORE INTO tipos_mantenimiento (nombre,clase) VALUES (?,?)", (t, cl))

    # Proveedores
    for p in ["GRUAS ETAC PERU S.A.C.", "FMC & ENOVE S.R.L.",
              "IBERGRUAS PERU S.A.C.", "DERCO PERU S.A."]:
        c.execute("INSERT OR IGNORE INTO proveedores (nombre) VALUES (?)", (p,))

    conn.commit()


# ── AUTH ─────────────────────────────────────────────────────────

def login(username, password):
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM usuarios WHERE username=? AND activo=1", (username,)
    ).fetchone()
    if not row:
        conn.close(); return None
    if bcrypt.checkpw(password.encode(), row["password"].encode()):
        conn.execute("UPDATE usuarios SET last_login=datetime('now','localtime') WHERE id=?", (row["id"],))
        conn.commit()
        conn.close()
        return dict(row)
    conn.close()
    return None


# ── USUARIOS ──────────────────────────────────────────────────────

def get_usuarios():
    conn = get_conn()
    rows = conn.execute("SELECT id,username,nombre,rol,activo,created_at,last_login FROM usuarios ORDER BY nombre").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def crear_usuario(username, password, nombre, rol):
    pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    conn = get_conn()
    try:
        conn.execute("INSERT INTO usuarios (username,password,nombre,rol) VALUES (?,?,?,?)",
                     (username, pw, nombre, rol))
        conn.commit(); conn.close(); return True, "Usuario creado"
    except sqlite3.IntegrityError:
        conn.close(); return False, "El usuario ya existe"

def cambiar_password(user_id, nueva):
    pw = bcrypt.hashpw(nueva.encode(), bcrypt.gensalt()).decode()
    conn = get_conn()
    conn.execute("UPDATE usuarios SET password=? WHERE id=?", (pw, user_id))
    conn.commit(); conn.close()

def toggle_usuario(user_id):
    conn = get_conn()
    conn.execute("UPDATE usuarios SET activo=NOT activo WHERE id=?", (user_id,))
    conn.commit(); conn.close()


# ── CATÁLOGOS ─────────────────────────────────────────────────────

def get_obras(solo_activas=True):
    conn = get_conn()
    q = "SELECT * FROM obras" + (" WHERE activa=1" if solo_activas else "") + " ORDER BY nombre"
    rows = conn.execute(q).fetchall(); conn.close()
    return [dict(r) for r in rows]

def get_equipos(solo_activos=True):
    conn = get_conn()
    q = "SELECT * FROM equipos" + (" WHERE activo=1" if solo_activos else "") + " ORDER BY nombre"
    rows = conn.execute(q).fetchall(); conn.close()
    return [dict(r) for r in rows]

def get_proveedores(solo_activos=True):
    conn = get_conn()
    q = "SELECT * FROM proveedores" + (" WHERE activo=1" if solo_activos else "") + " ORDER BY nombre"
    rows = conn.execute(q).fetchall(); conn.close()
    return [dict(r) for r in rows]

def get_tipos():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM tipos_mantenimiento ORDER BY nombre").fetchall()
    conn.close(); return [dict(r) for r in rows]

def add_catalogo(tabla, nombre, extra=None):
    conn = get_conn()
    try:
        if tabla == "obras":
            conn.execute("INSERT INTO obras (nombre) VALUES (?)", (nombre,))
        elif tabla == "equipos":
            conn.execute("INSERT INTO equipos (nombre) VALUES (?)", (nombre,))
        elif tabla == "proveedores":
            conn.execute("INSERT INTO proveedores (nombre,ruc) VALUES (?,?)", (nombre, extra or ""))
        elif tabla == "tipos_mantenimiento":
            conn.execute("INSERT INTO tipos_mantenimiento (nombre,clase) VALUES (?,?)", (nombre, extra or "Servicios"))
        conn.commit(); conn.close(); return True
    except sqlite3.IntegrityError:
        conn.close(); return False


def update_catalogo(tabla, item_id, nombre, extra=None, usuario_id=None):
    conn = get_conn()
    if tabla == "obras":
        conn.execute("UPDATE obras SET nombre=? WHERE id=?", (nombre, item_id))
    elif tabla == "equipos":
        conn.execute("UPDATE equipos SET nombre=? WHERE id=?", (nombre, item_id))
    elif tabla == "proveedores":
        conn.execute("UPDATE proveedores SET nombre=?, ruc=? WHERE id=?", (nombre, extra or "", item_id))
    elif tabla == "tipos_mantenimiento":
        conn.execute("UPDATE tipos_mantenimiento SET nombre=?, clase=? WHERE id=?", (nombre, extra or "Servicios", item_id))
    conn.commit()
    if usuario_id:
        log_actividad(usuario_id, f"UPDATE_{tabla.upper()}", f"ID {item_id}", conn)
    conn.close()


def delete_catalogo(tabla, item_id, usuario_id=None):
    conn = get_conn()
    try:
        if tabla == "obras":
            conn.execute("DELETE FROM obras WHERE id=?", (item_id,))
        elif tabla == "equipos":
            conn.execute("DELETE FROM equipos WHERE id=?", (item_id,))
        elif tabla == "proveedores":
            conn.execute("DELETE FROM proveedores WHERE id=?", (item_id,))
        elif tabla == "tipos_mantenimiento":
            conn.execute("DELETE FROM tipos_mantenimiento WHERE id=?", (item_id,))
        if usuario_id:
            log_actividad(usuario_id, f"DELETE_{tabla.upper()}", f"ID {item_id}", conn)
        conn.commit(); conn.close()
        return True, "Eliminado correctamente"
    except sqlite3.IntegrityError as e:
        conn.close()
        return False, "No se puede eliminar: hay registros relacionados en órdenes de compra"
    except Exception as e:
        conn.close()
        return False, str(e)


# ── ÓRDENES ──────────────────────────────────────────────────────

def get_ordenes(filtros=None):
    conn = get_conn()
    sql = """
        SELECT o.*, ob.nombre AS obra, eq.nombre AS equipo,
               pr.nombre AS proveedor, ti.nombre AS tipo,
               u.nombre AS creado_nombre
        FROM ordenes o
        LEFT JOIN obras ob ON o.obra_id=ob.id
        LEFT JOIN equipos eq ON o.equipo_id=eq.id
        LEFT JOIN proveedores pr ON o.proveedor_id=pr.id
        LEFT JOIN tipos_mantenimiento ti ON o.tipo_id=ti.id
        LEFT JOIN usuarios u ON o.creado_por=u.id
    """
    conds, params = [], []
    if filtros:
        if filtros.get("anio"):
            conds.append("o.anio=?"); params.append(filtros["anio"])
        if filtros.get("mes"):
            conds.append("o.mes=?"); params.append(filtros["mes"])
        if filtros.get("obra_id"):
            conds.append("o.obra_id=?"); params.append(filtros["obra_id"])
        if filtros.get("equipo_id"):
            conds.append("o.equipo_id=?"); params.append(filtros["equipo_id"])
        if filtros.get("tipo_id"):
            conds.append("o.tipo_id=?"); params.append(filtros["tipo_id"])
        if filtros.get("busqueda"):
            conds.append("(o.nro_orden LIKE ? OR o.recurso LIKE ? OR pr.nombre LIKE ?)")
            b = f"%{filtros['busqueda']}%"
            params += [b, b, b]
    if conds:
        sql += " WHERE " + " AND ".join(conds)
    sql += " ORDER BY o.anio DESC, o.mes DESC, o.id DESC"
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_orden(orden_id):
    conn = get_conn()
    row = conn.execute("""
        SELECT o.*, ob.nombre AS obra, eq.nombre AS equipo,
               pr.nombre AS proveedor, ti.nombre AS tipo
        FROM ordenes o
        LEFT JOIN obras ob ON o.obra_id=ob.id
        LEFT JOIN equipos eq ON o.equipo_id=eq.id
        LEFT JOIN proveedores pr ON o.proveedor_id=pr.id
        LEFT JOIN tipos_mantenimiento ti ON o.tipo_id=ti.id
        WHERE o.id=?
    """, (orden_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def insertar_orden(data, usuario_id):
    conn = get_conn()
    fecha = data.get("fecha", datetime.now().strftime("%Y-%m-%d"))
    anio = int(fecha[:4])
    mes  = int(fecha[5:7])
    igv = round(float(data.get("precio_sin_igv", 0)) * 0.18, 2)
    parcial = round(float(data.get("cantidad", 1)) * float(data.get("precio_sin_igv", 0)), 2)
    conn.execute("""
        INSERT INTO ordenes (
            nro_orden, obra_id, equipo_id, proveedor_id, tipo_id,
            fecha, anio, mes, estado, clase, clase_esp,
            recurso, observacion, moneda, forma_pago, unidad,
            cantidad, precio_sin_igv, valor_igv, parcial_calculado,
            parcial_con_igv, dcto_total, valor_total,
            estado_facturacion, gestor_compra, creado_por
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        data["nro_orden"], data.get("obra_id"), data.get("equipo_id"),
        data.get("proveedor_id"), data.get("tipo_id"),
        fecha, anio, mes,
        data.get("estado", "Activo"), data.get("clase"), data.get("clase_esp"),
        data.get("recurso"), data.get("observacion"),
        data.get("moneda", "USD"), data.get("forma_pago"),
        data.get("unidad", "glb"),
        float(data.get("cantidad", 1)),
        float(data.get("precio_sin_igv", 0)),
        igv, parcial,
        round(parcial + igv, 2),
        float(data.get("dcto_total", 0)),
        round(parcial + igv - float(data.get("dcto_total", 0)), 2),
        data.get("estado_facturacion", "Pendiente"),
        data.get("gestor_compra"), usuario_id
    ))
    conn.commit()
    new_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    log_actividad(usuario_id, "INSERT_ORDEN", f"Orden #{data['nro_orden']}", conn)
    conn.commit(); conn.close()
    return new_id

def actualizar_orden(orden_id, data, usuario_id):
    igv = round(float(data.get("precio_sin_igv", 0)) * 0.18, 2)
    parcial = round(float(data.get("cantidad", 1)) * float(data.get("precio_sin_igv", 0)), 2)
    conn = get_conn()
    conn.execute("""
        UPDATE ordenes SET
            nro_orden=?, obra_id=?, equipo_id=?, proveedor_id=?, tipo_id=?,
            fecha=?, anio=?, mes=?, estado=?, recurso=?, observacion=?,
            moneda=?, forma_pago=?, unidad=?, cantidad=?, precio_sin_igv=?,
            valor_igv=?, parcial_calculado=?, parcial_con_igv=?,
            dcto_total=?, valor_total=?, estado_facturacion=?,
            gestor_compra=?, updated_at=datetime('now','localtime')
        WHERE id=?
    """, (
        data["nro_orden"], data.get("obra_id"), data.get("equipo_id"),
        data.get("proveedor_id"), data.get("tipo_id"),
        data["fecha"], int(data["fecha"][:4]), int(data["fecha"][5:7]),
        data.get("estado","Activo"), data.get("recurso"), data.get("observacion"),
        data.get("moneda","USD"), data.get("forma_pago"), data.get("unidad","glb"),
        float(data.get("cantidad",1)), float(data.get("precio_sin_igv",0)),
        igv, parcial, round(parcial+igv,2),
        float(data.get("dcto_total",0)),
        round(parcial+igv-float(data.get("dcto_total",0)),2),
        data.get("estado_facturacion","Pendiente"), data.get("gestor_compra"),
        orden_id
    ))
    log_actividad(usuario_id, "UPDATE_ORDEN", f"ID {orden_id}", conn)
    conn.commit(); conn.close()

def eliminar_orden(orden_id, usuario_id):
    conn = get_conn()
    conn.execute("DELETE FROM ordenes WHERE id=?", (orden_id,))
    log_actividad(usuario_id, "DELETE_ORDEN", f"ID {orden_id}", conn)
    conn.commit(); conn.close()


# ── ANALYTICS ────────────────────────────────────────────────────

def stats_anual():
    conn = get_conn()
    rows = conn.execute("""
        SELECT anio, ROUND(SUM(parcial_calculado),2) AS total,
               COUNT(*) AS num_ordenes
        FROM ordenes GROUP BY anio ORDER BY anio
    """).fetchall(); conn.close()
    return [dict(r) for r in rows]

def stats_mensual(anio=None):
    conn = get_conn()
    if anio:
        rows = conn.execute("""
            SELECT anio, mes, ROUND(SUM(parcial_calculado),2) AS total,
                   COUNT(*) AS num_ordenes
            FROM ordenes WHERE anio=? GROUP BY anio,mes ORDER BY mes
        """, (anio,)).fetchall()
    else:
        rows = conn.execute("""
            SELECT anio, mes, ROUND(SUM(parcial_calculado),2) AS total,
                   COUNT(*) AS num_ordenes
            FROM ordenes GROUP BY anio,mes ORDER BY anio,mes
        """).fetchall()
    conn.close(); return [dict(r) for r in rows]

def stats_por_tipo(anio=None):
    conn = get_conn()
    q = """
        SELECT ti.nombre AS tipo, ROUND(SUM(o.parcial_calculado),2) AS total,
               COUNT(*) AS num
        FROM ordenes o
        LEFT JOIN tipos_mantenimiento ti ON o.tipo_id=ti.id
    """
    if anio: q += f" WHERE o.anio={anio}"
    q += " GROUP BY ti.nombre ORDER BY total DESC"
    rows = conn.execute(q).fetchall(); conn.close()
    return [dict(r) for r in rows]

def stats_por_proveedor(anio=None, top=8):
    conn = get_conn()
    q = """
        SELECT pr.nombre AS proveedor, ROUND(SUM(o.parcial_calculado),2) AS total,
               COUNT(DISTINCT o.nro_orden) AS num_ordenes
        FROM ordenes o
        LEFT JOIN proveedores pr ON o.proveedor_id=pr.id
    """
    if anio: q += f" WHERE o.anio={anio}"
    q += f" GROUP BY pr.nombre ORDER BY total DESC LIMIT {top}"
    rows = conn.execute(q).fetchall(); conn.close()
    return [dict(r) for r in rows]

def stats_trimestral(anio=None):
    conn = get_conn()
    q = """
        SELECT anio,
               CASE WHEN mes<=3 THEN 1 WHEN mes<=6 THEN 2
                    WHEN mes<=9 THEN 3 ELSE 4 END AS trimestre,
               ROUND(SUM(parcial_calculado),2) AS total
        FROM ordenes
    """
    if anio: q += f" WHERE anio={anio}"
    q += " GROUP BY anio,trimestre ORDER BY anio,trimestre"
    rows = conn.execute(q).fetchall(); conn.close()
    return [dict(r) for r in rows]

def stats_semestral(anio=None):
    conn = get_conn()
    q = """
        SELECT anio,
               CASE WHEN mes<=6 THEN 1 ELSE 2 END AS semestre,
               ROUND(SUM(parcial_calculado),2) AS total
        FROM ordenes
    """
    if anio: q += f" WHERE anio={anio}"
    q += " GROUP BY anio,semestre ORDER BY anio,semestre"
    rows = conn.execute(q).fetchall(); conn.close()
    return [dict(r) for r in rows]

def kpis_dashboard():
    conn = get_conn()
    r = {}
    row = conn.execute("SELECT SUM(parcial_calculado) AS t, COUNT(*) AS n FROM ordenes").fetchone()
    r["total_historico"] = row["t"] or 0
    r["total_ordenes"]   = row["n"] or 0
    anio_max = conn.execute("SELECT MAX(anio) FROM ordenes").fetchone()[0] or 0
    r["anio_max"] = anio_max
    row2 = conn.execute("SELECT SUM(parcial_calculado) AS t FROM ordenes WHERE anio=?", (anio_max,)).fetchone()
    r["total_anio"] = row2["t"] or 0
    r["num_proveedores"] = conn.execute("SELECT COUNT(DISTINCT proveedor_id) FROM ordenes").fetchone()[0] or 0
    r["num_obras"]       = conn.execute("SELECT COUNT(DISTINCT obra_id) FROM ordenes").fetchone()[0] or 0
    conn.close(); return r

def get_anios():
    conn = get_conn()
    rows = conn.execute("SELECT DISTINCT anio FROM ordenes WHERE anio IS NOT NULL ORDER BY anio").fetchall()
    conn.close(); return [r["anio"] for r in rows]


# ── LOG ──────────────────────────────────────────────────────────

def log_actividad(usuario_id, accion, detalle="", conn=None):
    close = conn is None
    if conn is None: conn = get_conn()
    conn.execute("INSERT INTO actividad (usuario_id,accion,detalle) VALUES (?,?,?)",
                 (usuario_id, accion, detalle))
    if close: conn.commit(); conn.close()

def get_actividad(limit=100):
    conn = get_conn()
    rows = conn.execute("""
        SELECT a.fecha, u.nombre AS usuario, a.accion, a.detalle
        FROM actividad a LEFT JOIN usuarios u ON a.usuario_id=u.id
        ORDER BY a.id DESC LIMIT ?
    """, (limit,)).fetchall()
    conn.close(); return [dict(r) for r in rows]
