#!/usr/bin/env python3
"""
Servidor MCP personalizado construido con FastMCP
Nombre del Servidor: ServidorDomiciliosMCP
Taller MCP - Semana 07
"""

from typing import Annotated
from pydantic import Field
from mcp.server.fastmcp import FastMCP

# Instancia del servidor FastMCP con el nombre 'ServidorDomiciliosMCP'
mcp = FastMCP("ServidorDomiciliosMCP")

@mcp.tool(
    description="Calcula el porcentaje de descuento y el monto final a pagar para un cliente según el valor del pedido y su antigüedad en meses."
)
def calcular_descuento_cliente(
    monto_total: Annotated[float, Field(description="Monto total original del pedido o compra en COP (debe ser mayor a 0).", gt=0)],
    antiguedad_meses: Annotated[int, Field(description="Antigüedad del cliente registrada en la plataforma en meses (>= 0).", ge=0)]
) -> str:
    """Calcula el descuento aplicable a un cliente basándose en el monto total y su antigüedad."""
    descuento_porcentaje = 0

    # Lógica de descuento por antigüedad
    if antiguedad_meses >= 12:
        descuento_porcentaje += 10
    elif antiguedad_meses >= 6:
        descuento_porcentaje += 5

    # Lógica de descuento por monto total
    if monto_total >= 200000:
        descuento_porcentaje += 10
    elif monto_total >= 100000:
        descuento_porcentaje += 5

    # Límite máximo de descuento del 25%
    descuento_porcentaje = min(descuento_porcentaje, 25)

    monto_descuento = (monto_total * descuento_porcentaje) / 100.0
    monto_final = monto_total - monto_descuento

    return (
        f"Monto Original: ${monto_total:,.2f} COP | "
        f"Antigüedad: {antiguedad_meses} meses | "
        f"Descuento Aplicado: {descuento_porcentaje}% (${monto_descuento:,.2f} COP) | "
        f"Monto Final a Pagar: ${monto_final:,.2f} COP"
    )

@mcp.tool(
    description="Consulta el estado de cobertura de entrega de domicilios para un barrio y ciudad específicos en Colombia."
)
def consultar_estado_cobertura(
    barrio: Annotated[str, Field(description="Nombre del barrio de entrega (ej. 'El Poblado', 'Chapinero', 'Laureles').")],
    ciudad: Annotated[str, Field(description="Nombre de la ciudad de entrega (ej. 'Medellín', 'Bogotá', 'Cali').")]
) -> str:
    """Verifica si un barrio y ciudad tienen cobertura de domicilios y retorna el servicio disponible."""
    coberturas = {
        "medellín": {
            "el poblado": "Cobertura Total - Entrega Express (20-30 min)",
            "laureles": "Cobertura Total - Entrega Standard (30-45 min)",
            "bello": "Cobertura Parcial - Entrega Programada (45-60 min)"
        },
        "bogotá": {
            "chapinero": "Cobertura Total - Entrega Express (20-30 min)",
            "usaquén": "Cobertura Total - Entrega Standard (30-45 min)",
            "suba": "Cobertura Parcial - Entrega Programada (45-60 min)"
        },
        "cali": {
            "granada": "Cobertura Total - Entrega Standard (30-45 min)",
            "san antonio": "Cobertura Total - Entrega Standard (30-45 min)"
        }
    }

    ciudad_clean = ciudad.strip().lower()
    barrio_clean = barrio.strip().lower()

    if ciudad_clean in coberturas:
        barrios_ciudad = coberturas[ciudad_clean]
        if barrio_clean in barrios_ciudad:
            return f"Estado de cobertura para {barrio.title()}, {ciudad.title()}: {barrios_ciudad[barrio_clean]}."
        else:
            return f"Estado de cobertura para {barrio.title()}, {ciudad.title()}: Cobertura Estándar disponible mediante aliados logísticos (60+ min)."
    else:
        return f"Estado de cobertura para {barrio.title()}, {ciudad.title()}: Sin cobertura directa de domicilios por el momento."

if __name__ == "__main__":
    # Ejecuta el servidor FastMCP usando transporte STDIO por defecto
    mcp.run()
