import datetime

import pytest

from oncle_jack.calendar import mes_objetivo
from oncle_jack.models import Comico, Event


def _ev(y, m, d, estado="Pendiente"):
    return Event(
        fecha=datetime.date(y, m, d),
        mes="x",
        lugar="L",
        mc_1="a",
        mc_2="b",
        comicos=[Comico(nombre=f"C{i}", foto_url=f"https://x/{i}") for i in range(4)],
        sabor_override=None,
        estado=estado,
    )


def _temporada(**estados):
    # claves: e10, e11, e12, e01 -> estado
    return [
        _ev(2026, 10, 4, estados.get("e10", "Pendiente")),
        _ev(2026, 11, 15, estados.get("e11", "Pendiente")),
        _ev(2026, 12, 13, estados.get("e12", "Pendiente")),
        _ev(2027, 1, 10, estados.get("e01", "Pendiente")),
    ]


def test_mes_actual_pendiente():
    evs = _temporada()
    assert mes_objetivo(evs, datetime.date(2026, 10, 20)) is evs[0]


def test_mes_actual_generado_pasa_al_siguiente():
    evs = _temporada(e10="Generado")
    assert mes_objetivo(evs, datetime.date(2026, 10, 1)) is evs[1]


def test_sin_evento_en_mes_actual_devuelve_siguiente():
    evs = _temporada()
    assert mes_objetivo(evs, datetime.date(2026, 9, 26)) is evs[0]


def test_cadena_de_generados():
    evs = _temporada(e10="Generado", e11="Generado")
    assert mes_objetivo(evs, datetime.date(2026, 10, 5)) is evs[2]


def test_cruce_de_anio():
    evs = _temporada(e12="Generado")
    assert mes_objetivo(evs, datetime.date(2026, 12, 20)) is evs[3]


def test_estado_vacio_o_none_no_es_generado():
    for estado in ("", None):
        evs = _temporada(e10=estado)
        assert mes_objetivo(evs, datetime.date(2026, 10, 5)) is evs[0]


def test_eventos_anteriores_se_ignoran():
    evs = _temporada()
    assert mes_objetivo(evs, datetime.date(2026, 11, 1)) is evs[1]


def test_mismo_mes_otro_anio_no_casa():
    evs = [_ev(2026, 10, 4), _ev(2026, 11, 15)]
    with pytest.raises(ValueError):
        mes_objetivo(evs, datetime.date(2027, 10, 4))


def test_ninguno_disponible():
    evs = _temporada(e10="Generado", e11="Generado", e12="Generado", e01="Generado")
    with pytest.raises(ValueError, match="Generado"):
        mes_objetivo(evs, datetime.date(2026, 9, 26))


def test_lista_vacia():
    with pytest.raises(ValueError):
        mes_objetivo([], datetime.date(2026, 9, 26))
