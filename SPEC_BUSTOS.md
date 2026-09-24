# Especificación — flujo "bustos de cómicos"

Spec independiente de SPEC.md. SPEC.md y la v1 del CLI no se modifican.
Este trabajo se ejecuta DESPUÉS de cerrar las tareas 1 a 4 de la v1.
Metodología: SDD + TDD (ningún código de `src/` sin test en rojo antes).
Material de origen: `resumen_bustos_oncle_jack.md` y
`resumen_errores_canva_comicos.md` (Descargas del usuario).

Leyenda: **[SUPUESTO]** = valor por defecto no confirmado por Sergio,
pendiente de confirmar.

## 1. Objetivo y disparador

Desde una carpeta local de fotos de grupo, producir un diseño de Canva por
persona (busto recortado, sin fondo, centrado sobre "Plantilla Papel") en
`Proyectos > OncleJack > Plantillas > <Sabor> > ComicosFin` (el sabor varía
según el mes/evento; ver §6.2).

Disparador: la frase "ya están las fotos finales" (se aceptan variantes).
Si el usuario no da la ruta de la carpeta de fotos, Claude la pide; no la
adivina.

## 2. Reparto de responsabilidades

| Parte | Dónde vive | Se prueba |
|---|---|---|
| Validar la carpeta de bustos y emitir el plan JSON | CLI Python (`oncle-jack`) | pytest, sin red ni API |
| Recorte de transparencia al bbox del alfa y cálculo de escala/posición | Python puro (Pillow) | pytest con PNG sintéticos |
| Selección de la mejor foto por persona y obtención de recortes | Llamada a la API de Anthropic (visión) | manual + tests con cliente simulado |
| Llamadas al MCP de Canva | Instrucciones en sección nueva de CLAUDE.md | manual |

El CLI no llama a Canva. La frontera es la misma que en SPEC.md §1.

## 3. Fases del flujo

1. **Entrada.** Carpeta local con fotos de grupo (ruta dada por Sergio).
2. **Propuesta de selección.** Claude (API de visión) propone, por persona,
   la mejor foto (ojos abiertos, expresión, mirada a cámara, nitidez,
   gorra/pelo sin cortar por el borde). Sergio APRUEBA la selección antes de
   recortar. Sin aprobación no se pasa a la fase 3.
3. **Recorte a busto.** Solo del pecho/costillas hacia arriba (con brazos si
   el usuario lo pide), fondo transparente, contornos suavizados, sin restos
   de vecinos ni objetos (ver §5).
4. **Salida de bustos:** PNG con alfa, nombrados `busto_N_descripcion.png`
   (confirmado).
5. **Validación (CLI).** `oncle-jack validate-bustos --dir <ruta>` comprueba
   número de PNG (entre 1 y 7; N = nº de PNG de entrada, ver §4), canal alfa y patrón de nombre, y emite
   un JSON con el plan por busto: archivo, nombre de diseño, tamaño tras
   recortar al bbox del alfa, escala y posición. Sale con error si algo no
   cumple.
6. **Composición en Canva** (instrucciones en CLAUDE.md, §6).

## 4. Composición (fase 5-6)

- Plantilla: `DAHWAo4A-jQ` "Plantilla Papel", 1080x1350, una capa
  (confirmado por Sergio: siempre la misma). Nunca se modifica.
- Antes de centrar, se recorta la transparencia sobrante al bbox del alfa,
  para centrar la silueta y no la caja del PNG (error conocido del resumen 2).
  Si el alfa es totalmente transparente, error explícito.
- Escala proporcional, sin deformar, con límite `max_pct` (defecto 0.70
  (confirmado)): ancho <= 1080*max_pct (756) y
  alto <= 1350*max_pct (945); rige el límite que se alcance antes. Puede
  ampliar o reducir según el bbox; siempre queda aire de papel por los
  cuatro lados.
