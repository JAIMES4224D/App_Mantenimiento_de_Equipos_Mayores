"""
Base de datos local SQLite optimizada para importación masiva en hilos secundarios.
Contiene TODOS los métodos de consulta, catálogos, inserción y lógica de filtros analíticos requeridos por la interfaz.
"""
import sqlite3
import os
import sys
import bcrypt
from datetime import datetime

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(BASE_DIR, "mantenimiento.db")

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()
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
    c.execute("""CREATE TABLE IF NOT EXISTS obras (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT UNIQUE NOT NULL, activa INTEGER NOT NULL DEFAULT 1)""")
    c.execute("""CREATE TABLE IF NOT EXISTS equipos (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT UNIQUE NOT NULL, activo INTEGER NOT NULL DEFAULT 1)""")
    c.execute("""CREATE TABLE IF NOT EXISTS proveedores (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT UNIQUE NOT NULL, ruc TEXT, activo INTEGER NOT NULL DEFAULT 1)""")
    c.execute("""CREATE TABLE IF NOT EXISTS tipos_mantenimiento (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT UNIQUE NOT NULL, clase TEXT NOT NULL DEFAULT 'Servicios')""")
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
    c.execute("""CREATE TABLE IF NOT EXISTS actividad (id INTEGER PRIMARY KEY AUTOINCREMENT, usuario_id INTEGER REFERENCES usuarios(id), accion TEXT NOT NULL, detalle TEXT, fecha TEXT DEFAULT (datetime('now','localtime')))""")
    conn.commit()
    _seed(conn)
    conn.close()

def _seed(conn):
    c = conn.cursor()
    if not c.execute("SELECT 1 FROM usuarios WHERE username='admin'").fetchone():
        pw = bcrypt.hashpw(b"admin123", bcrypt.gensalt()).decode()
        c.execute("INSERT INTO usuarios (username,password,nombre,rol) VALUES (?,?,?,?)", ("admin", pw, "Administrador", "admin"))
    for o in ["CHALLAPAMPA", "VILLANOVA", "ANDALUCÍA"]:
        c.execute("INSERT OR IGNORE INTO obras (nombre) VALUES (?)", (o,))
    for e in ["Grúa Torre Potain", "Retroexcavadora JCB", "Planta de Concreto", "Camión Grúa", "Generador Eléctrico", "Equipo Mayor General"]:
        c.execute("INSERT OR IGNORE INTO equipos (nombre) VALUES (?)", (e,))
    for t, cl in [("Mtto Preventivo", "Servicios"), ("Mtto Correctivo", "Servicios"), ("Repuesto", "Materiales"), ("Repuestos", "Materiales")]:
        c.execute("INSERT OR IGNORE INTO tipos_mantenimiento (nombre,clase) VALUES (?,?)", (t, cl))
    conn.commit()

# ── AUTH & USUARIOS ──
def login(username, password):
    conn = get_conn()
    row = conn.execute("SELECT * FROM usuarios WHERE username=? AND activo=1", (username,)).fetchone()
    if not row: conn.close(); return None
    if bcrypt.checkpw(password.encode(), row["password"].encode()):
        conn.execute("UPDATE usuarios SET last_login=datetime('now','localtime') WHERE id=?", (row["id"],))
        conn.commit(); conn.close(); return dict(row)
    conn.close(); return None

def get_usuarios():
    conn = get_conn()
    rows = conn.execute("SELECT id,username,nombre,rol,activo,created_at,last_login FROM usuarios ORDER BY nombre").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def crear_usuario(username, password, nombre, rol):
    pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    conn = get_conn()
    try:
        conn.execute("INSERT INTO usuarios (username,password,nombre,rol) VALUES (?,?,?,?)", (username, pw, nombre, rol))
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

def log_actividad(usuario_id, accion, detalle="", conn=None):
    close = conn is None
    if conn is None: conn = get_conn()
    conn.execute("INSERT INTO actividad (usuario_id,accion,detalle) VALUES (?,?,?)", (usuario_id, accion, detalle))
    if close: conn.commit(); conn.close()

