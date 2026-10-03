"""Cliente MCP en Python para el servidor oficial @modelcontextprotocol/server-postgres.

Taller guiado - Semana 07, Parte 1, Escenario B.

La cadena de conexion se lee de la variable DATABASE_URL para no subir
credenciales al repositorio. Sin ella, usa el Postgres local de Docker.
    Neon / Supabase:  DATABASE_URL="postgresql://usuario:clave@host/domicilios?sslmode=require"
"""

import asyncio
import os

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://curso:curso@localhost:55432/domicilios"
)


async def ejecutar_cliente_mcp():
    # Parametros para arrancar el servidor MCP de Postgres mediante STDIO
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-postgres", DATABASE_URL],
    )

    print("[MCP CLIENT] Conectando al servidor MCP PostgreSQL...")
    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            # Paso 1: Inicializacion del protocolo
            await session.initialize()
            print("[MCP CLIENT] Protocolo inicializado con exito.")

            # Paso 2: Descubrimiento de herramientas disponibles (tools/list)
            herramientas = await session.list_tools()
            nombres = [t.name for t in herramientas.tools]
            print(f"\n[MCP CLIENT] Herramientas descubiertas ({len(nombres)}):")
            for tool in herramientas.tools:
                print(f" - {tool.name}: {(tool.description or '')[:80]}...")

            # Paso 3: Esquema. Algunas versiones del servidor exponen get_schema;
            # otras solo exponen query y el esquema como recursos.
            print("\n[MCP CLIENT] Consultando el esquema...")
            if "get_schema" in nombres:
                esquema = await session.call_tool("get_schema", arguments={})
            else:
                esquema = await session.call_tool("query", arguments={"sql": (
                    "SELECT table_name, column_name, data_type "
                    "FROM information_schema.columns WHERE table_schema = 'public' "
                    "ORDER BY table_name, ordinal_position;"
                )})
            print("[MCP CLIENT] Resultado del esquema:")
            for item in esquema.content:
                print(item.text[:600])

            # Paso 4: Invocacion de la herramienta query
            consulta_sql = (
                "SELECT c.nombre, c.ciudad, SUM(p.monto) AS total_comprado "
                "FROM clientes c JOIN pedidos p ON c.id = p.cliente_id "
                "WHERE p.estado = 'ENTREGADO' "
                "GROUP BY c.id, c.nombre, c.ciudad ORDER BY total_comprado DESC;"
            )
            print(f"\n[MCP CLIENT] Ejecutando consulta SQL: {consulta_sql}")
            resultado = await session.call_tool("query", arguments={"sql": consulta_sql})
            print("[MCP CLIENT] Resultado de la consulta:")
            for item in resultado.content:
                print(item.text)


if __name__ == "__main__":
    asyncio.run(ejecutar_cliente_mcp())
