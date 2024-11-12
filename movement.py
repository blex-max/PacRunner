import constants as cst


def move_bound_y(
    cur_y: int,
    ve: bool
) -> tuple[bool, int]:
    if ve == 1:
        if cur_y < cst.PG_ABS_PY_BOUND:
            return (1, cur_y + 1, cur_y)
        else:
            return (0, cur_y, None)
    elif ve == 0:
        if cur_y > -cst.PG_ABS_NY_BOUND:
            return (1, cur_y - 1, cur_y)
        else:
            return (0, cur_y, None)
    else:
        raise ValueError
