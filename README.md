# MantenimientoApp v1.0
## Sistema de Gestión de Costos de Mantenimiento — Equipos Mayores

### Instalación

```bash
pip install -r requirements.txt
python app.py
```

### Acceso por defecto
- **Usuario:** admin
- **Contraseña:** admin123

### Módulos
| Módulo | Descripción |
|--------|-------------|
| 🏠 Dashboard | KPIs + gráficos de resumen en tiempo real |
| 📋 Órdenes | Ingreso, edición, búsqueda y eliminación de OCs |
| 📊 Reportes | Gráficos: Anual, Mensual, Trimestral, Semestral, Por Tipo, Proveedores, Comparativo |
| 📁 Catálogos | Obras, Equipos, Proveedores, Tipos de Mantenimiento |
| ⚙ Admin | Usuarios, roles, log de actividad (solo admin) |

### Base de datos
SQLite local — se crea automáticamente como `mantenimiento.db`
No requiere instalar MySQL ni ningún servidor.

### Roles
- **admin** — acceso total + módulo de administración
- **supervisor** — acceso a reportes y catálogos, puede editar
- **operador** — ingreso de órdenes y consultas
