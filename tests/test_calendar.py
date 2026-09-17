import pytest

from oncle_jack.calendar import resolve_sabor
from oncle_jack.models import CalendarEntry, Comico, Event


def _comicos():
    return [Comico(nombre=f"Cómico {i}", foto_url=f"https://x/{i}") for i in range(1, 5)]


def _calendario():
    return [
        CalendarEntry(mes="Octubre", sabor="Original", fijo=True),
        CalendarEntry(mes="Noviembre", sabor="RIE", fijo=False),
        CalendarEntry(mes="Diciembre", sabor="Winter", fijo=True),
        CalendarEntry(mes="Marzo", sabor="Blue", fijo=False),
    ]


def _evento(mes, sabor_override=None):
    return Event(
        fecha="14/11/2026",
        mes=mes,
        lugar="Carrer de les Roselles, 32",
        mc_1="Mercè Copado",
        mc_2="Sergio Afonso",
        comicos=_comicos(),
        sabor_override=sabor_override,
        estado="Pendiente",
    )


def test_usa_el_override_del_evento_si_esta_relleno():
    calendario = _calendario()
    eventos = [_evento("Noviembre", sabor_override="Blue")]

    sabor = resolve_sabor(calendario, eventos, "Noviembre")

    assert sabor == "Blue"
    # no toca el calendario
    assert [c.sabor for c in calendario if c.mes == "Noviembre"] == ["RIE"]


def test_usa_el_calendario_si_no_hay_override():
    calendario = _calendario()
    eventos = [_evento("Noviembre")]

    sabor = resolve_sabor(calendario, eventos, "Noviembre")

    assert sabor == "RIE"


def test_mes_desconocido_lanza_key_error():
    calendario = _calendario()
    eventos = [_evento("Julio")]

    with pytest.raises(KeyError):
        resolve_sabor(calendario, eventos, "Julio")
