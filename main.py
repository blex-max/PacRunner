import time
import sys
import curses
import constants as cst


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
    dheady = 0
    playgrid_x_mar = dw // 10
    playgrid_x_w = int(dw - (playgrid_x_mar * 2))
    playgrid_x_spc = playgrid_x_w // (cst.PLAYGRID_W - 1)

    color_offset = 1

    # init print
    rainbow_wave_ml(stdscr,
                    cst.TITLE_L,
                    dheady,
                    ((dw // 2) - (cst.TITLE_W // 2)),
                    cst.RAINBOW_L,
                    color_offset)
    color_offset = (color_offset + 1) % len(cst.RAINBOW_L)

    # print track
    for nl in range(cst.PLAYGRID_H):
        for nc in range(cst.PLAYGRID_W):
            stdscr.addch(cst.TITLE_H + cst.OFFSET_FROM_TITLE + nl,
                         playgrid_x_mar + (nc * playgrid_x_spc),
                         cst.GRIDCH)

    # print hero
    stdscr.addch(cst.TITLE_H + cst.OFFSET_FROM_TITLE + (cst.PLAYGRID_H // 2),
                 playgrid_x_mar + (cst.HERO_X * playgrid_x_spc),
                 cst.HEROCH, curses.color_pair(1) | curses.A_BOLD)
    # game loop
    while True:
        # usr input
        c = stdscr.getch()
        match c:
            case 113:  # q
                break
            case 259:  # arrow up
                pass
            case 258:  # arrow down
                pass
            case _:
                pass

        rainbow_wave_ml(stdscr,
                        cst.TITLE_L,
                        dheady,
                        ((dw // 2) - (cst.TITLE_W // 2)),
                        cst.RAINBOW_L,
                        color_offset)
        color_offset = (color_offset + 1) % len(cst.RAINBOW_L)

        # print track
        # for nl in range(cst.PLAYGRID_H):
        #     for nc in range(cst.PLAYGRID_W):
        #         stdscr.addch(cst.TITLE_H + cst.OFFSET_FROM_TITLE + nl,
        #                      playgrid_x_mar + (nc * playgrid_x_spc),
        #                      '.')

        stdscr.refresh()
        time.sleep(0.05)

    sys.exit(0)


curses.wrapper(main)