# ── MÉTODOS DE CATÁLOGOS COMPLETOS ──
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
            conn.execute("INSERT INTO obras (nombre) VALUES (?)", (nombre.strip().upper(),))
        elif tabla == "equipos":
            conn.execute("INSERT INTO equipos (nombre) VALUES (?)", (nombre.strip(),))
        elif tabla == "proveedores":
            conn.execute("INSERT INTO proveedores (nombre, ruc) VALUES (?,?)", (nombre.strip().upper(), (extra or "").strip()))
        elif tabla == "tipos_mantenimiento":
            conn.execute("INSERT INTO tipos_mantenimiento (nombre, clase) VALUES (?,?)", (nombre.strip(), (extra or "Servicios").strip()))
        conn.commit(); conn.close(); return True
    except sqlite3.IntegrityError:
        conn.close(); return False

def update_catalogo(tabla, item_id, nombre, extra=None, usuario_id=None):
    conn = get_conn()
    if tabla == "obras":
        conn.execute("UPDATE obras SET nombre=? WHERE id=?", (nombre.strip().upper(), item_id))
    elif tabla == "equipos":
        conn.execute("UPDATE equipos SET nombre=? WHERE id=?", (nombre.strip(), item_id))
    elif tabla == "proveedores":
        conn.execute("UPDATE proveedores SET nombre=?, ruc=? WHERE id=?", (nombre.strip().upper(), (extra or "").strip(), item_id))
    elif tabla == "tipos_mantenimiento":
        conn.execute("UPDATE tipos_mantenimiento SET nombre=?, clase=? WHERE id=?", (nombre.strip(), (extra or "Servicios").strip(), item_id))
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
    except sqlite3.IntegrityError:
        conn.close()
        return False, "No se puede eliminar: hay registros relacionados en órdenes de compra"
    except Exception as e:
        conn.close()
        return False, str(e)

# ── GET_OR_CREATE AUXILIARES PARA IMPORTACIÓN ──
def get_or_create_obra(nombre, conn):
    nombre = str(nombre).strip().upper()
    if not nombre or nombre in ["NAN", "NONE"]: nombre = "SIN OBRA"
    row = conn.execute("SELECT id FROM obras WHERE nombre=?", (nombre,)).fetchone()
    if row: return row["id"]
    conn.execute("INSERT INTO obras (nombre) VALUES (?)", (nombre,))
    return conn.execute("SELECT last_insert_rowid()").fetchone()[0]

def get_or_create_equipo(nombre, conn):
    nombre = str(nombre).strip()
    row = conn.execute("SELECT id FROM equipos WHERE nombre=?", (nombre,)).fetchone()
    if row: return row["id"]
    conn.execute("INSERT INTO equipos (nombre) VALUES (?)", (nombre,))
    return conn.execute("SELECT last_insert_rowid()").fetchone()[0]

def get_or_create_proveedor(nombre, conn):
    nombre = str(nombre).strip().upper()
    if not nombre or nombre in ["NAN", "NONE"]: nombre = "SIN PROVEEDOR"
    row = conn.execute("SELECT id FROM proveedores WHERE nombre=?", (nombre,)).fetchone()
    if row: return row["id"]
    conn.execute("INSERT INTO proveedores (nombre, ruc) VALUES (?,?)", (nombre, ""))
    return conn.execute("SELECT last_insert_rowid()").fetchone()[0]

def get_or_create_tipo(nombre, clase, conn):
    nombre = str(nombre).strip()
    clase = str(clase).strip()
    if not nombre or nombre in ["NAN", "NONE"]: nombre = "Mantenimiento General"
    if not clase or clase in ["NAN", "NONE"]: clase = "Servicios"
    row = conn.execute("SELECT id FROM tipos_mantenimiento WHERE nombre=?", (nombre,)).fetchone()
    if row: return row["id"]
    conn.execute("INSERT INTO tipos_mantenimiento (nombre, clase) VALUES (?,?)", (nombre, clase))
    return conn.execute("SELECT last_insert_rowid()").fetchone()[0]

def _identificar_equipo_por_recurso(recurso_text):
    txt = str(recurso_text).upper()
    if "TORRE" in txt or "GRUA" in txt or "POTAIN" in txt: return "Grúa Torre Potain"
    if "RETRO" in txt or "JCB" in txt or "EXCAVADORA" in txt: return "Retroexcavadora JCB"
    if "PLANTA" in txt or "MEZCLADOR" in txt or "CONCRETO" in txt: return "Planta de Concreto"
    if "CAMION" in txt or "CAMIÓ" in txt: return "Camión Grúa"
    if "GENERADOR" in txt or "GRUPO" in txt or "ELECTR" in txt: return "Generador Eléctrico"
    return "Equipo Mayor General"

