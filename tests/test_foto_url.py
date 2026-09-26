import pytest

from oncle_jack.foto_url import validate_foto_url


@pytest.mark.parametrize("url", [
    "https://canva.link/zyxvd0tfeqmde4l",
    "https://www.canva.com/design/DAF123/view",
    "https://canva.com/design/DAF123/view",
])
def test_urls_validas(url):
    assert validate_foto_url(url, "01/11/2026", 1, "Comico_1_Foto_URL") == url


def test_valida_devuelve_strip():
    assert validate_foto_url("  https://canva.link/abc \n", "01/11/2026", 1, "C") == "https://canva.link/abc"


@pytest.mark.parametrize("url", [
    "http://canva.link/abc",
    "https://canva.com.evil.com/abc",
    "https://canva.com@x.com/abc",
    "https://evil.com/canva.com",
    "https://drive.google.com/file/d/123/view",
    "canva.link/abc",
    "texto suelto",
    None,
    "",
    "   ",
])
def test_urls_invalidas(url):
    with pytest.raises(ValueError):
        validate_foto_url(url, "01/11/2026", 1, "Comico_1_Foto_URL")


def test_mensaje_incluye_contexto():
    with pytest.raises(ValueError) as exc:
        validate_foto_url("https://drive.google.com/x", "15/11/2026", 3, "Comico_3_Foto_URL")
    msg = str(exc.value)
    assert "15/11/2026" in msg
    assert "3" in msg
    assert "Comico_3_Foto_URL" in msg
    assert "https://drive.google.com/x" in msg


# Tests para validate_evento_objetivo
import datetime
from oncle_jack.models import Event, Comico
from oncle_jack.foto_url import validate_evento_objetivo


def test_evento_objetivo_valido():
    """Evento con 4 fotos canva válidas y 4 nombres no vacíos pasa."""
    evento = Event(
        fecha=datetime.date(2026, 11, 15),
        mes="Noviembre",
        lugar="Barcelona",
        mc_1="MC 1",
        mc_2="MC 2",
        comicos=[
            Comico("Cómico 1", "https://canva.link/abc1"),
            Comico("Cómico 2", "https://www.canva.com/design/DAF123/view"),
            Comico("Cómico 3", "https://canva.com/design/DAF456/view"),
            Comico("Cómico 4", "https://canva.link/def4"),
        ],
        sabor_override=None,
        estado="Pendiente",
    )
    resultado = validate_evento_objetivo(evento)
    assert resultado == evento


def test_evento_objetivo_nombre_vacio_posicion_1():
    """Nombre vacío en posición 1 → ValueError con posición y columna."""
    evento = Event(
        fecha=datetime.date(2026, 11, 15),
        mes="Noviembre",
        lugar="Barcelona",
        mc_1="MC 1",
        mc_2="MC 2",
        comicos=[
            Comico("", "https://canva.link/abc1"),
            Comico("Cómico 2", "https://canva.link/abc2"),
            Comico("Cómico 3", "https://canva.link/abc3"),
            Comico("Cómico 4", "https://canva.link/abc4"),
        ],
        sabor_override=None,
        estado="Pendiente",
    )
    with pytest.raises(ValueError) as exc:
        validate_evento_objetivo(evento)
    msg = str(exc.value)
    assert "15/11/2026" in msg
    assert "1" in msg
    assert "Comico_1_Nombre" in msg


def test_evento_objetivo_nombre_solo_espacios_posicion_2():
    """Nombre con solo espacios en posición 2 → ValueError."""
    evento = Event(
        fecha=datetime.date(2026, 11, 15),
        mes="Noviembre",
        lugar="Barcelona",
        mc_1="MC 1",
        mc_2="MC 2",
        comicos=[
            Comico("Cómico 1", "https://canva.link/abc1"),
            Comico("   ", "https://canva.link/abc2"),
            Comico("Cómico 3", "https://canva.link/abc3"),
            Comico("Cómico 4", "https://canva.link/abc4"),
        ],
        sabor_override=None,
        estado="Pendiente",
    )
    with pytest.raises(ValueError) as exc:
        validate_evento_objetivo(evento)
    msg = str(exc.value)
    assert "15/11/2026" in msg
    assert "2" in msg
    assert "Comico_2_Nombre" in msg


