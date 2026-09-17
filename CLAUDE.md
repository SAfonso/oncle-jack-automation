# Proyecto: Carteles y reel — Monólogos de L'Oncle Jack

Este archivo le dice a Claude Code qué hacer cuando le pidas cosas como
**"haz los carteles de este mes"** o **"haz los carteles de este mes pero
con la plantilla Blue"**.

## Antes de la primera vez — requisito único

Este proyecto necesita el conector MCP de Canva conectado en Claude Code
(distinto del conector de Canva del chat de claude.ai). Instrucciones:
https://www.canva.com/help/mcp-agent-setup/ (busca "Manual Configuration").
Requiere que la cuenta de Canva sea Pro, Teams, Business o Nonprofit.
Compruébalo con `/mcp` dentro de Claude Code antes de pedir nada de lo de abajo.

## De dónde salen los datos

Todo sale de `datos_carteles_oncle_jack.xlsx` (pendiente de subir a Google
Drive — de momento vive en este proyecto), con 4 hojas:

- **Sabores_disponibles**: nombres exactos de las carpetas de plantilla en
  Canva (`Plantillas > <Sabor>`). Son literales — hay que usarlos tal cual,
  sin traducir ni cambiar mayúsculas.
- **Calendario_Sabores**: qué sabor le toca a cada mes de la temporada
  26/27. Octubre = "Original", Diciembre = "Winter" y Marzo = "BlackBerry"
  son **fijos**, no se tocan salvo por la mecánica de intercambio (ver
  abajo). El resto de meses los rellena el usuario.
- **Eventos**: una fila por show — fecha, lugar, MC's, y los 4 cómicos
  (nombre + link a su foto ya editada con el filtro). Columna
  `Sabor_override`: normalmente vacía; si tiene un valor, fuerza ese sabor
  para ese evento en concreto.
- **Instrucciones**: notas de uso para humanos, ignorar como fuente de datos.

## Qué es una "plantilla" (por sabor)

Cada carpeta `Plantillas/<Sabor>` en Canva contiene DOS diseños distintos
que hay que tratar juntos:

- **"Cartel"** (1080×1080, cuadrado, 2 páginas):
  - Página 1: tarjeta individual cuadrada de un cómico (foto + nombre).
  - Página 2: cartel de lineup con los 4 nombres, algunos tapados por una
    capa de "blur" pixelado (ver mecánica de revelado progresivo abajo).
- **"Reel"** (1080×1920, vertical, 7 páginas):
  - Página 1: collage intro con las fotos de los 4 cómicos.
  - Páginas 2–5: tarjeta individual vertical de cada uno de los 4 cómicos.
  - Página 6: tarjeta de MC's.
  - Página 7: cartel final con los 4 nombres ya sin tapar, fecha y dirección.

Todo lo decorativo (filigrana, tipografía, iconos, texturas) es parte fija
de la plantilla del sabor — el proceso NUNCA lo toca. Solo se tocan:
nombres, fecha, fotos, y las capas de blur de la página 2 del Cartel.

## Resolver qué sabor toca a un evento

1. Si la fila del evento en "Eventos" tiene `Sabor_override` relleno, ese
   es el sabor a usar.
2. Si no, mira el mes de la `Fecha` del evento y búscalo en
   `Calendario_Sabores` para obtener el sabor.

## Mecánica de intercambio cuando hay override

Si el usuario pide explícitamente un sabor distinto al que le toca a ese
mes (p. ej. "haz los carteles de este mes pero con la plantilla Blue"
cuando este mes no era Blue en el calendario):

1. Anota qué sabor tenía asignado ESTE mes en `Calendario_Sabores`
   (p. ej. "RIE").
2. Busca en qué mes estaba asignado el sabor pedido ("Blue") en el
   calendario (p. ej. "Abril").
3. Intercambia los dos: este mes pasa a tener "Blue", y "Abril" pasa a
   tener "RIE". Escribe ese intercambio de vuelta en la hoja
   `Calendario_Sabores` del Excel.
4. Genera el cartel/reel de este mes usando el sabor pedido ("Blue").
5. Nunca toques las filas fijas (Octubre=Original, Diciembre=Winter,
   Marzo=BlackBerry) como destino de un intercambio — si el sabor pedido
   resulta estar asignado a Octubre, Diciembre o Marzo, avisa al usuario
   en vez de mover esas filas.

## El proceso paso a paso, por evento

1. Resuelve el sabor del evento (sección anterior).
2. Duplica (`copy-design`) el "Cartel" Y el "Reel" de `Plantillas/<Sabor>`.
3. Crea la carpeta `OncleJack/26/27/<Sabor>-<Mes>` en Canva
   (`create-folder`) y mueve ahí las dos copias (`move-item-to-folder`).
4. Rellena en ambas copias: los 4 nombres, la fecha, y sustituye cada foto
   por la de su URL correspondiente (mismo mecanismo de `edit-design` /
   `replace_text` / sustitución de imagen ya usado en las pruebas).
5. En la página 2 del "Cartel" (el lineup con blur), aplica el estado de
   revelado que corresponda a esta publicación concreta (ver mecánica de
   revelado progresivo) — el usuario debe indicar qué día/paso de la
   secuencia toca, ya que eso no sale del Excel.
6. Confirma (commit) y exporta: el "Cartel" en PNG (ambas páginas) y el
   "Reel" en MP4, dentro de esa misma carpeta.
7. Actualiza en el Excel el Estado de esa fila a "Generado".

## Mecánica del revelado progresivo (página 2 del "Cartel")

Los 4 nombres están ordenados de arriba a abajo por tamaño de letra
(1º el más pequeño/arriba, 4º el cabeza de cartel/abajo). Se revelan en
este orden a lo largo de la semana:

- Paso 1: solo el 1º visible (2º, 3º y 4º tapados).
- Paso 2: 1º y 3º visibles (2º y 4º tapados).
- Paso 3: 1º, 3º y 2º visibles (solo el 4º tapado).
- Paso 4: los 4 visibles (estado final, coincide con la página 7 del reel).

Para tapar un nombre: crea un rectángulo con la misma imagen de textura de
píxel ya usada en la plantilla, con el mismo `top/left/width/height`
EXACTOS del elemento de texto de ese nombre (cada nombre tiene un tamaño
distinto — el blur debe copiar sus medidas, ni más ni menos). Para
destapar un nombre: elimina el rectángulo de blur que lo cubre.

## Cosas a vigilar (bugs conocidos)

- Si un nombre o la fecha es más largo de lo normal, el cuadro de texto
  puede crecer y montarse encima del texto de abajo. Revisa la miniatura
  de cada página tras editar y avisa si detectas solape — no lo des por
  bueno en silencio.
- Todas las operaciones de `edit-design` dentro de una misma llamada
  tienen que ser de la misma página.
- No se puede leer ni recrear la animación/transición del reel — no hace
  falta: al duplicar el archivo tal cual, la animación se conserva sola.

## Estilo al hablar de esto con el usuario

Sé directo sobre qué se hizo y qué no. Si algo falla (una foto no
descarga, un locator_id no coincide, el texto se desborda, un sabor pedido
choca con un mes fijo), dilo explícitamente en vez de dar el resultado por
bueno.
