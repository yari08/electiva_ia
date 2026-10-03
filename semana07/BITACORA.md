# Bitácora · Taller Semana 07 (MCP)

Registro de cómo se hizo el taller, para poder retomarlo o explicarlo. Fecha: 3 de octubre de 2026.

## Dónde está cada cosa

| Qué | Dónde |
|---|---|
| Código y evidencias | GitHub `yari08/electiva_ia`, carpeta `semana07/` |
| Copia local | `Downloads/checkpoint_semana07 (1)/semana07/` (sin `evidencias_fases_1_4.txt`: bajarlo de GitHub) |
| Base de datos | Supabase, proyecto `domicilios` (São Paulo), tablas `clientes` y `pedidos` en la base `postgres` |
| Entorno de ejecución | GitHub Codespace (Python, Node y Claude Code). En el PC no se instaló nada |

## Pasos que se siguieron

1. **Código del taller.** Se tomó el código de la página, no el del zip `checkpoint_semana07 (1)`, porque el zip trae otras tablas, otros datos y otras reglas de descuento. Se subió a `semana07/descargas/`.
2. **Base en Supabase** (plan B del taller, sin Docker). Se ejecutó `init_db.sql` en el SQL Editor con *Run and enable RLS*. Quedaron 4 clientes y 6 pedidos, y las consultas de las Fases 2 y 3 se verificaron ahí.
3. **Codespace.** Se instaló `requirements.txt` y `probador_mcp_local.py` pasó 7/7 casos.
4. **Conexión a Supabase desde el Codespace:**
   - Hay que usar el **Session pooler** (`aws-0-sa-east-1.pooler.supabase.com:5432`), porque la conexión directa solo funciona por IPv6.
   - Hay que darle a Node la CA de Supabase (*Database → Settings → SSL configuration → Download certificate*) y usar `sslmode=verify-full&sslrootcert=...`. Con `sslmode=require` falla con `self-signed certificate in certificate chain`.
   - La contraseña se escribe a mano en la terminal (`read -s`) y nunca se guarda en el repo.
   - Con esto `cliente_mcp_postgres.py` funcionó.
5. **Fases 1 a 4 en vivo.** Se instaló Claude Code en el Codespace, se inició sesión con `/login` (usando `BROWSER=true claude` para que muestre el código en vez de redirigir a `localhost`) y se lanzó desde `semana07/` con el `.mcp.json`. Las preguntas del taller se le hicieron al agente y la conversación se exportó con `/export` a `evidencias_fases_1_4.txt`.

## Correcciones respecto a la página

- **Servidor:** `"chaperino"` no coincidía con Chapinero, y `"Bogotá"` con tilde no se reconocía. Se arregló con normalización de tildes.
- **Servidor de Postgres:** la versión actual de `@modelcontextprotocol/server-postgres` solo expone `query`, no `get_schema`. El cliente lee el esquema con `query`.
- **Resultados de la página:** algunos están mal calculados. Con sus propios datos:
  - ENTREGADO suma 321.000 (63,44 %).
  - CANCELADO suma 150.000 (29,64 %).
  - El promedio por pedido de Bogotá es 105.000.
- **Probador:** `sys.exit()` dentro de los `async with` generaba un traceback. Se movió afuera.

## Pendiente o abierto

- **Resiliencia ante HTTP 429:** está en los objetivos, pero la página no pide ejercicio. No se implementó.
- **Evidencias sin revisar:** las preguntas 1-2 de la Fase 2, las 1-2 de la Fase 3 y el caso de 120.000 COP están en `evidencias_fases_1_4.txt` pero no se compararon contra lo esperado.
- **Limpieza:** borrar el Codespace *psychic dollop* (tiene la sesión de Claude Code iniciada).
