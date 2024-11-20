import curses
from typing import LiteralString


def art_width(ml_str):
    return len(ml_str.strip().splitlines()[0])


def art2lines(ml_str):
    return ml_str.strip().splitlines()


def colour_strobe(stdscr,
                  text: str,
                  y_pos: int,
                  init_x: int,
                  color_offset: int,
                  color_wrap: int):
    for i, char in enumerate(text):
        color_index = (i + color_offset) % color_wrap
        stdscr.addch(y_pos,
                     init_x + i,
                     char,
                     curses.color_pair(color_index + 1) | curses.A_BOLD)


def colour_wave(stdscr,
                line_l: list[str] | list[LiteralString],
                init_y: int,
                init_x: int,
                color_offset: int,
                color_wrap: int):
    for i, line in enumerate(line_l):
        colour_strobe(stdscr,
                      line,
                      init_y + i,
                      init_x,
                      color_offset,
                      color_wrap)
