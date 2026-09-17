import json
import shutil
from pathlib import Path

import pytest
from click.testing import CliRunner

from oncle_jack.cli import cli
from oncle_jack.excel_source import load_workbook

FIXTURE = Path(__file__).parent / "fixtures" / "datos_ejemplo.xlsx"


@pytest.fixture
def excel_path(tmp_path):
    destino = tmp_path / "datos.xlsx"
    shutil.copy(FIXTURE, destino)
    return destino


@pytest.fixture
def runner():
    return CliRunner()


def test_resolve_sin_override_usa_el_calendario(runner, excel_path):
    result = runner.invoke(
        cli, ["resolve", "--month", "Noviembre", "--excel", str(excel_path)]
    )

    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["mes"] == "Noviembre"
    assert data["sabor"] == "RIE"
    assert data["carpeta_plantilla"] == "Plantillas/RIE"
    assert data["evento"]["fecha"] == "14/11/2026"
    assert data["evento"]["lugar"] == "Carrer de les Roselles, 32"
    assert len(data["evento"]["comicos"]) == 4
    assert data["evento"]["comicos"][0]["nombre"] == "Nombre Cómico 1"


def test_resolve_con_override_intercambia_y_persiste(runner, excel_path):
    result = runner.invoke(
        cli,
        [
            "resolve",
            "--month",
            "Noviembre",
            "--override",
            "Blue",
            "--excel",
            str(excel_path),
        ],
    )

    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["sabor"] == "Blue"
    assert data["carpeta_plantilla"] == "Plantillas/Blue"

    calendario, _ = load_workbook(excel_path)
    por_mes = {c.mes: c.sabor for c in calendario}
    assert por_mes["Noviembre"] == "Blue"
    assert por_mes["Abril"] == "RIE"


def test_resolve_con_override_a_mes_fijo_falla_sin_mutar_archivo(runner, excel_path):
    result = runner.invoke(
        cli,
        [
            "resolve",
            "--month",
            "Noviembre",
            "--override",
            "BlackBerry",
            "--excel",
            str(excel_path),
        ],
    )

    assert result.exit_code != 0
    assert "Marzo" in result.output

    calendario, _ = load_workbook(excel_path)
    por_mes = {c.mes: c.sabor for c in calendario}
    assert por_mes["Noviembre"] == "RIE"
    assert por_mes["Marzo"] == "BlackBerry"


def test_reveal_no_necesita_excel(runner):
    result = runner.invoke(cli, ["reveal", "--step", "2"])

    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data == {"step": 2, "visible_positions": [1, 3], "hidden_positions": [2, 4]}


def test_reveal_paso_invalido_falla(runner):
    result = runner.invoke(cli, ["reveal", "--step", "9"])

    assert result.exit_code != 0


def test_mark_generated_marca_el_evento(runner, excel_path):
    result = runner.invoke(
        cli, ["mark-generated", "--month", "Noviembre", "--excel", str(excel_path)]
    )

    assert result.exit_code == 0, result.output

    _, eventos = load_workbook(excel_path)
    assert eventos[0].estado == "Generado"


def test_resolve_acepta_el_mes_en_minusculas(runner, excel_path):
    result = runner.invoke(
        cli, ["resolve", "--month", "noviembre", "--excel", str(excel_path)]
    )

    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["mes"] == "Noviembre"
    assert data["sabor"] == "RIE"


def test_resolve_mes_sin_evento_falla(runner, excel_path):
    result = runner.invoke(
        cli, ["resolve", "--month", "Enero", "--excel", str(excel_path)]
    )

    assert result.exit_code != 0
