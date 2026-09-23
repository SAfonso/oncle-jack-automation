#!/bin/bash
# init.sh — Verificación del entorno
# Proyecto: CLI Python (oncle-jack-automation) que resuelve los datos mensuales de los carteles de Monólogos de L'Oncle Jack contra un Excel local. Spec completa en SPEC.md; v1 = solo local, Drive es v2.

echo "Verificando entorno..."


echo "Stack: Python"

echo "Stack: click"

echo "Stack: openpyxl"

echo "Stack: pytest"


echo "Modo harness: EJECUTOR"
echo "Complejidad: simple"

echo "Comprobando git/gh (necesarios para integrator/NOTARIO y watchman/CENTINELA)..."
if ! command -v git >/dev/null 2>&1; then
  echo "FALTA: git no está instalado"
fi
if ! command -v gh >/dev/null 2>&1; then
  echo "FALTA: gh no está instalado — instálalo antes de la primera tarea"
fi
if ! gh auth status >/dev/null 2>&1; then
  echo "gh no está autenticado — ejecuta 'gh auth login' antes de la primera tarea"
fi
if ! git remote get-url origin >/dev/null 2>&1; then
  echo "No hay remoto 'origin' configurado — configúralo antes de la primera tarea"
fi

echo "Entorno verificado. Listo para iniciar."
