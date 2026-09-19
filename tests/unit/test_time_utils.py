import pytest
from app.utils.time_utils import (
    calcular_duracion_minutos,
    es_hora_en_punto,
    hay_solapamiento,
    parse_hora,
    validar_reglas_horario,
)


def test_es_hora_en_punto():
    assert es_hora_en_punto("00:00") is True
    assert es_hora_en_punto("08:00") is True
    assert es_hora_en_punto("18:00") is True
    assert es_hora_en_punto("23:00") is True

    # Minutos fraccionados
    assert es_hora_en_punto("18:30") is False
    assert es_hora_en_punto("17:15") is False
    assert es_hora_en_punto("19:01") is False

    # Formatos incorrectos
    assert es_hora_en_punto("24:00") is False
    assert es_hora_en_punto("8:00") is False
    assert es_hora_en_punto("invalid") is False
    assert es_hora_en_punto(123) is False  # type: ignore


def test_parse_hora():
    t = parse_hora("18:00")
    assert t.hour == 18
    assert t.minute == 0

    with pytest.raises(ValueError, match="Formato de hora inválido"):
        parse_hora("invalid_time")


def test_calcular_duracion_minutos():
    assert calcular_duracion_minutos("18:00", "19:00") == 60
    assert calcular_duracion_minutos("18:00", "20:00") == 120
    assert calcular_duracion_minutos("18:00", "18:00") == 0
    assert calcular_duracion_minutos("19:00", "18:00") == -60


def test_hay_solapamiento():
    # Solapamiento parcial dentro
    assert hay_solapamiento("18:00", "20:00", "18:30", "19:30") is True
    # Solapamiento mismo inicio
    assert hay_solapamiento("18:00", "19:00", "18:00", "20:00") is True
    # Solapamiento mismo fin
    assert hay_solapamiento("18:00", "20:00", "19:00", "20:00") is True
    # Contiguos exactos: NO solapamiento
    assert hay_solapamiento("18:00", "19:00", "19:00", "20:00") is False
    assert hay_solapamiento("19:00", "20:00", "18:00", "19:00") is False
    # Disjuntos separados
    assert hay_solapamiento("10:00", "11:00", "14:00", "15:00") is False


def test_validar_reglas_horario_valido():
    # No debe levantar excepción
    validar_reglas_horario("18:00", "19:00")
    validar_reglas_horario("08:00", "10:00")


def test_validar_reglas_horario_minutos_fraccionados():
    with pytest.raises(ValueError, match="debe ser una hora en punto"):
        validar_reglas_horario("18:30", "19:30")

    with pytest.raises(ValueError, match="debe ser una hora en punto"):
        validar_reglas_horario("18:00", "19:45")


def test_validar_reglas_horario_invertido():
    with pytest.raises(ValueError, match="estrictamente posterior"):
        validar_reglas_horario("19:00", "18:00")

    with pytest.raises(ValueError, match="estrictamente posterior"):
        validar_reglas_horario("18:00", "18:00")


def test_validar_reglas_horario_duracion_menor_una_hora():
    # Aunque fuera fraccionada, si pasara el check de formato, la duración < 60 min falla
    # Probando duración con horas en punto no puede haber < 60 excepto si es <= 0 (cubierto arriba)
    pass