- Centrado en horizontal y vertical.
- Un diseño por busto, copia de la plantilla, guardado con el nombre del
  busto (nunca "Plantilla Papel"), en `Proyectos > OncleJack > Plantillas >
  <Sabor> > ComicosFin` (carpeta `ComicosFin` dentro del sabor, §6.2).
- Nº de bustos VARIABLE, de 1 a 7 (confirmado por Sergio): puede haber un
  artista de última hora (7) o faltar alguno (p. ej. 3). Mínimo 1, máximo 7;
  0 u 8 o más PNG -> error explícito. N = nº de PNG de entrada. No se
  asume una composición fija (MCs/cómicos).

## 5. Selección y recorte con API (dependencia nueva)

- Dependencia: SDK `anthropic`. Justificación: la selección de la mejor foto
  es un juicio visual subjetivo que no se puede hacer de forma determinista
  en el repo, y SAM/ultralytics/torch se descartan (peso, falta de disco).
- Secreto: `ANTHROPIC_API_KEY` solo por variable de entorno (`.env`, ya
  ignorado por git). Nunca en código, tests ni ejemplos. Los tests usan
  cliente simulado, sin red ni clave.
- Salida de la API validada antes de usarse (entrada externa): esquema JSON
  estricto (persona, foto, caja/puntos), rangos dentro de la imagen.
- **Decisión de Sergio (opción a): quitar el fondo.** La API devuelve una
  caja por persona; se recorta la foto a esa caja (Pillow) y se quita el
  fondo con `remove-background` del conector de Canva. No se añade `rembg`
  ni ninguna dependencia aparte de `anthropic` y `Pillow`. Sergio NO exige
  la revisión manual como paso obligatorio.
- **Riesgo conocido y aviso obligatorio:** en fotos de grupo la caja puede
  contener a vecinos, que `remove-background` conservaría (error 3 del
  resumen 1). El flujo debe AVISAR cuando la caja de una persona solape con
  la caja de otra persona de la misma foto (comprobación determinista y
  testeable). La miniatura de aprobación del primer busto (§6.4) sirve
  además para detectarlo visualmente. El aviso no bloquea: informa.
- Pillow: dependencia nueva, justificada por el recorte al bbox del alfa.

## 6. Instrucciones de Canva (van a CLAUDE.md, sección nueva)

Orden de operaciones y reglas (derivadas de los errores conocidos):

1. Comprobar acceso del entorno a `www.canva.com` y
   `export-download.canva.com`. Si falla, PARAR y avisar antes de nada más.
