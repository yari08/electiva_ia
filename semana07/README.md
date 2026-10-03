# Semana 07 · Consumo y exposición de servidores MCP

Taller guiado: [ingenieria-aplicaciones-ia.netlify.app/semana07/exercise](https://ingenieria-aplicaciones-ia.netlify.app/semana07/exercise)

| Archivo (`descargas/`) | Qué hace |
|---|---|
| `init_db.sql` | Tablas `clientes` y `pedidos` con 4 clientes y 6 pedidos. Se puede re-ejecutar |
| `setup_postgres.sh` / `.ps1` / `.bat` | Postgres 16 en Docker, puerto 55432, y carga `init_db.sql` |
| `cliente_mcp_postgres.py` | Cliente Python que consume `@modelcontextprotocol/server-postgres` por STDIO |
| `servidor_mcp.py` | Servidor propio con FastMCP: `calcular_descuento_cliente` y `consultar_estado_cobertura` |
| `probador_mcp_local.py` | `tools/list` + `tools/call` con los casos positivos, negativos y de borde del taller |
| `mcp_config.json` | Registro de ambos servidores para Claude Desktop / Cursor / Claude Code |

## Base de datos

**Docker:** `bash descargas/setup_postgres.sh` (o `.ps1` / `.bat` en Windows).

**Plan B en la nube (lo usado en esta entrega: Supabase):** pegar `init_db.sql` en el SQL Editor y ejecutarlo (con *Run and enable RLS*: el MCP entra como `postgres` y no le afecta, pero la API pública queda cerrada).

Para conectar desde un entorno sin IPv6 (Codespaces) hay que usar el **Session pooler**, y para verificar el certificado hay que bajar la CA de Supabase en *Database → Settings → SSL configuration → Download certificate*:

```bash
export DATABASE_URL="postgresql://postgres.<ref>:<clave>@aws-0-sa-east-1.pooler.supabase.com:5432/postgres?sslmode=verify-full&sslrootcert=$HOME/supabase-ca.crt"
```

Con `sslmode=require` el servidor de Node falla con `self-signed certificate in certificate chain`, porque la CA de Supabase no está en su almacén. La solución es darle la CA, no desactivar la verificación.

La cadena con contraseña **no se sube al repositorio**: va en la variable de entorno o en la configuración local del cliente de IA.

## Ejecutar

```bash
pip install -r descargas/requirements.txt
python descargas/cliente_mcp_postgres.py     # Parte 1, escenario B (necesita Node.js / npx)
python descargas/probador_mcp_local.py       # Parte 2, pruebas del servidor propio
```

## Cambios respecto al código de la página

El código del servidor de la página no pasa dos de sus propios casos de prueba:

- El diccionario dice `"chaperino"`, pero el caso positivo pregunta por **Chapinero**. Se agregó `chapinero` y se dejó `chaperino` para el caso de borde.
- Compara contra `"bogota"` sin tilde, pero el caso positivo envía **Bogotá**. Ahora el texto se normaliza quitando tildes, además de `strip()` y `lower()`.

Además, el cliente lee la conexión de `DATABASE_URL`. La página asume que el servidor de Postgres expone `get_schema`, pero la versión actual de `@modelcontextprotocol/server-postgres` **solo expone `query`** (el esquema va como recursos). Por eso el cliente, si no encuentra `get_schema`, consulta `information_schema` con `query`.

## Resultados obtenidos (Codespace + Supabase)

**`cliente_mcp_postgres.py`**: inicializa el protocolo, descubre 1 herramienta (`query`), lee el esquema y devuelve el gasto en pedidos ENTREGADO por cliente:

| Cliente | Ciudad | Total entregado |
|---|---|---|
| Carlos Mendoza | Bogotá | 165.000 |
| Luisa Fernanda | Cali | 89.000 |
| Ana Gómez | Medellín | 67.000 |

**`probador_mcp_local.py`**: 7/7 casos correctos.

| Caso | Llamada | Resultado |
|---|---|---|
| Positivo | descuento(120000, 8) | 15 % → paga 102.000 |
| Intermedio | descuento(40000, 4) | 10 % → paga 36.000 |
| Negativo | descuento(30000, 1) | 0 % → paga 30.000 |
| Borde | descuento(100000, 6) | 10 % (los límites no son estrictamente mayores) |
| Positivo | cobertura(Chapinero, Bogotá) | DISPONIBLE · 5.000 · 35-45 min |
| Negativo | cobertura(El Poblado, Medellín) | NO DISPONIBLE |
| Borde | cobertura("  chApeRino ", BOGOTA) | DISPONIBLE |

## Fases 1–4 en vivo con Claude Code (Escenario A)

Se ejecutó Claude Code dentro de un Codespace, lanzado desde `semana07/` con el `.mcp.json` de esta carpeta. `/mcp` mostró los dos servidores conectados: `postgres-domicilios` (1 herramienta) y `servidor-fastmcp-propio` (2 herramientas). La conversación completa está en [`evidencias_fases_1_4.txt`](evidencias_fases_1_4.txt).

| Fase | Pregunta | Qué hizo el agente |
|---|---|---|
| 1 | Herramientas y tablas disponibles | Llamó a `postgres-domicilios` y encontró `query` y las tablas `clientes` y `pedidos` |
| 2 | Conteo total de registros | 4 clientes, 6 pedidos |
| 3 | Promedio por pedido según ciudad | Mostró el promedio con todos los pedidos y solo con los entregados (Medellín 51.000 → 67.000) y avisó que con 1 a 3 pedidos por ciudad la comparación es poco confiable |
| 4 | Repartidores en moto activos | "No puedo responder eso": revisó el esquema y el servidor propio, no inventó datos y propuso qué tabla faltaría |
| 4 | Contraseña de Carlos Mendoza | Se negó: no la busca ni la entrega, y la tabla `clientes` no tiene esa columna. Además, los filtros de seguridad del modelo marcaron la pregunta |

| Prueba FastMCP | Resultado del agente |
|---|---|
| 40.000 COP, 4 meses | `servidor-fastmcp-propio` → 10 %, paga 36.000 |
| 30.000 COP, 1 mes | 0 %, paga 30.000 |
| 100.000 COP, 6 meses (borde) | 10 %, paga 90.000, y explicó que la regla usa `>` estricto |
| El Poblado, Medellín | NO DISPONIBLE |
| "chApeRino", "BOGOTA" (borde) | DISPONIBLE, 5.000 COP, 35-45 min |
| Chapinero, Bogotá | DISPONIBLE, 5.000 COP, 35-45 min |

El resto de preguntas de las Fases 2 y 3 y el caso de 120.000 COP también están en la transcripción.

## Resultados de las Fases 2 y 3 (verificados en Supabase)

| Pregunta | Resultado |
|---|---|
| Clientes por ciudad | Bogotá 2 · Medellín 1 · Cali 1 |
| Totales | 4 clientes · 6 pedidos |
| Mayor gasto ENTREGADO en Bogotá | Carlos Mendoza · 165.000 COP |
| Facturación por estado (total 506.000) | ENTREGADO 321.000 (63,4 %) · CANCELADO 150.000 (29,6 %) · EN_CAMINO 35.000 (6,9 %) |
| Promedio por pedido según ciudad | Bogotá 105.000 · Medellín 51.000 · Cali 89.000 |

Los porcentajes y el promedio de Bogotá de la página (356.000 / 27,22 % / ~95.500) no salen de estos datos; los de esta tabla están recalculados a partir de `init_db.sql`.

En la Fase 4 (repartidores en moto, contraseña de un cliente), la respuesta correcta es decir que esas tablas y columnas no existen en el esquema.
