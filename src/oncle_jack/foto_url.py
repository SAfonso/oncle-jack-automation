from urllib.parse import urlsplit

from oncle_jack.models import Event

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


def validate_evento_objetivo(evento: Event) -> Event:
    """Valida el evento objetivo: 4 fotos Canva válidas y 4 nombres no vacíos.

    Args:
        evento: Event con 4 cómicos

    Returns:
        evento si es válido

    Raises:
        ValueError si algún nombre está vacío/solo espacios o alguna foto es inválida.
                   Incluye fecha (dd/mm/yyyy), posición (1-4) y columna.
    """
    fecha_str = evento.fecha.strftime("%d/%m/%Y")

    # Validar nombres no vacíos
    for posicion, comico in enumerate(evento.comicos, start=1):
        if not (comico.nombre or "").strip():
            raise ValueError(
                f"nombre vacío en evento {fecha_str}, comico {posicion}, "
                f"columna Comico_{posicion}_Nombre"
            )

    # Validar fotos (reutiliza validate_foto_url)
    for posicion, comico in enumerate(evento.comicos, start=1):
        validate_foto_url(
            comico.foto_url,
            fecha_str,
            posicion,
            f"Comico_{posicion}_Foto_URL",
        )

    return evento