def test_evento_objetivo_nombre_vacio_posicion_3():
    """Nombre vacío en posición 3 → ValueError con posición y columna."""
    evento = Event(
        fecha=datetime.date(2026, 11, 15),
        mes="Noviembre",
        lugar="Barcelona",
        mc_1="MC 1",
        mc_2="MC 2",
        comicos=[
            Comico("Cómico 1", "https://canva.link/abc1"),
            Comico("Cómico 2", "https://canva.link/abc2"),
            Comico("", "https://canva.link/abc3"),
            Comico("Cómico 4", "https://canva.link/abc4"),
        ],
        sabor_override=None,
        estado="Pendiente",
    )
    with pytest.raises(ValueError) as exc:
        validate_evento_objetivo(evento)
    msg = str(exc.value)
    assert "15/11/2026" in msg
    assert "3" in msg
    assert "Comico_3_Nombre" in msg


def test_evento_objetivo_nombre_vacio_posicion_4():
    """Nombre vacío en posición 4 → ValueError con posición y columna."""
    evento = Event(
        fecha=datetime.date(2026, 11, 15),
        mes="Noviembre",
        lugar="Barcelona",
        mc_1="MC 1",
        mc_2="MC 2",
        comicos=[
            Comico("Cómico 1", "https://canva.link/abc1"),
            Comico("Cómico 2", "https://canva.link/abc2"),
            Comico("Cómico 3", "https://canva.link/abc3"),
            Comico("", "https://canva.link/abc4"),
        ],
        sabor_override=None,
        estado="Pendiente",
    )
    with pytest.raises(ValueError) as exc:
        validate_evento_objetivo(evento)
    msg = str(exc.value)
    assert "15/11/2026" in msg
    assert "4" in msg
    assert "Comico_4_Nombre" in msg


def test_evento_objetivo_foto_invalida_reutiliza_validate_foto_url():
    """Foto inválida en posición 1 → error desde validate_foto_url."""
    evento = Event(
        fecha=datetime.date(2026, 11, 15),
        mes="Noviembre",
        lugar="Barcelona",
        mc_1="MC 1",
        mc_2="MC 2",
        comicos=[
            Comico("Cómico 1", "https://drive.google.com/file/d/123/view"),
            Comico("Cómico 2", "https://canva.link/abc2"),
            Comico("Cómico 3", "https://canva.link/abc3"),
            Comico("Cómico 4", "https://canva.link/abc4"),
        ],
        sabor_override=None,
        estado="Pendiente",
    )
    with pytest.raises(ValueError) as exc:
        validate_evento_objetivo(evento)
    msg = str(exc.value)
    assert "15/11/2026" in msg
    assert "1" in msg
    assert "Comico_1_Foto_URL" in msg
    assert "https://drive.google.com/file/d/123/view" in msg


def test_evento_objetivo_foto_invalida_posicion_3():
    """Foto inválida en posición 3."""
    evento = Event(
        fecha=datetime.date(2026, 11, 15),
        mes="Noviembre",
        lugar="Barcelona",
        mc_1="MC 1",
        mc_2="MC 2",
        comicos=[
            Comico("Cómico 1", "https://canva.link/abc1"),
            Comico("Cómico 2", "https://canva.link/abc2"),
            Comico("Cómico 3", "http://canva.link/abc3"),
            Comico("Cómico 4", "https://canva.link/abc4"),
        ],
        sabor_override=None,
        estado="Pendiente",
    )
    with pytest.raises(ValueError) as exc:
        validate_evento_objetivo(evento)
    msg = str(exc.value)
    assert "15/11/2026" in msg
    assert "3" in msg
    assert "Comico_3_Foto_URL" in msg