2. Subir los bustos enviando los bytes directamente. NO usar
   `upload-asset-from-url` para el PNG exportado (falló con "No approval
   received").
3. Por busto: `copy-design` de `DAHWAo4A-jQ`, título = nombre del busto (no
   "Plantilla Papel", para no confundirla con la original). Colocar el
   busto según §4.
4. Puerta de aprobación (confirmado): solo el primero; descargar la
   miniatura y ENTREGARLA como archivo (no describirla como si se viera);
   esperar OK; guardar la edición al recibirlo (una edición abierta sin
   guardar deja la copia vacía) y hacer el resto.
5. Exportar cada diseño a PNG 1080x1350 y verificar tras descargar.
6. Mover solo los DISEÑOS a ComicosFin con `move-item-to-folder`. Mover
   imágenes falla siempre con este conector: no intentarlo. Avisar
   explícitamente de que los PNG exportados quedan en Subidos y hay que
   arrastrarlos a mano a ComicosFin.
7. Canva renombra las subidas (sin guiones bajos, sufijo " - 1"): buscarlas
   en Subidos por "Busto" o por ID, no por el nombre original.
8. Al final listar ComicosFin y confirmar que están los N diseños esperados (N = nº de PNG de entrada); no dar
   nada por bueno sin verificarlo.
9. No modificar nunca la plantilla original. Reportar directo lo que falló.

## 6.2 Sabor y carpeta de destino

Destino confirmado: `Plantillas/<Sabor>/ComicosFin`.

**Decisión de Sergio:** el sabor NO se lo dice él ni se pasa a mano; se
infiere del último sabor hecho en los carteles.

**Definición de "último" (CONFIRMADA por Sergio; el Excel no guarda marca de
cuándo se generó cada fila):** el sabor del evento
con `Estado = "Generado"` de `Fecha` más reciente en la hoja Eventos,
resuelto con la lógica de carteles (`Sabor_override` si existe, si no
`Calendario_Sabores` por mes; `resolve_sabor`). Solo lectura del Excel, sin
cambios de esquema y sin el swap de `resolve`. Nota: "más reciente" es por
fecha del show, no por el momento en que se marcó Generado.

Casos borde:
- Ninguna fila "Generado": error explícito; no se inventa sabor.
- Filas "Generado" en meses distintos con sabores distintos: se elige la de
  fecha más reciente y el flujo MUESTRA el sabor inferido (y de qué evento)
  para que Sergio lo vea antes de seguir.
- Empate de fecha más reciente con sabores distintos: error explícito.
- Mes sin entrada en el calendario: error (KeyError de `resolve_sabor`).

`validate-bustos` acepta `--sabor` como override opcional; si no se pasa, se
infiere (confirmado por Sergio).
Emite `sabor`, `origen_sabor` (inferido|parametro) y `carpeta_destino`. Si
la carpeta `ComicosFin` no existe en ese sabor, avisar (no crearla en
silencio).

Consecuencia: el flujo de bustos LEE el Excel (solo lectura), a diferencia
de lo dicho en §6.1.

## 6.1 Relación con el Excel y el flujo de carteles

Sin cambios de esquema en el Excel (confirmado). Nombres de archivo
`busto_N_descripcion` (confirmado). Este flujo es independiente del de
carteles/reel mensuales, salvo que LEE el Excel (solo lectura) para inferir
el sabor (§6.2); no lo escribe.

## 7. Criterios de aceptación (mínimo un test cada uno)

- Recorte al bbox del alfa: PNG con margen transparente -> imagen del
  tamaño del bbox; alfa vacío -> error.
- Cálculo de escala/posición: respeta 756x945 (defecto), proporción
  intacta, centrado exacto; `max_pct` configurable; entradas fuera de rango
  -> error.
- `validate-bustos`: carpeta correcta -> JSON del plan con exit 0; falta un
  PNG, PNG sin alfa o nombre mal formado -> exit distinto de 0 con mensaje
  claro.
- Cliente de selección: con cliente simulado, respuesta válida -> propuesta
  parseada; respuesta con esquema roto o coordenadas fuera de imagen ->
  error; sin `ANTHROPIC_API_KEY` -> error explícito, sin red.
- `pytest` verde local y en CI sin red ni secretos.

## 8. Fuera de alcance

Mover imágenes a ComicosFin por API; cambios en el Excel; Drive (v2 de
SPEC.md); SAM/ultralytics/torch.

## 9. Supuestos y estado

Confirmados por Sergio: nº de bustos variable de 1 a 7; carpeta destino
`Plantillas/<Sabor>/ComicosFin`; plantilla `DAHWAo4A-jQ`; sabor inferido del
último generado en carteles, con "último" = fecha de show más reciente con
Estado="Generado"; `--sabor` como override opcional; nombres
`busto_N_descripcion`; sin cambios de esquema en el Excel; 70 % como
parámetro por defecto; puerta de aprobación solo en el primer busto; frase
disparadora con variantes y petición de la ruta si falta.

Enmienda de la restricción "sin credenciales": CONFIRMADA por Sergio. Uso de
`ANTHROPIC_API_KEY` por variable de entorno aprobado. Redacción: "sin
credenciales en la v1 de carteles; los bustos usan solo variable de entorno
(ANTHROPIC_API_KEY), nunca en el repo" (tarea 14). Nada queda sin confirmar.
