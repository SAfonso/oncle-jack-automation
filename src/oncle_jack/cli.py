import json
import os
from pathlib import Path

import click

from oncle_jack.calendar import apply_override_swap, resolve_sabor
from oncle_jack.excel_source import load_workbook, mark_generated, save_calendar
from oncle_jack.foto_url import validate_evento_objetivo
from oncle_jack.models import Event
from oncle_jack.reveal import reveal_state


def _excel_path_from_env() -> str | None:
    if "EXCEL_PATH" in os.environ:
        return os.environ["EXCEL_PATH"]
    env_file = Path(".env")
    if env_file.exists():
        for linea in env_file.read_text().splitlines():
            linea = linea.strip()
            if linea.startswith("EXCEL_PATH="):
                return linea.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def _resolver_ruta_excel(excel: str | None) -> str:
    ruta = excel or _excel_path_from_env()
    if not ruta:
        raise click.UsageError(
            "Falta la ruta al Excel: pásala con --excel o define EXCEL_PATH en .env"
        )
    return ruta


def _normalizar_mes(mes: str) -> str:
    return mes.strip().capitalize()


def _buscar_evento(eventos: list[Event], mes: str) -> Event:
    evento = next((e for e in eventos if e.mes == mes), None)
    if evento is None:
        raise click.ClickException(f"no hay ningún evento en 'Eventos' para el mes {mes!r}")
    return evento


def _evento_a_dict(evento: Event) -> dict:
    return {
        "fecha": evento.fecha.strftime("%d/%m/%Y"),
        "lugar": evento.lugar,
        "mc_1": evento.mc_1,
        "mc_2": evento.mc_2,
        "comicos": [{"nombre": c.nombre, "foto_url": c.foto_url} for c in evento.comicos],
    }


@click.group()
def cli():
    pass


@cli.command()
@click.option("--month", "mes", required=True, help="Mes a resolver, p. ej. Noviembre")
@click.option("--override", default=None, help="Fuerza este sabor e intercambia en el calendario")
@click.option("--excel", default=None, help="Ruta al .xlsx local (o define EXCEL_PATH en .env)")
def resolve(mes: str, override: str | None, excel: str | None):
    mes = _normalizar_mes(mes)
    ruta = _resolver_ruta_excel(excel)
    try:
        calendario, eventos = load_workbook(ruta)
        evento = _buscar_evento(eventos, mes)
        validate_evento_objetivo(evento)
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc

    if override:
        try:
            calendario = apply_override_swap(calendario, mes, override)
        except ValueError as exc:
            raise click.ClickException(str(exc)) from exc
        save_calendar(ruta, calendario)
        sabor = override
    else:
        sabor = resolve_sabor(calendario, eventos, mes)

    resultado = {
        "mes": mes,
        "sabor": sabor,
        "carpeta_plantilla": f"Plantillas/{sabor}",
        "evento": _evento_a_dict(evento),
    }
    click.echo(json.dumps(resultado, ensure_ascii=False, indent=2))


@cli.command()
@click.option("--step", required=True, type=int, help="Paso de revelado (1-4)")
def reveal(step: int):
    try:
        estado = reveal_state(step)
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc

    resultado = {
        "step": estado.step,
        "visible_positions": estado.visible_positions,
        "hidden_positions": estado.hidden_positions,
    }
    click.echo(json.dumps(resultado, ensure_ascii=False))


@cli.command(name="mark-generated")
@click.option("--month", "mes", required=True, help="Mes cuyo evento marcar como Generado")
@click.option("--excel", default=None, help="Ruta al .xlsx local (o define EXCEL_PATH en .env)")
def mark_generated_cmd(mes: str, excel: str | None):
    mes = _normalizar_mes(mes)
    ruta = _resolver_ruta_excel(excel)
    try:
        _, eventos = load_workbook(ruta)
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc
    evento = _buscar_evento(eventos, mes)

    mark_generated(ruta, evento)

    resultado = {"mes": mes, "fecha": evento.fecha.strftime("%d/%m/%Y"), "estado": "Generado"}
    click.echo(json.dumps(resultado, ensure_ascii=False))
