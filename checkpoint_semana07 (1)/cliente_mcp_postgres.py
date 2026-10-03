#!/usr/bin/env python3
"""
Cliente MCP en Python para servidor @modelcontextprotocol/server-postgres
Taller MCP - Semana 07
"""

import asyncio
import sys
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# URL de conexión a la base de datos PostgreSQL desplegada en Docker
DATABASE_URL = "postgresql://curso:curso@localhost:55432/domicilios"

async def main():
    print("=" * 60)
    print("  CLIENTE MCP - CONEXIÓN A POSTGRESQL (DOMICILIOS)")
    print("=" * 60)
    print(f"Conectando al servidor MCP de Postgres en {DATABASE_URL}...\n")

    # Configuración de los parámetros para lanzar el servidor vía npx
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-postgres", DATABASE_URL]
    )

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # 1. Inicializar la sesión con el servidor MCP
                print("1. Inicializando sesión MCP (initialize)...")
                await session.initialize()
                print("   ✔ Sesión inicializada correctamente.\n")

                # 2. Descubrir las herramientas expuestas por el servidor
                print("2. Descubriendo herramientas disponibles (list_tools)...")
                tools_response = await session.list_tools()
                print(f"   Se encontraron {len(tools_response.tools)} herramienta(s):")
                for tool in tools_response.tools:
                    print(f"   - Nombre: {tool.name}")
                    print(f"     Descripción: {tool.description}")
                    print(f"     Esquema de entrada: {json.dumps(tool.inputSchema, ensure_ascii=False)}\n")

                # 3. Obtener el esquema de la base de datos (get_schema / consulta de esquema)
                print("3. Obtención del esquema de la base de datos...")
                tool_names = [t.name for t in tools_response.tools]
                if "get_schema" in tool_names:
                    schema_result = await session.call_tool("get_schema", {})
                    print("   [Obtenido con herramienta 'get_schema']:")
                    for content in schema_result.content:
                        print(content.text)
                else:
                    # Alternativa estándar usando la herramienta 'query' para consultar el diccionario de datos
                    sql_schema = """
                    SELECT table_name, column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_schema = 'public' 
                    ORDER BY table_name, ordinal_position;
                    """
                    schema_result = await session.call_tool("query", {"sql": sql_schema})
                    print("   [Esquema obtenido desde information_schema vía 'query']:")
                    for content in schema_result.content:
                        print(content.text)
                print()

                # 4. Ejecutar una consulta SQL de prueba (query)
                print("4. Ejecutando consulta SQL de prueba (query)...")
                sql_prueba = """
                SELECT 
                    c.nombre AS cliente,
                    c.barrio,
                    c.ciudad,
                    COUNT(p.id) AS total_pedidos,
                    COALESCE(SUM(p.monto_total), 0) AS monto_total_acumulado
                FROM clientes c
                LEFT JOIN pedidos p ON c.id = p.cliente_id
                GROUP BY c.id, c.nombre, c.barrio, c.ciudad
                ORDER BY monto_total_acumulado DESC;
                """
                query_result = await session.call_tool("query", {"sql": sql_prueba})
                print("   [Resultado de la consulta SQL]:")
                for content in query_result.content:
                    print(content.text)

                print("\n" + "=" * 60)
                print("  EJECUCIÓN DEL CLIENTE MCP POSTGRES COMPLETADA CON ÉXITO")
                print("=" * 60)

    except Exception as e:
        print(f"\n❌ ERROR de ejecución en cliente MCP: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
