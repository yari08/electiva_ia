# Semana 07: Tool Calling y Model Context Protocol (MCP)

Este paquete contiene todos los archivos ejecutables y scripts de configuración para el taller de la **Semana 07: Construir un agente con Tool Calling y MCP** del curso *Ingeniería de Aplicaciones con IA*.

---

## 📁 Contenido del Paquete (10 Archivos)

1. `setup_postgres.sh`: Script de automatización en Bash para despliegue de PostgreSQL en Docker (macOS / Linux).
2. `setup_postgres.ps1`: Script de automatización en PowerShell para despliegue de PostgreSQL en Docker (Windows).
3. `setup_postgres.bat`: Script Batch para invocar la configuración de PowerShell en CMD sin restricciones (Windows).
4. `init_db.sql`: Script SQL con la estructura y semillas de prueba para la base de datos `domicilios`.
5. `requirements.txt`: Archivo de dependencias Python (`mcp<2`, `psycopg2-binary`, `pydantic`).
6. `cliente_mcp_postgres.py`: Cliente Python asíncrono para interactuar con el servidor MCP oficial de PostgreSQL (`@modelcontextprotocol/server-postgres`).
7. `servidor_mcp.py`: Servidor MCP propio construido con `FastMCP` que expone herramientas de cálculo de descuentos y consulta de cobertura de domicilios.
8. `probador_mcp_local.py`: Script de pruebas locales para verificar herramientas del servidor FastMCP vía transporte STDIO.
9. `mcp_config.json`: Archivo de configuración de ejemplo para integraciones con Claude Desktop o Cursor.
10. `README.md` / `LEEME.txt`: Guía de instrucciones paso a paso para ejecución en macOS, Linux y Windows.

---

## ⚙️ Requisitos Previos

- **Docker Desktop** instalado y en ejecución.
- **Python 3.10** o superior.
- **Node.js** y `npx` (requerido para ejecutar el servidor MCP oficial de PostgreSQL `@modelcontextprotocol/server-postgres`).

---

## 🚀 Instrucciones de Ejecución Paso a Paso

### Paso 1: Desplegar PostgreSQL en Docker y Cargar Datos Iniciales

Ejecuta el script correspondiente a tu sistema operativo:

- **macOS / Linux:**
  ```bash
  chmod +x setup_postgres.sh
  ./setup_postgres.sh
  ```

- **Windows (PowerShell):**
  ```powershell
  Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
  .\setup_postgres.ps1
  ```

- **Windows (CMD Batch):**
  ```cmd
  setup_postgres.bat
  ```

El script creará e iniciará un contenedor Docker llamado `postgres-mcp` en el puerto `55432` con la base de datos `domicilios` e insertará los datos iniciales de las tablas `clientes` y `pedidos`.

---

### Paso 2: Instalar Dependencias de Python

Instala las librerías necesarias en tu entorno virtual de Python:

```bash
pip install -r requirements.txt
```

---

### Paso 3: Probar el Cliente MCP de PostgreSQL

Ejecuta el cliente de prueba en Python para conectarte al servidor MCP de PostgreSQL vía `npx`:

- **macOS / Linux:**
  ```bash
  python3 cliente_mcp_postgres.py
  ```

- **Windows:**
  ```cmd
  python cliente_mcp_postgres.py
  ```

El cliente descubrirá automáticamente las herramientas expuestas por el servidor de Postgres, consultará el esquema de la base de datos y ejecutará una consulta SQL analítica sobre pedidos y clientes.

---

### Paso 4: Probar el Servidor MCP Propio (FastMCP)

Ejecuta el script probador local que levanta el servidor `servidor_mcp.py` en un subproceso y consume sus herramientas:

- **macOS / Linux:**
  ```bash
  python3 probador_mcp_local.py
  ```

- **Windows:**
  ```cmd
  python probador_mcp_local.py
  ```

Verificarás el funcionamiento de las herramientas `@mcp.tool`:
- `calcular_descuento_cliente`: Calcula el descuento aplicable según el monto total y la antigüedad del cliente.
- `consultar_estado_cobertura`: Consulta los tiempos y la disponibilidad de domicilios por barrio y ciudad.

---

### Paso 5: Configurar en Claude Desktop o Cursor (Opcional)

Puedes copiar la configuración de `mcp_config.json` e incluirla en el archivo `claude_desktop_config.json` de Claude Desktop o en las configuraciones de Cursor para interactuar visualmente con ambos servidores MCP.
