# CHECKPOINTS.md — Criterios de validación

## Proyecto
CLI Python (oncle-jack-automation) que resuelve los datos mensuales de los carteles de Monólogos de L'Oncle Jack contra un Excel local. Spec completa en SPEC.md; v1 = solo local, Drive es v2.

## Criterios de aceptación

- Los 4 bloques de SPEC.md §5 tienen tests escritos en rojo antes del código y en verde al terminar
- `pytest` pasa en local y en GitHub Actions
- `oncle-jack resolve` funciona de punta a punta contra el Excel real (verificación manual)
- README explica cómo ejecutar los tres comandos contra un Excel local



## Restricciones
Ninguna tarea puede violarlas:

- Sin credenciales, v1 solo local, Drive es v2.




## Fuentes de datos

- Excel local `datos_carteles_oncle_jack.xlsx` (hojas Sabores_disponibles, Calendario_Sabores, Eventos)



## Reglas del harness

- Las tareas del backlog son atómicas: cortas, acotadas y con un único entregable verificable — nada de objetivos amplios tipo 'hazme el front'; esos los descompone el planner antes de entrar al backlog

- Cada tarea lleva complejidad (alta | media | baja) asignada por el planner, y se lanza con el modelo de su tier: alta → potente, media → intermedio, baja → económico

- Una tarea a la vez en in_progress

- Solo el reviewer puede marcar done

- Máximo 2 rechazos antes de escalar al usuario


## Definición de done
Una tarea está done cuando el reviewer la aprueba contra los criterios anteriores.
