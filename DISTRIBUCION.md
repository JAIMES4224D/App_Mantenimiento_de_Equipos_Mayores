# 📦 MTTO PRO - Distribución como Ejecutable

## ✅ Ejecutable Generado

**Archivo**: `dist/mtto_pro.exe` (80.8 MB)

## 🚀 Usar en Cualquier Windows

El archivo `.exe` funciona en **cualquier Windows 10/11 sin necesidad de instalar nada**:

1. Copiar `dist/mtto_pro.exe` a cualquier carpeta
2. Ejecutar el archivo (doble clic)
3. Inicia automáticamente la aplicación

## 📋 Requisitos

- **Windows 10 o superior**
- Nada más (todas las dependencias están incluidas)

## 🔧 Distribución

Para compartir la aplicación:

```bash
# Opción 1: Carpeta completa
Copiar d:\Proyectos\mtto_pro\dist\mtto_pro.exe a otra máquina

# Opción 2: Crear un instalador (opcional)
# Usar WiX Toolset o NSIS para crear un instalador .msi o .exe de instalación
```

## 📝 Notas Técnicas

- **Generador**: PyInstaller 6.20.0
- **Python**: 3.14.5
- **Tamaño**: 80.8 MB (incluye todas las dependencias: PyQt6, Matplotlib, BCrypt, SQLite)
- **Base de datos**: SQLite local (`mantenimiento.db` se crea en la carpeta de ejecución)

## ⚡ Rendimiento

- Inicio rápido (~3-5 segundos)
- Sin tiempos de espera de compilación
- Interfaz responsiva

## 🛠️ Para Regenerar el .exe

Si modifica el código:

```bash
cd d:\Proyectos\mtto_pro
c:\python314\python.exe -m PyInstaller mtto_pro.spec --distpath dist --workpath build -y
```

## 📦 Archivos de Compilación

- `mtto_pro.spec` - Configuración de PyInstaller
- `build/` - Archivos temporales (se puede eliminar)
- `dist/mtto_pro.exe` - **Ejecutable final** (usar este archivo)
