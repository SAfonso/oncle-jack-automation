# Especificación — oncle-jack-automation

Repo: https://github.com/SAfonso/oncle-jack-automation
Metodología: SDD (esta spec manda sobre cualquier código) + TDD (ningún
código de `src/` se escribe sin un test en rojo primero).

> **Estado actual:** v1 trabaja con el Excel en **local**. La integración
> con Google Drive es la v2, deliberadamente pospuesta hasta confirmar que
> la lógica funciona bien en local (ver sección 10).

## 1. Objetivo

Resolver, de forma determinista y testeable, todos los datos que hacen
falta para generar el cartel y el reel de un mes de Monólogos de L'Oncle
Jack: qué sabor de plantilla toca, qué 4 cómicos y en qué orden, qué
nombres hay que tapar en el teaser de esa semana, y dejar constancia en
el Excel de cualquier cambio (intercambio de sabor, evento marcado como
generado).

Este proyecto **no** toca Canva. Genera un resultado (JSON) que Claude
Code, ya con el `CLAUDE.md` del proyecto de carteles, usa para hacer las
llamadas al conector de Canva. La frontera es intencional: todo lo que se
pueda probar sin IA ni APIs externas de diseño, se prueba aquí.

## 2. Alcance v1

**Dentro:**
- Leer el Excel (`Sabores_disponibles`, `Calendario_Sabores`, `Eventos`)
  desde una ruta **local** en disco.
- Resolver el sabor de un mes: override explícito → si no, calendario.
- Aplicar el intercambio en el calendario cuando hay override, con la
  protección de los meses fijos (Octubre=Original, Diciembre=Winter,
  Marzo=BlackBerry).
- Calcular el estado de revelado (qué nombres tapar) para un paso
  1–4 de la secuencia.
- Marcar un evento como "Generado" en el Excel.
- Escribir de vuelta en el mismo archivo local cualquier cambio al
  calendario.

**Fuera (explícitamente, no lo pidas en esta versión):**
- Cualquier llamada a la API/MCP de Canva.
- Google Drive — v2, ver sección 10.
- Descarga o procesado de las fotos de los cómicos (se pasan las URLs
  ya editadas, tal cual).
- Interfaz gráfica; esto es un CLI.

## 3. Arquitectura

```
src/oncle_jack/
  models.py       # dataclasses: CalendarEntry, Event, RevealState
  calendar.py     # resolve_sabor(), apply_override_swap()  — puro, sin I/O
  reveal.py       # reveal_state(step)                      — puro, sin I/O
  excel_source.py # leer/escribir el .xlsx local             — I/O, se prueba contra un fixture real en disco
  cli.py          # entrypoint: click
```

`calendar.py` y `reveal.py` no importan nada de `excel_source` — reciben
y devuelven estructuras de Python normales. Eso es lo que los hace
testeables sin ningún archivo ni red. `excel_source.py` es la única capa
con I/O, y en tests se prueba contra un `.xlsx` de fixture en disco, con
`openpyxl`, sin red en ningún momento.

## 4. Modelo de datos

```python
@dataclass
class CalendarEntry:
    mes: str            # "Octubre", "Noviembre", ...
    sabor: str
    fijo: bool          # True para los meses fijos: Octubre, Diciembre, Marzo

@dataclass
class Comico:
    nombre: str
    foto_url: str

@dataclass
class Event:
    fecha: str           # dd/mm/yyyy
    mes: str             # derivado de fecha
    lugar: str
    mc_1: str
    mc_2: str
    comicos: list[Comico]  # exactamente 4, orden = orden de revelado (1º=arriba/más pequeño .. 4º=cabeza de cartel)
    sabor_override: str | None
    estado: str           # "Pendiente" | "Generado"

@dataclass
class RevealState:
    step: int                 # 1..4
    visible_positions: list[int]  # p.ej. [1,3] en el paso 2
    hidden_positions: list[int]   # p.ej. [2,4] en el paso 2
```

## 5. Comportamiento — criterios de aceptación

Cada bloque de aquí abajo es (como mínimo) un test en `tests/`.

### 5.1 `reveal_state(step)` — pura, sin I/O

- `reveal_state(1)` → visibles `[1]`, ocultos `[2,3,4]`
- `reveal_state(2)` → visibles `[1,3]`, ocultos `[2,4]`
- `reveal_state(3)` → visibles `[1,2,3]`, ocultos `[4]`
- `reveal_state(4)` → visibles `[1,2,3,4]`, ocultos `[]`
- `reveal_state(0)` o `reveal_state(5)` → lanza `ValueError` (no hay paso
  0 ni 5)

