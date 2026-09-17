from oncle_jack.models import RevealState

# Orden de revelado a lo largo de la semana (ver CLAUDE.md): 1º, luego 3º,
# luego 2º, y por último el cabeza de cartel (4º).
_ORDEN_REVELADO = [1, 3, 2, 4]


def reveal_state(step: int) -> RevealState:
    if step not in (1, 2, 3, 4):
        raise ValueError(f"paso de revelado inválido: {step} (debe ser 1-4)")

    visible = sorted(_ORDEN_REVELADO[:step])
    hidden = sorted(_ORDEN_REVELADO[step:])
    return RevealState(step=step, visible_positions=visible, hidden_positions=hidden)
