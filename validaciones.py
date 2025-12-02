"""
Funciones de validación para entradas del sistema.
Incluye validación de email, campos obligatorios, formato de fecha y horas.
"""
import re
from datetime import datetime


def validar_email(email: str) -> bool:
    """Valida que el email tenga formato correcto.

    Retorna True si el formato es válido, False en caso contrario.
    """
    if not email:
        return False
    patron = r"^[\w\.-]+@[\w\.-]+\.\w{2,}$"
    return re.match(patron, email) is not None


def validar_no_vacio(valor: str) -> bool:
    """Valida que el campo no esté vacío (ni solo espacios)."""
    return bool(valor and valor.strip())


def validar_fecha_iso(fecha: str) -> bool:
    """Valida que la fecha esté en formato YYYY-MM-DD."""
    try:
        datetime.strptime(fecha, "%Y-%m-%d")
        return True
    except Exception:
        return False


def validar_horas(horas) -> bool:
    """Valida que las horas sean un número positivo (y razonable, p.ej <= 24)."""
    try:
        h = float(horas)
        return 0 < h <= 24
    except Exception:
        return False
