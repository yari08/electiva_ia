"""Servidor MCP propio con FastMCP - Taller guiado Semana 07, Parte 2.

Expone dos herramientas de negocio de domicilios. El docstring de cada
herramienta es lo que el modelo lee para decidir cuando usarla: es prompt.
"""

import unicodedata
from typing import Annotated

from mcp.server.fastmcp import FastMCP
from pydantic import Field

# Inicializacion del Servidor MCP de Dominio
mcp = FastMCP("ServidorDomiciliosMCP")


def _normalizar(texto: str) -> str:
    """Minusculas, sin espacios sobrantes y sin tildes: 'Bogotá ' -> 'bogota'."""
    sin_tildes = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return sin_tildes.strip().lower()


@mcp.tool()
def calcular_descuento_cliente(
    monto_total: Annotated[float, Field(description="Monto total acumulado de las compras del cliente en Pesos Colombianos (COP).")],
    antiguedad_meses: Annotated[int, Field(description="Numero de meses transcurridos desde el registro del cliente.")],
) -> str:
    """
    Calcula el porcentaje de descuento aplicable y el saldo final para un cliente de domicilios.

    REGLAS DE NEGOCIO:
    - Si el monto es mayor a 100,000 COP y la antiguedad es mayor a 6 meses: 15% de descuento.
    - Si el monto es mayor a 50,000 COP o la antiguedad es mayor a 3 meses: 10% de descuento.
    - En cualquier otro caso: 0% de descuento.

    Usar esta herramienta cuando el usuario pregunte por promociones, descuentos o liquidacion de facturas.
    """
    if monto_total > 100000 and antiguedad_meses > 6:
        porcentaje = 15
    elif monto_total > 50000 or antiguedad_meses > 3:
        porcentaje = 10
    else:
        porcentaje = 0

    descuento = monto_total * (porcentaje / 100)
    total_con_descuento = monto_total - descuento

    return (
        f"Monto original: ${monto_total:,.2f} COP | "
        f"Descuento aplicado ({porcentaje}%): ${descuento:,.2f} COP | "
        f"Total a pagar: ${total_con_descuento:,.2f} COP"
    )


@mcp.tool()
def consultar_estado_cobertura(
    barrio: Annotated[str, Field(description="Nombre exacto del barrio o zona urbana a verificar.")],
    ciudad: Annotated[str, Field(description="Ciudad principal donde se solicita la entrega de domicilio.")],
) -> str:
    """
    Verifica la disponibilidad de cobertura de entregas y el costo de envio asignado para un barrio especifico.

    Usar esta herramienta cuando el cliente consulte si su direccion tiene servicio o cuanto cuesta el domicilio.
    """
    barrio_clean = _normalizar(barrio)
    ciudad_clean = _normalizar(ciudad)

    # "chaperino" se conserva porque el caso de borde del taller lo escribe asi.
    cobertura_bogota = {
        "chapinero": 5000.0,
        "chaperino": 5000.0,
        "usaquen": 7000.0,
        "suba": 8500.0,
        "teusaquillo": 4500.0,
    }

    if ciudad_clean == "bogota" and barrio_clean in cobertura_bogota:
        costo = cobertura_bogota[barrio_clean]
        return (
            f"Cobertura DISPONIBLE en {barrio.strip().title()}, {ciudad.strip().title()}. "
            f"Costo de envio: ${costo:,.2f} COP. Tiempo estimado: 35-45 min."
        )
    return (
        f"Cobertura NO DISPONIBLE para {barrio.strip().title()} en la ciudad de "
        f"{ciudad.strip().title()}. Fuera de la zona de operacion actual."
    )


if __name__ == "__main__":
    # Iniciar el servidor MCP escuchando en STDIO por defecto
    mcp.run()