# ── FILTROS DINÁMICOS COMPARTIDOS ──
def _construir_where_filtros(filtros):
    conds = []
    params = []
    if filtros:
        if filtros.get("anio"):
            conds.append("o.anio = ?")
            params.append(int(filtros["anio"]))
        if filtros.get("obra_id"):
            conds.append("o.obra_id = ?")
            params.append(int(filtros["obra_id"]))
        if filtros.get("busqueda"):
            conds.append("(o.nro_orden LIKE ? OR o.recurso LIKE ? OR pr.nombre LIKE ?)")
            b = f"%{filtros['busqueda']}%"
            params += [b, b, b]
    return conds, params

# ── ÓRDENES: CONSULTAS VISUALES ──
def get_ordenes(filtros=None):
    conn = get_conn()
    sql = "SELECT o.*, ob.nombre AS obra, eq.nombre AS equipo, pr.nombre AS proveedor, ti.nombre AS tipo, u.nombre AS creado_nombre FROM ordenes o LEFT JOIN obras ob ON o.obra_id=ob.id LEFT JOIN equipos eq ON o.equipo_id=eq.id LEFT JOIN proveedores pr ON o.proveedor_id=pr.id LEFT JOIN tipos_mantenimiento ti ON o.tipo_id=ti.id LEFT JOIN usuarios u ON o.creado_por=u.id"
    conds, params = _construir_where_filtros(filtros)
    if conds: sql += " WHERE " + " AND ".join(conds)
    sql += " ORDER BY o.anio DESC, o.mes DESC, o.id DESC"
    rows = conn.execute(sql, params).fetchall(); conn.close()
    return [dict(r) for r in rows]

def get_orden(orden_id):
    conn = get_conn()
    row = conn.execute("SELECT o.*, ob.nombre AS obra, eq.nombre AS equipo, pr.nombre AS proveedor, ti.nombre AS tipo FROM ordenes o LEFT JOIN obras ob ON o.obra_id=ob.id LEFT JOIN equipos eq ON o.equipo_id=eq.id LEFT JOIN proveedores pr ON o.proveedor_id=pr.id LEFT JOIN tipos_mantenimiento ti ON o.tipo_id=ti.id WHERE o.id=?", (orden_id,)).fetchone()
    conn.close(); return dict(row) if row else None

# ── CLAVE: AGREGAR CONTROLES CRUD DIRECTOS MANUALES (¡SOLUCIONADO!) ──
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
    fecha = data.get("fecha", datetime.now().strftime("%Y-%m-%d"))
    
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
        fecha, int(fecha[:4]), int(fecha[5:7]),
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

# ── ESTADÍSTICAS REPARADAS ──
def kpis_dashboard():
    conn = get_conn()
    r = {}
    row = conn.execute("SELECT SUM(parcial_calculado) AS t, COUNT(*) AS n FROM ordenes").fetchone()
    r["total_historico"] = row["t"] or 0; r["total_ordenes"] = row["n"] or 0
    anio_max = conn.execute("SELECT MAX(anio) FROM ordenes").fetchone()[0] or 0
    r["anio_max"] = anio_max
    row2 = conn.execute("SELECT SUM(parcial_calculado) AS t FROM ordenes WHERE anio=?", (anio_max,)).fetchone()
    r["total_anio"] = row2["t"] or 0
    r["num_proveedores"] = conn.execute("SELECT COUNT(DISTINCT proveedor_id) FROM ordenes").fetchone()[0] or 0
    r["num_obras"] = conn.execute("SELECT COUNT(DISTINCT obra_id) FROM ordenes").fetchone()[0] or 0
    conn.close(); return r

def stats_anual(filtros=None):
    conn = get_conn()
    sql = "SELECT o.anio, ROUND(SUM(o.parcial_calculado),2) AS total, COUNT(*) AS num_ordenes FROM ordenes o LEFT JOIN proveedores pr ON o.proveedor_id=pr.id"
    conds, params = _construir_where_filtros(filtros)
    if conds: sql += " WHERE " + " AND ".join(conds)
    sql += " GROUP BY o.anio ORDER BY o.anio"
    rows = conn.execute(sql, params).fetchall(); conn.close()
    return [dict(r) for r in rows]

