"""Probador local del servidor FastMCP propio por STDIO.

Ejecuta tools/list y luego tools/call con los casos positivos, negativos y de
borde del taller, comparando cada respuesta con lo esperado.
    python probador_mcp_local.py
"""

import asyncio
import os
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVIDOR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "servidor_mcp.py")

# (herramienta, argumentos, texto que debe aparecer en la respuesta)
CASOS = [
    ("calcular_descuento_cliente", {"monto_total": 120000.0, "antiguedad_meses": 8}, "(15%)"),
    ("calcular_descuento_cliente", {"monto_total": 40000.0, "antiguedad_meses": 4}, "(10%)"),
    ("calcular_descuento_cliente", {"monto_total": 30000.0, "antiguedad_meses": 1}, "(0%)"),
    ("calcular_descuento_cliente", {"monto_total": 100000.0, "antiguedad_meses": 6}, "(10%)"),
    ("consultar_estado_cobertura", {"barrio": "Chapinero", "ciudad": "Bogotá"}, "DISPONIBLE"),
    ("consultar_estado_cobertura", {"barrio": "El Poblado", "ciudad": "Medellín"}, "NO DISPONIBLE"),
    ("consultar_estado_cobertura", {"barrio": "  chApeRino ", "ciudad": "BOGOTA"}, "DISPONIBLE"),
]


async def main():
    params = StdioServerParameters(command=sys.executable, args=[SERVIDOR])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            herramientas = await session.list_tools()
            print(f"tools/list -> {[t.name for t in herramientas.tools]}\n")

            fallos = 0
            for nombre, args, esperado in CASOS:
                res = await session.call_tool(nombre, args)
                texto = " ".join(c.text for c in res.content)
                # "DISPONIBLE" tambien esta dentro de "NO DISPONIBLE"
                ok = esperado in texto and not (
                    esperado == "DISPONIBLE" and "NO DISPONIBLE" in texto
                )
                fallos += not ok
                print(f"[{'OK ' if ok else 'FALLA'}] {nombre}({args})")
                print(f"        {texto}\n")

            print(f"{len(CASOS) - fallos}/{len(CASOS)} casos correctos")
            return fallos


if __name__ == "__main__":
    # sys.exit fuera de los async with: adentro, anyio lo envuelve en un traceback
    sys.exit(1 if asyncio.run(main()) else 0)