### 5.2 `resolve_sabor(calendario, eventos, mes)` — pura, sin I/O

- Si el evento de `mes` tiene `sabor_override` relleno → devuelve ese
  sabor, sin tocar el calendario.
- Si no, devuelve `calendario[mes].sabor`.
- Si `mes` no existe en el calendario → lanza `KeyError` explícito (no
  devolver un sabor por defecto silenciosamente).

### 5.3 `apply_override_swap(calendario, mes, sabor_pedido)` — pura, sin I/O

- Caso normal: `mes` tenía sabor "RIE", "Blue" estaba en "Abril" → tras
  la llamada, `mes` = "Blue" y "Abril" = "RIE". Devuelve el calendario
  actualizado.
- Si `mes` ya tenía asignado `sabor_pedido` → no hace ningún cambio
  (idempotente), lo devuelve tal cual.
- Si `sabor_pedido` no existe en ningún mes del calendario → lanza
  `ValueError` ("sabor desconocido").
- **Protección de meses fijos:** si `mes` es un mes fijo (Octubre,
  Diciembre o Marzo) O si el mes donde estaba `sabor_pedido` es un mes
  fijo → lanza `ValueError` explicando cuál de los dos es fijo y por qué
  no se puede mover. No se hace el intercambio parcialmente. Qué mes es
  fijo lo dice el dato (`fijo: bool` de `CalendarEntry`, columna `Tipo`
  del Excel) — el código no tiene la lista de meses fijos hardcodeada.

### 5.4 `excel_source` — con un `.xlsx` real de fixture, nunca de producción

- `load_workbook(path)` → devuelve `(calendario: list[CalendarEntry],
  eventos: list[Event])` a partir del `.xlsx` en esa ruta.
- `save_calendar(path, calendario)` → escribe de vuelta solo la hoja
  `Calendario_Sabores` modificada, sin tocar el resto del archivo.
- `mark_generated(path, evento)` → pone `Estado = "Generado"` en la fila
  de ese evento.
- Los tests usan `tests/fixtures/datos_ejemplo.xlsx` (copiado a un
  archivo temporal antes de cada test, para no mutar el fixture) — nunca
  el Excel real del usuario.

## 6. CLI — comandos

```
oncle-jack resolve --month <mes> [--override <sabor>] --excel <ruta>
```
Resuelve sabor (aplicando swap si hay override y lo persiste en el
archivo), carga el evento de ese mes, y devuelve por stdout un JSON:
```json
{
  "mes": "Noviembre",
  "sabor": "Blue",
  "carpeta_plantilla": "Plantillas/Blue",
  "evento": { "fecha": "...", "lugar": "...", "mc_1": "...", "mc_2": "...",
              "comicos": [ {"nombre": "...", "foto_url": "..."}, ... ] }
}
```

```
oncle-jack reveal --step <1|2|3|4>
```
Devuelve por stdout el JSON de `RevealState` para ese paso. No necesita
`--excel`, es puro.

```
oncle-jack mark-generated --month <mes> --excel <ruta>
```
Marca el evento de ese mes como "Generado" en el archivo.

`--excel` puede omitirse si se define `EXCEL_PATH` en `.env`.

## 7. Secretos

Ninguno en v1 — es un archivo local, sin credenciales de por medio. La
sección de secretos vuelve a aparecer en la v2 (Drive), ver sección 10.

## 8. CI

`.github/workflows/tests.yml` corre `pytest` en cada push y pull request
contra `main`. La suite completa no necesita red ni variables de entorno
— todo corre contra el fixture local en disco.

## 9. Definición de terminado (v1)

- Los 4 bloques de la sección 5 tienen tests en rojo escritos antes que
  el código, y en verde al terminar.
- `pytest` pasa en local y en GitHub Actions.
- `oncle-jack resolve` funciona de punta a punta contra el Excel real del
  usuario en local (verificación manual, no automática).
- README explica cómo ejecutar los tres comandos contra un Excel local.

## 10. v2 (pospuesta) — Google Drive

Una vez v1 esté verificado en local, `excel_source.py` pasa a leer/escribir
el `.xlsx` desde Google Drive en lugar de disco, manteniendo exactamente
la misma interfaz (`load_workbook`, `save_calendar`, `mark_generated`) —
por eso `calendar.py` y `reveal.py` no cambian nada al llegar la v2, ya
que no saben ni les importa de dónde viene el Excel.

Cuando llegue ese momento: cuenta de servicio de Google con acceso al
archivo, `GOOGLE_APPLICATION_CREDENTIALS` y `EXCEL_FILE_ID` como secretos
(`.env` en local, *secrets* de GitHub en CI) — nunca en código ni commits.
