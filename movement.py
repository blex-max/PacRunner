import constants as cst


def move_bound_y(
    cur_y: int,
    up: bool
) -> tuple[bool, int, int]:
    if up:
        if cur_y > cst.PG_UY_BOUND:
            # cur_y - 1 and neg bound because curses coord system
            return (1, cur_y - 1, cur_y)
        else:
            return (0, cur_y, None)
    elif not up:
        if cur_y < cst.PG_DY_BOUND:
            return (1, cur_y + 1, cur_y)
        else:
            return (0, cur_y, None)
    else:
        raise ValueError
