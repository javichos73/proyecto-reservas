import re
from datetime import datetime, time

TIME_EXACT_HOUR_PATTERN = re.compile(r"^([01]\d|2[0-3]):00$")


def es_hora_en_punto(hora_str: str) -> bool:
    """Verifica si la hora tiene formato estricto HH:00 (horas en punto)."""
    if not isinstance(hora_str, str):
        return False
    return bool(TIME_EXACT_HOUR_PATTERN.match(hora_str))


def parse_hora(hora_str: str) -> time:
    """Convierte un string HH:MM a objeto time. Lanza ValueError si el formato es inválido."""
    try:
        dt = datetime.strptime(hora_str, "%H:%M")
        return dt.time()
    except Exception as e:
        raise ValueError(f"Formato de hora inválido: {hora_str}. Se esperaba HH:MM") from e


def calcular_duracion_minutos(hora_inicio_str: str, hora_fin_str: str) -> int:
    """Calcula la duración en minutos entre dos horas en formato HH:MM dentro del mismo día."""
    t_inicio = parse_hora(hora_inicio_str)
    t_fin = parse_hora(hora_fin_str)

    minutos_inicio = t_inicio.hour * 60 + t_inicio.minute
    minutos_fin = t_fin.hour * 60 + t_fin.minute

    return minutos_fin - minutos_inicio


def hay_solapamiento(
    inicio1_str: str, fin1_str: str, inicio2_str: str, fin2_str: str
) -> bool:
    """
    Determina si dos intervalos de tiempo se solapan dentro del mismo día.
    Los intervalos contiguos (ej. 18:00-19:00 y 19:00-20:00) NO se solapan.
    Fórmula: inicio1 < fin2 AND fin1 > inicio2
    """
    return (inicio1_str < fin2_str) and (fin1_str > inicio2_str)


def validar_reglas_horario(hora_inicio_str: str, hora_fin_str: str) -> None:
    """
    Valida las reglas de negocio para los horarios de reserva:
    1. Deben ser horas en punto exactas (:00).
    2. hora_fin debe ser estrictamente posterior a hora_inicio.
    3. Duración mínima de 1 hora (60 minutos).
    Lanza ValueError con mensaje descriptivo si alguna regla se viola.
    """
    if not es_hora_en_punto(hora_inicio_str):
        raise ValueError(
            f"La hora de inicio '{hora_inicio_str}' debe ser una hora en punto (minutos :00)."
        )

    if not es_hora_en_punto(hora_fin_str):
        raise ValueError(
            f"La hora de fin '{hora_fin_str}' debe ser una hora en punto (minutos :00)."
        )

    duracion = calcular_duracion_minutos(hora_inicio_str, hora_fin_str)

    if duracion <= 0:
        raise ValueError(
            f"La hora de fin ({hora_fin_str}) debe ser estrictamente posterior a la hora de inicio ({hora_inicio_str})."
        )

    if duracion < 60:
        raise ValueError(
            f"La duración mínima de una reserva es de 1 hora (60 minutos). Duración solicitada: {duracion} minutos."
        )
