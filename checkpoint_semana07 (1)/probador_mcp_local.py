#!/usr/bin/env python3
"""
Probador MCP Local para ServidorDomiciliosMCP
Permite probar herramientas del servidor FastMCP localmente mediante STDIO
sin requerir un cliente visual o Claude Desktop.
Taller MCP - Semana 07
"""

import asyncio
import os
import sys
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Ruta absoluta o relativa al servidor FastMCP
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SERVIDOR_PATH = os.path.join(SCRIPT_DIR, "servidor_mcp.py")

async def main():
    print("=" * 65)
    print("  PROBADOR MCP LOCAL - SERVIDOR DOMICILIOS (FASTMCP)")
    print("=" * 65)
    print(f"Iniciando subproceso STDIO para: {SERVIDOR_PATH}\n")

    # Configuración de los parámetros para lanzar el servidor Python vía STDIO
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[SERVIDOR_PATH]
    )

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # 1. Inicializar la sesión MCP
                print("1. Inicializando sesión MCP con el servidor...")
                await session.initialize()
                print("   ✔ Sesión inicializada correctamente.\n")

                # 2. Listar las herramientas expuestas por el servidor FastMCP
                print("2. Descubriendo herramientas expuestas (list_tools)...")
                tools_response = await session.list_tools()
                print(f"   Se encontraron {len(tools_response.tools)} herramienta(s):")
                for tool in tools_response.tools:
                    print(f"   - Herramienta: {tool.name}")
                    print(f"     Descripción: {tool.description}")
                    print(f"     Esquema: {json.dumps(tool.inputSchema, ensure_ascii=False)}\n")

                # 3. Invocar herramienta: calcular_descuento_cliente
                print("3. Probando la herramienta 'calcular_descuento_cliente'...")
                params_descuento = {
                    "monto_total": 150000.0,
                    "antiguedad_meses": 14
                }
                print(f"   Parámetros enviados: {params_descuento}")
                result_descuento = await session.call_tool("calcular_descuento_cliente", params_descuento)
                print("   [Resultado del Servidor]:")
                for content in result_descuento.content:
                    print(f"   {content.text}")
                print()

                # 4. Invocar herramienta: consultar_estado_cobertura (Caso con cobertura)
                print("4. Probando la herramienta 'consultar_estado_cobertura' (Caso 1: El Poblado, Medellín)...")
                params_cobertura_1 = {
                    "barrio": "El Poblado",
                    "ciudad": "Medellín"
                }
                print(f"   Parámetros enviados: {params_cobertura_1}")
                result_cobertura_1 = await session.call_tool("consultar_estado_cobertura", params_cobertura_1)
                print("   [Resultado del Servidor]:")
                for content in result_cobertura_1.content:
                    print(f"   {content.text}")
                print()

                # 5. Invocar herramienta: consultar_estado_cobertura (Caso 2: Suba, Bogotá)
                print("5. Probando la herramienta 'consultar_estado_cobertura' (Caso 2: Suba, Bogotá)...")
                params_cobertura_2 = {
                    "barrio": "Suba",
                    "ciudad": "Bogotá"
                }
                print(f"   Parámetros enviados: {params_cobertura_2}")
                result_cobertura_2 = await session.call_tool("consultar_estado_cobertura", params_cobertura_2)
                print("   [Resultado del Servidor]:")
                for content in result_cobertura_2.content:
                    print(f"   {content.text}")
                print()

                print("=" * 65)
                print("  PRUEBA LOCAL DEL SERVIDOR FASTMCP COMPLETADA EXITOSAMENTE")
                print("=" * 65)

    except Exception as e:
        print(f"\n❌ ERROR durante la ejecución de la prueba MCP local: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
