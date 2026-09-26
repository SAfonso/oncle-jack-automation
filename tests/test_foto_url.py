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
