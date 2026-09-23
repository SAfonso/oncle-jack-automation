# AGENTS.md — Mapa de agentes

## Proyecto
CLI Python (oncle-jack-automation) que resuelve los datos mensuales de los carteles de Monólogos de L'Oncle Jack contra un Excel local. Spec completa en SPEC.md; v1 = solo local, Drive es v2.

## Modo del harness
EJECUTOR

## Agentes


### leader — modo DIRECTOR
**Scope:** Orquesta la ejecución del harness y escala al usuario cuando toca
**Tools:** ninguna definida


### planner — modo ARQUITECTO
**Scope:** Descompone objetivos en tareas atómicas y asigna complejidad a cada una
**Tools:** ninguna definida


### implementer — modo BISTURÍ
**Scope:** Implementa las tareas del backlog
**Tools:** ninguna definida


### reviewer — modo FISCAL
**Scope:** Revisa y valida el output contra los criterios de aceptación
**Tools:** ninguna definida


### integrator — modo NOTARIO
**Scope:** Formaliza en git el trabajo aprobado: crea la rama al iniciar la tarea y hace commit+push+PR al cerrarla
**Tools:** ninguna definida


### watchman — modo CENTINELA
**Scope:** Verifica CI y merge tras la integración; si falla, reabre el ciclo de revisión con el reviewer
**Tools:** ninguna definida



## Flujo

1. leader →


2. planner →


3. implementer →


4. reviewer →


5. integrator →


6. watchman


