import shutil
from pathlib import Path

import pytest

from oncle_jack.excel_source import load_workbook, mark_generated, save_calendar

FIXTURE = Path(__file__).parent / "fixtures" / "datos_ejemplo.xlsx"


@pytest.fixture
def excel_path(tmp_path):
    destino = tmp_path / "datos.xlsx"
    shutil.copy(FIXTURE, destino)
    return destino


def test_load_workbook_lee_calendario_y_eventos(excel_path):
    calendario, eventos = load_workbook(excel_path)

    octubre = next(c for c in calendario if c.mes == "Octubre")
    assert octubre.sabor == "Original"
    assert octubre.fijo is True

    marzo = next(c for c in calendario if c.mes == "Marzo")
    assert marzo.sabor == "BlackBerry"
    assert marzo.fijo is True

    noviembre = next(c for c in calendario if c.mes == "Noviembre")
    assert noviembre.sabor == "RIE"
    assert noviembre.fijo is False

    assert len(eventos) == 1
    evento = eventos[0]
    assert evento.fecha == "14/11/2026"
    assert evento.mes == "Noviembre"
    assert evento.lugar == "Carrer de les Roselles, 32"
    assert evento.mc_1 == "Mercè Copado"
    assert evento.mc_2 == "Sergio Afonso"
    assert evento.estado == "Pendiente"
    assert evento.sabor_override is None
    assert len(evento.comicos) == 4
    assert evento.comicos[0].nombre == "Nombre Cómico 1"
    assert evento.comicos[3].foto_url == "https://drive.google.com/uc?id=FIX4"


def test_save_calendar_escribe_solo_la_hoja_calendario(excel_path):
    calendario, eventos_antes = load_workbook(excel_path)
    for entry in calendario:
        if entry.mes == "Noviembre":
            entry.sabor = "Blue"

    save_calendar(excel_path, calendario)

    calendario_recargado, eventos_despues = load_workbook(excel_path)
    noviembre = next(c for c in calendario_recargado if c.mes == "Noviembre")
    assert noviembre.sabor == "Blue"
    # no ha tocado el resto del archivo
    assert eventos_despues == eventos_antes


def test_mark_generated_marca_el_evento_correspondiente(excel_path):
    _, eventos = load_workbook(excel_path)
    evento = eventos[0]
    assert evento.estado == "Pendiente"

    mark_generated(excel_path, evento)

    _, eventos_recargados = load_workbook(excel_path)
    assert eventos_recargados[0].estado == "Generado"


def test_no_muta_el_fixture_original(excel_path):
    calendario, _ = load_workbook(excel_path)
    for entry in calendario:
        entry.sabor = "Cambiado"
    save_calendar(excel_path, calendario)

    calendario_original, _ = load_workbook(FIXTURE)
    assert all(c.sabor != "Cambiado" for c in calendario_original)
