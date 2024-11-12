import time
import sys
import curses
import constants as cst
import movement as mv


def rainbow_wave(stdscr, text, y_pos, init_x, colors, color_offset):
    for i, char in enumerate(text):
        color_index = (i + color_offset) % len(colors)
        stdscr.addch(y_pos,
                     init_x + i,
                     char,
                     curses.color_pair(color_index + 1) | curses.A_BOLD)


def rainbow_wave_ml(stdscr, line_l, init_y, init_x, colors, color_offset):
    for i, line in enumerate(line_l):
        rainbow_wave(stdscr, line, init_y + i, init_x, colors, color_offset)


def main(stdscr):
    stdscr.clear()
    stdscr.nodelay(True)
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()
    for i, color in enumerate(cst.RAINBOW_L):
        curses.init_pair(i + 1, color, -1)  # -1 for default background
    dh, dw = stdscr.getmaxyx()
    playgrid_x_mar = dw // 10
    playgrid_x_w = int(dw - (playgrid_x_mar * 2))
    playgrid_x_spc = playgrid_x_w // (cst.PLAYGRID_W - 1)
    hero_abs_x = playgrid_x_mar + (cst.HERO_REL_X * playgrid_x_spc)

    # init game loop
    # init vars
    hero_y = cst.PLAYGRID_YC
    legal_mv = 0
    color_offset = 1

    # init draw title
    rainbow_wave_ml(stdscr,
                    cst.TITLE_L,
                    cst.TITLE_Y_OFFSET,
                    ((dw // 2) - (cst.TITLE_W // 2)),
                    cst.RAINBOW_L,
                    color_offset)
    color_offset = (color_offset + 1) % len(cst.RAINBOW_L)
    # init draw track
    for nl in range(cst.PLAYGRID_H):
        for nc in range(cst.PLAYGRID_W):
            stdscr.addch(cst.PLAYGRID_Y_OFFSET + nl,
                         playgrid_x_mar + (nc * playgrid_x_spc),
                         cst.GRIDCH)
    # init draw hero
    stdscr.addch(hero_y,
                 hero_abs_x,
                 cst.HEROCH, curses.color_pair(1) | curses.A_BOLD)

    # game loop
    while True:
        # strobe title
        rainbow_wave_ml(stdscr,
                        cst.TITLE_L,
                        cst.TITLE_Y_OFFSET,
                        ((dw // 2) - (cst.TITLE_W // 2)),
                        cst.RAINBOW_L,
                        color_offset)
        color_offset = (color_offset + 1) % len(cst.RAINBOW_L)

        # usr input
        c = stdscr.getch()
        match c:
            case 113:  # q
                break
            case 258:  # arrow down
                legal_mv, hero_y, prev_y = mv.move_bound_y(hero_y, 1)
            case 259:  # arrow up
                legal_mv, hero_y, prev_y = mv.move_bound_y(hero_y, 0)
            case _:
                pass

        # draw hero
        stdscr.addch(hero_y,
                     hero_abs_x,
                     cst.HEROCH,
                     curses.color_pair(1) | curses.A_BOLD)
        if legal_mv:  # clear prev position
            stdscr.addch(prev_y,
                         hero_abs_x,
                         cst.GRIDCH)
            legal_mv = 0  # block until next time

        stdscr.refresh()
        time.sleep(0.05)

    sys.exit(0)


curses.wrapper(main)
