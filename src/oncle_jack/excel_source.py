from pathlib import Path

import openpyxl

from oncle_jack.models import CalendarEntry, Comico, Event

_MESES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
]

_COL_ESTADO = 14  # columna "Estado" en la hoja Eventos (1-indexada)


def _mes_de_fecha(fecha: str) -> str:
    _dia, mes, _anio = fecha.split("/")
    return _MESES[int(mes) - 1]


def load_workbook(path: str | Path) -> tuple[list[CalendarEntry], list[Event]]:
    wb = openpyxl.load_workbook(path, data_only=True)

    calendario = []
    for mes, sabor, tipo in wb["Calendario_Sabores"].iter_rows(min_row=2, values_only=True):
        if mes is None:
            continue
        calendario.append(CalendarEntry(mes=mes, sabor=sabor, fijo=bool(tipo and "Fijo" in tipo)))

    eventos = []
    for row in wb["Eventos"].iter_rows(min_row=2, values_only=True):
        fecha = row[0]
        if fecha is None:
            continue
        (
            fecha, lugar, mc_1, mc_2,
            c1_nombre, c1_foto, c2_nombre, c2_foto,
            c3_nombre, c3_foto, c4_nombre, c4_foto,
            sabor_override, estado, _notas,
        ) = row[:15]
        comicos = [
            Comico(nombre=c1_nombre, foto_url=c1_foto),
            Comico(nombre=c2_nombre, foto_url=c2_foto),
            Comico(nombre=c3_nombre, foto_url=c3_foto),
            Comico(nombre=c4_nombre, foto_url=c4_foto),
        ]
        eventos.append(
            Event(
                fecha=fecha,
                mes=_mes_de_fecha(fecha),
                lugar=lugar,
                mc_1=mc_1,
                mc_2=mc_2,
                comicos=comicos,
                sabor_override=sabor_override,
                estado=estado,
            )
        )

    return calendario, eventos


def save_calendar(path: str | Path, calendario: list[CalendarEntry]) -> None:
    wb = openpyxl.load_workbook(path)
    ws = wb["Calendario_Sabores"]
    por_mes = {entry.mes: entry for entry in calendario}
    for row in ws.iter_rows(min_row=2):
        mes_cell, sabor_cell = row[0], row[1]
        entry = por_mes.get(mes_cell.value)
        if entry is not None:
            sabor_cell.value = entry.sabor
    wb.save(path)


def mark_generated(path: str | Path, evento: Event) -> None:
    wb = openpyxl.load_workbook(path)
    ws = wb["Eventos"]
    for row in ws.iter_rows(min_row=2):
        if row[0].value == evento.fecha:
            ws.cell(row=row[0].row, column=_COL_ESTADO, value="Generado")
            break
    wb.save(path)
