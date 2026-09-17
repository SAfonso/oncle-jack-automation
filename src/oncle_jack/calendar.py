from oncle_jack.models import CalendarEntry, Event


def resolve_sabor(calendario: list[CalendarEntry], eventos: list[Event], mes: str) -> str:
    evento = next((e for e in eventos if e.mes == mes), None)
    if evento is not None and evento.sabor_override:
        return evento.sabor_override

    entry = next((c for c in calendario if c.mes == mes), None)
    if entry is None:
        raise KeyError(f"mes desconocido en Calendario_Sabores: {mes!r}")
    return entry.sabor


def apply_override_swap(
    calendario: list[CalendarEntry], mes: str, sabor_pedido: str
) -> list[CalendarEntry]:
    entry_mes = next((c for c in calendario if c.mes == mes), None)
    if entry_mes is None:
        raise KeyError(f"mes desconocido en Calendario_Sabores: {mes!r}")

    if entry_mes.sabor == sabor_pedido:
        return list(calendario)

    entry_sabor = next((c for c in calendario if c.sabor == sabor_pedido), None)
    if entry_sabor is None:
        raise ValueError(
            f"sabor desconocido: {sabor_pedido!r} no está asignado a ningún mes del calendario"
        )

    if entry_mes.fijo:
        raise ValueError(f"{mes} es un mes fijo, no se puede reasignar su sabor")
    if entry_sabor.fijo:
        raise ValueError(
            f"{entry_sabor.mes} es un mes fijo, no se puede mover de ahí el sabor {sabor_pedido!r}"
        )

    sabor_original_mes = entry_mes.sabor
    nuevo_calendario = []
    for c in calendario:
        if c.mes == mes:
            nuevo_calendario.append(CalendarEntry(mes=c.mes, sabor=sabor_pedido, fijo=c.fijo))
        elif c.mes == entry_sabor.mes:
            nuevo_calendario.append(
                CalendarEntry(mes=c.mes, sabor=sabor_original_mes, fijo=c.fijo)
            )
        else:
            nuevo_calendario.append(c)
    return nuevo_calendario
