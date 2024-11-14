import sys
import curses
from pytick.Ticker import Ticker
import constants as cst
import movement as mv


# passing colors to this makes no sense, it doesn't use them directly
def colour_strobe(stdscr, text, y_pos, init_x, colors, color_offset):
    for i, char in enumerate(text):
        color_index = (i + color_offset) % len(colors)
        stdscr.addch(y_pos,
                     init_x + i,
                     char,
                     curses.color_pair(color_index + 1) | curses.A_BOLD)


def colour_wave(stdscr, line_l, init_y, init_x, colors, color_offset):
    for i, line in enumerate(line_l):
        colour_strobe(stdscr, line, init_y + i, init_x, colors, color_offset)


# consider config dataclass for accessing
# system-specific (i.e. assinged with in main) constants
# when separating into sub windows and so on
def main(stdscr):
    stdscr.clear()
    stdscr.nodelay(True)
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()
    for i, color in enumerate(cst.COLOR_L):
        curses.init_pair(i + 1, color, -1)  # -1 for default background
    dh, dw = stdscr.getmaxyx()
    topwin = stdscr.subwin(cst.TITLE_H, dw, cst.TITLE_Y_OFFSET, 0)
    playarea_x_mar = dw // 8
    playarea_x_w = int(dw - (playarea_x_mar * 2))
    playgrid_x_spc = (playarea_x_w - (2 * cst.PLAYAREA_HMAR)) // (cst.PLAYGRID_W - 1)
    playwin = stdscr.subwin(cst.PLAYAREA_H, playarea_x_w, cst.PLAYAREA_Y_OFFSET, playarea_x_mar)
    hero_x = (cst.HERO_REL_X * playgrid_x_spc) + cst.PLAYAREA_HMAR

    # init game loop
    # init vars
    timer = Ticker(0.01)
    hero_y = cst.PLAYAREA_YC
    hero_x = (cst.HERO_REL_X * playgrid_x_spc) + cst.PLAYAREA_HMAR
    legal_mv = 0
    color_offset = 1

    # init draw title
    colour_wave(topwin,
                cst.TITLE_L,
                cst.TITLE_Y_OFFSET,
                ((dw // 2) - (cst.TITLE_W // 2)),
                cst.COLOR_L,
                color_offset)
    color_offset = (color_offset + 1) % len(cst.COLOR_L)
    playwin.box()
    # init draw track
    for nl in range(cst.PLAYGRID_H):
        for nc in range(cst.PLAYGRID_W):
            playwin.addch(nl + cst.PLAYAREA_VMAR,
                          (nc * playgrid_x_spc) + cst.PLAYAREA_HMAR,
                          cst.GRIDCH)
    # init draw hero
    playwin.addch(hero_y,
                  hero_x,
                  cst.HEROCH,
                  curses.color_pair(1) | curses.A_BOLD)
    timer.start()
    # game loop
    while True:
        # strobe title and edges
        if timer.counter_comp(5):
            colour_wave(topwin,
                        cst.TITLE_L,
                        cst.TITLE_Y_OFFSET,
                        ((dw // 2) - (cst.TITLE_W // 2)),
                        cst.COLOR_L,
                        color_offset)
            for y in [cst.PLAYAREA_VMAR - 1, cst.PLAYAREA_H - 3]:
                colour_strobe(playwin,
                              '-' * (playarea_x_w - (cst.PLAYAREA_HMAR * 2)),
                              y,
                              cst.PLAYAREA_HMAR,
                              [cst.COLOR_L[0], cst.COLOR_L[2]],
                              color_offset)
            color_offset = (color_offset + 1) % len(cst.COLOR_L)
            topwin.refresh()

        # usr input
        c = stdscr.getch()
        match c:
            case 113:  # q
                break
            case 258:  # arrow down
                legal_mv, hero_y, prev_y = mv.move_bound_y(hero_y, 0)
            case 259:  # arrow up
                legal_mv, hero_y, prev_y = mv.move_bound_y(hero_y, 1)
            case _:
                pass

        # draw hero
        playwin.addch(hero_y,
                      hero_x,
                      cst.HEROCH,
                      curses.color_pair(1) | curses.A_BOLD)
        if legal_mv:  # clear prev position
            playwin.addch(prev_y,
                          hero_x,
                          cst.GRIDCH)
            legal_mv = 0  # block until next time

        playwin.refresh()
        # stdscr.refresh()
        timer.update()

    sys.exit(0)


curses.wrapper(main)