def stats_mensual(filtros=None):
    conn = get_conn()
    sql = "SELECT o.anio, o.mes, ROUND(SUM(o.parcial_calculado),2) AS total, COUNT(*) AS num_ordenes FROM ordenes o LEFT JOIN proveedores pr ON o.proveedor_id=pr.id"
    conds, params = _construir_where_filtros(filtros)
    if conds: sql += " WHERE " + " AND ".join(conds)
    sql += " GROUP BY o.anio, o.mes ORDER BY o.anio, o.mes"
    rows = conn.execute(sql, params).fetchall(); conn.close()
    return [dict(r) for r in rows]

def stats_trimestral(filtros=None):
    conn = get_conn()
    sql = """
        SELECT o.anio,
               CASE WHEN o.mes<=3 THEN 1 WHEN o.mes<=6 THEN 2
                    WHEN o.mes<=9 THEN 3 ELSE 4 END AS trimestre,
               ROUND(SUM(o.parcial_calculado),2) AS total
        FROM ordenes o
        LEFT JOIN proveedores pr ON o.proveedor_id=pr.id
    """
    conds, params = _construir_where_filtros(filtros)
    if conds: sql += " WHERE " + " AND ".join(conds)
    sql += " GROUP BY o.anio, trimestre ORDER BY o.anio, trimestre"
    rows = conn.execute(sql, params).fetchall(); conn.close()
    return [dict(r) for r in rows]

def stats_semestral(filtros=None):
    conn = get_conn()
    sql = """
        SELECT o.anio,
               CASE WHEN o.mes<=6 THEN 1 ELSE 2 END AS semestre,
               ROUND(SUM(o.parcial_calculado),2) AS total
        FROM ordenes o
        LEFT JOIN proveedores pr ON o.proveedor_id=pr.id
    """
    conds, params = _construir_where_filtros(filtros)
    if conds: sql += " WHERE " + " AND ".join(conds)
    sql += " GROUP BY o.anio, semestre ORDER BY o.anio, semestre"
    rows = conn.execute(sql, params).fetchall(); conn.close()
    return [dict(r) for r in rows]

def stats_por_tipo(filtros=None):
    conn = get_conn()
    sql = """
        SELECT ti.nombre AS tipo, ROUND(SUM(o.parcial_calculado),2) AS total, COUNT(*) AS num 
        FROM ordenes o 
        LEFT JOIN tipos_mantenimiento ti ON o.tipo_id=ti.id
        LEFT JOIN proveedores pr ON o.proveedor_id=pr.id
    """
    conds, params = _construir_where_filtros(filtros)
    if conds: sql += " WHERE " + " AND ".join(conds)
    sql += " GROUP BY ti.nombre ORDER BY total DESC"
    rows = conn.execute(sql, params).fetchall(); conn.close()
    return [dict(r) for r in rows]

def stats_por_proveedor(filtros=None, top=8):
    conn = get_conn()
    sql = """
        SELECT pr.nombre AS proveedor, ROUND(SUM(o.parcial_calculado),2) AS total, COUNT(DISTINCT o.nro_orden) AS num_ordenes 
        FROM ordenes o 
        LEFT JOIN proveedores pr ON o.proveedor_id=pr.id
    """
    conds, params = _construir_where_filtros(filtros)
    if conds: sql += " WHERE " + " AND ".join(conds)
    sql += f" GROUP BY pr.nombre ORDER BY total DESC LIMIT {top}"
    rows = conn.execute(sql, params).fetchall(); conn.close()
    return [dict(r) for r in rows]

def get_anios():
    conn = get_conn()
    rows = conn.execute("SELECT DISTINCT anio FROM ordenes WHERE anio IS NOT NULL ORDER BY anio").fetchall(); conn.close()
    return [r["anio"] for r in rows]

def get_actividad(limit=100):
    conn = get_conn()
    rows = conn.execute("SELECT a.fecha, u.nombre AS usuario, a.accion, a.detalle FROM actividad a LEFT JOIN usuarios u ON a.usuario_id=u.id ORDER BY a.id DESC LIMIT ?", (limit,)).fetchall(); conn.close()
    return [dict(r) for r in rows]