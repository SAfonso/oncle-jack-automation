from oncle_jack.models import CalendarEntry, Event


def resolve_sabor(calendario: list[CalendarEntry], eventos: list[Event], mes: str) -> str:
    evento = next((e for e in eventos if e.mes == mes), None)
    if evento is not None and evento.sabor_override:
        return evento.sabor_override

    entry = next((c for c in calendario if c.mes == mes), None)
    if entry is None:
        raise KeyError(f"mes desconocido en Calendario_Sabores: {mes!r}")
    return entry.sabor
