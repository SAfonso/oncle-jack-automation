from urllib.parse import urlsplit

_HOSTS_VALIDOS = {"canva.link", "canva.com", "www.canva.com"}


def validate_foto_url(valor: str | None, fecha: str, posicion: int, columna: str) -> str:
    texto = valor.strip() if isinstance(valor, str) else ""
    try:
        partes = urlsplit(texto)
        valido = (
            partes.scheme == "https"
            and partes.username is None
            and partes.password is None
            and partes.hostname in _HOSTS_VALIDOS
        )
    except ValueError:
        valido = False
    if not valido:
        raise ValueError(
            f"foto_url invalida en evento {fecha}, comico {posicion}, "
            f"columna {columna}: {valor!r} (se espera https con host canva.link o canva.com)"
        )
    return texto
