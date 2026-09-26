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

**Estado v1:** comandos `resolve` (`--month` opcional; sin él, mes objetivo
automático con la fecha del sistema, SPEC 5.6), `reveal` y `mark-generated`.
Validación de fotos Canva (SPEC 5.5) y de los 4 nombres solo en el evento
del mes objetivo. Fechas: el Excel admite `datetime` real o texto
`dd/mm/yyyy`; internamente `date`; el JSON sale en `dd/mm/yyyy`. La cabecera
de la columna 7 de `Eventos` es `Comico_2_Nombre` (bug corregido). 95 tests,
CI en GitHub Actions.

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

## Flujo de generación en Canva

Lo hace Claude con el MCP de Canva; el CLI solo entrega el JSON de
`resolve`. Detalle en `SPEC.md`, sección 11.

- Plantilla `Plantillas/<Sabor>` con dos diseños: Cartel (2 páginas) y Reel
  (7 páginas). Carpeta destino: `OncleJack/26/27/<Sabor>-<Mes>`.
- Cada `foto_url` es un shortlink `canva.link` a un diseño de Canva con un
  marco de imagen: se resuelve con `resolve-shortlink`, se lee su `mediaId` +
  `imageBox` y se aplica con `update_fill` + `crop_media`, escalando el
  `imageBox` por (ancho del marco destino / ancho del marco origen).
- Se genera un Cartel completo por cómico (4 diseños "Cartel k - <Nombre>"):
  página 1 = tarjeta del cómico k; página 2 = lineup con el paso k de
  revelado (1: solo el 1º visible; 2: 1º y 3º; 3: solo el 4º tapado; 4: los 4
  visibles). Orden por tamaño de letra: `Comico_1..4` de menor a mayor (el 4º
  es el cabeza de cartel). El Reel es uno solo.

### Gotchas conocidos

- `edit-design` solo permite operaciones de una página por llamada.
- Guardar sobre una transacción abierta con una copia antigua puede pisar
  cambios previos: verificar leyendo el contenido, no la miniatura (caché).
- Una fecha larga ("4 Octubre") parte el texto: ensanchar el cuadro y
  recolocar la hora.
- Los blur con medidas exactas del texto dejan asomar ascendentes/
  descendentes y pueden invadir la línea contigua o la fecha: ajustar a mano.
- Las exportaciones (PNG/MP4) son descargas de Canva y no se pueden guardar
  dentro de la carpeta de Canva.
- La hora (19:00h) no sale del Excel.

## Pendiente

- Error explícito en `resolve` si el mes objetivo tiene el sabor vacío en
  `Calendario_Sabores` (hoy daría `Plantillas/None`; pendiente de decisión).
- Test directo del caso "mes actual Generado -> siguiente" (el actual depende
  de que Diciembre esté vacío en el fixture).
- Endurecer `validate_foto_url` (puertos/mayúsculas; mensaje sin
  `www.canva.com`).
- La hora del show no sale del Excel.
- Fuera de alcance: flujo de bustos, ver `SPEC_BUSTOS.md`. v2 (Drive)
  pospuesta.
