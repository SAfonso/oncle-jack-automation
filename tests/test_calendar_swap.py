import pytest

from oncle_jack.calendar import apply_override_swap
from oncle_jack.models import CalendarEntry


def _calendario():
    return [
        CalendarEntry(mes="Octubre", sabor="Original", fijo=True),
        CalendarEntry(mes="Noviembre", sabor="RIE", fijo=False),
        CalendarEntry(mes="Diciembre", sabor="Winter", fijo=True),
        CalendarEntry(mes="Marzo", sabor="Blue", fijo=False),
    ]


def _sabor(calendario, mes):
    return next(c.sabor for c in calendario if c.mes == mes)


def test_swap_normal_intercambia_los_dos_meses():
    calendario = _calendario()

    nuevo = apply_override_swap(calendario, "Noviembre", "Blue")

    assert _sabor(nuevo, "Noviembre") == "Blue"
    assert _sabor(nuevo, "Marzo") == "RIE"
    # no muta el calendario original
    assert _sabor(calendario, "Noviembre") == "RIE"
    assert _sabor(calendario, "Marzo") == "Blue"


def test_swap_idempotente_si_el_mes_ya_tiene_ese_sabor():
    calendario = _calendario()

    nuevo = apply_override_swap(calendario, "Noviembre", "RIE")

    assert nuevo == calendario


def test_swap_sabor_desconocido_lanza_value_error():
    calendario = _calendario()

    with pytest.raises(ValueError):
        apply_override_swap(calendario, "Noviembre", "Apple")


def test_swap_mes_destino_fijo_lanza_value_error():
    calendario = _calendario()

    with pytest.raises(ValueError):
        apply_override_swap(calendario, "Octubre", "Blue")


def test_swap_sabor_pedido_esta_en_mes_fijo_lanza_value_error():
    calendario = _calendario()

    with pytest.raises(ValueError):
        apply_override_swap(calendario, "Noviembre", "Original")
