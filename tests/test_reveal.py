import pytest

from oncle_jack.reveal import reveal_state


def test_step_1_solo_el_primero_visible():
    state = reveal_state(1)
    assert state.step == 1
    assert state.visible_positions == [1]
    assert state.hidden_positions == [2, 3, 4]


def test_step_2_primero_y_tercero_visibles():
    state = reveal_state(2)
    assert state.visible_positions == [1, 3]
    assert state.hidden_positions == [2, 4]


def test_step_3_solo_el_cuarto_tapado():
    state = reveal_state(3)
    assert state.visible_positions == [1, 2, 3]
    assert state.hidden_positions == [4]


def test_step_4_todos_visibles():
    state = reveal_state(4)
    assert state.visible_positions == [1, 2, 3, 4]
    assert state.hidden_positions == []


@pytest.mark.parametrize("step", [0, 5])
def test_step_fuera_de_rango_lanza_value_error(step):
    with pytest.raises(ValueError):
        reveal_state(step)
