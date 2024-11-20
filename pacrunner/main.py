import sys
import curses
from pytick.ticker import Ticker
from pacrunner import constants as cst
from pacrunner import visobj as vo
from pacrunner import artfunc as af
import random as rnd


# consider config dataclass for accessing
# system-specific (i.e. assinged with in main) constants
# when separating into sub windows and so on
def gameloop(stdscr):
    stdscr.clear()
    stdscr.nodelay(True)
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()
    for i, color in enumerate(cst.COLOR_L):
        curses.init_pair(i + 1, color, -1)  # -1 for default background
    dh, dw = stdscr.getmaxyx()
    topwin = stdscr.subwin(cst.TITLE_H,
                           dw,
                           cst.TITLE_Y_OFFSET,
                           0)
    playarea_x_mar = dw // 6  # changing 8 to 6 here fucked up the ghost clearing
    playarea_x_w = int(dw - (playarea_x_mar * 2))
    playgrid_x_w = (playarea_x_w - (2 * cst.PLAYAREA_HMAR))
    playgrid_x_spc = playgrid_x_w // (cst.PLAYGRID_W - 1)
    playgrid_rx_bound = cst.PLAYAREA_HMAR + (cst.PLAYGRID_W - 1) * playgrid_x_spc
    playwin = stdscr.subwin(cst.PLAYAREA_H,
                            playarea_x_w,
                            cst.PLAYAREA_Y_OFFSET,
                            playarea_x_mar)
    playwin.box()

    # init game loop
    # init vars
    timer = Ticker(0.01)
    x_speed = 1000  # higher is slower
    init_player_x = (cst.HERO_REL_X * playgrid_x_spc) + cst.PLAYAREA_HMAR
    pacman = vo.Player(
        cst.PLAYAREA_YC,
        init_player_x,
        cst.PG_DY_BOUND,
        init_player_x,
        cst.PG_UY_BOUND
    )
    ghosts = []
    color_offset = 1
    # draw track - might be visually nicer without
    # for nl in range(cst.PLAYGRID_H):
    #     for nc in range(cst.PLAYGRID_W):
    #         playwin.addch(nl + cst.PLAYAREA_VMAR,
    #                       (nc * playgrid_x_spc) + cst.PLAYAREA_HMAR,
    #                       cst.GRIDCH)
    prev_y = None
    timer.start()
    # breakpoint()
    # game loop
    while True:
        # strobe title and edges
        if timer.counter_comp(5):
            af.colour_wave(topwin,
                           cst.TITLE_L,
                           cst.TITLE_Y_OFFSET,
                           ((dw // 2) - (cst.TITLE_W // 2)),
                           color_offset,
                           len(cst.COLOR_L))
            color_offset = (color_offset + 1) % len(cst.COLOR_L)
            topwin.refresh()
        if timer.counter_comp(6):
            for y in [cst.PLAYAREA_VMAR - 1, cst.PLAYAREA_H - 3]:
                af.colour_strobe(playwin,
                                '-' * (playarea_x_w - (cst.PLAYAREA_HMAR * 2)),
                                y,
                                cst.PLAYAREA_HMAR,
                                color_offset,
                                3)
        if timer.counter_comp(32):
            for g in ghosts:
                g.tog_anim()
                g.draw()
        if timer.counter_comp(20):
            pacman.tog_anim()
        if timer.counter_comp(x_speed):
            if rnd.random() > 0:
                ghosts.append(vo.Ghost(playwin,
                                       timer,
                                       rnd.randint(20, 80),
                                       rnd.choice(cst.COLOR_L),
                                       rnd.randint(cst.PG_UY_BOUND,
                                                   cst.PG_DY_BOUND),
                                       playgrid_rx_bound,
                                       cst.PG_DY_BOUND,
                                       playgrid_rx_bound,
                                       cst.PG_UY_BOUND,
                                       playarea_x_mar))

        ghosts = [g for g in ghosts if g.update()]  # probably not very pythonic

        # usr input
        c = stdscr.getch()
        match c:
            case 113:  # q
                break
            case 258:  # arrow down
                prev_y = pacman.y
                pacman.move_y(0)
            case 259:  # arrow up
                prev_y = pacman.y
                pacman.move_y(1)
            case _:
                pass

        # draw hero
        pacman.draw(playwin,
                    curses.color_pair(1) | curses.A_BOLD)
        if prev_y is not None:  # clear prev position
            playwin.addch(prev_y,
                          pacman.x,  # this will break if x movement is introduced
                          cst.GRIDCH)
            prev_y = None  # block until next time

        playwin.refresh()
        # stdscr.refresh()
        timer.update()

    sys.exit(0)


def main():
    curses.wrapper(gameloop)
