# oncle-jack-automation

CLI que resuelve, de forma testeada (TDD), los datos de cada mes de
Monólogos de L'Oncle Jack: qué sabor de plantilla toca, el lineup de esa
fecha, y qué nombres tocan revelarse esa semana en el teaser.

Este proyecto **no** toca Canva — eso lo hace Claude Code por su cuenta,
usando la salida de este CLI, siguiendo el `CLAUDE.md` del proyecto de
carteles. Sigue SDD + TDD: la especificación completa, con los criterios
de aceptación de cada pieza, está en [`SPEC.md`](./SPEC.md) — ningún
código en `src/` se escribe sin un test en rojo primero.

**Estado actual:** v1 trabaja contra un Excel **local**. La integración
con Google Drive es la v2, pospuesta a propósito hasta confirmar que la
lógica funciona bien en local (detalle en `SPEC.md`, sección 10).

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

No hace falta `.env` ni credenciales en esta versión — solo la ruta al
Excel.

## Comandos

```bash
# --month es opcional: sin él se usa el mes objetivo (SPEC 5.6, fecha del sistema)
oncle-jack resolve --month noviembre --excel ./datos_carteles_oncle_jack.xlsx [--override Blue]
oncle-jack reveal --step 2
oncle-jack mark-generated --month noviembre --excel ./datos_carteles_oncle_jack.xlsx
```

`reveal` es puro (sin I/O) — no necesita `--excel`.

Si defines `EXCEL_PATH` en `.env`, puedes omitir `--excel` en `resolve` y `mark-generated`.

## Tests

```bash
pytest
```

La suite corre entera contra el fixture de `tests/fixtures/`, sin tocar
nunca el Excel real ni la red.

## Estructura

```
src/oncle_jack/
  models.py       # dataclasses del dominio
  calendar.py     # resolve_sabor(), apply_override_swap() — puro
  reveal.py       # reveal_state(step) — puro
  excel_source.py # lectura/escritura del .xlsx local — única capa con I/O
  cli.py          # entrypoint (click)
tests/
SPEC.md           # especificación y criterios de aceptación
```
