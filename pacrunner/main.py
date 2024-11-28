import sys
import curses
from tickpy.ticker import IncTicker
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
    _, dw = stdscr.getmaxyx()
    topwin = stdscr.subwin(cst.TITLE_H,
                           dw,
                           cst.TITLE_Y_OFFSET,
                           0)
    playwin_x_mar = dw // 6  # changing 8 to 6 here fucked up the ghost clearing
    playwin_x_w = 50 # int(dw - (playwin_x_mar * 2))  # a shorter track would be preferable for now I think
    track_x_w = (playwin_x_w - (2 * cst.PLAYWIN_HMAR))
    # x_spc is really about hero move dist
    track_x_spc = track_x_w // (cst.TRACK_W - 1)  # this should be reconceptualised
    track_rx_bound = cst.PLAYWIN_HMAR + (cst.TRACK_W - 1) * track_x_spc
    playwin = stdscr.subwin(cst.PLAYWIN_H,
                            playwin_x_w,
                            cst.PLAYWIN_Y_OFFSET,
                            playwin_x_mar)
    playwin.box()

    # init game loop
    # init vars
    # have an 'corner-of-eye difficulty (I like having it in a second screen region)'
    diff_mod = 100
    x_speed = 1000  # higher is slower
    init_player_x = (cst.HERO_REL_X * track_x_spc) + cst.PLAYWIN_HMAR
    pacman = vo.Player(
        cst.PLAYWIN_YO,
        init_player_x,
        cst.TRACK_DY_BOUND,
        init_player_x,
        cst.TRACK_UY_BOUND
    )
    ghosts = []
    color_offset = 1
    # draw track - might be visually nicer without
    # for nl in range(cst.track_H):
    #     for nc in range(cst.track_W):
    #         playwin.addch(nl + cst.PLAYAREA_VMAR,
    #                       (nc * track_x_spc) + cst.PLAYAREA_HMAR,
    #                       cst.GRIDCH)
    prev_y = None
    run = True
    tck = IncTicker(0.01)
    # breakpoint()
    # game loop
    while run:
        # strobe title and edges
        if tck.cmod(5):
            af.colour_wave(topwin,
                           cst.TITLE_L,
                           cst.TITLE_Y_OFFSET,
                           ((dw // 2) - (cst.TITLE_W // 2)),
                           color_offset,
                           len(cst.COLOR_L))
            color_offset = (color_offset + 1) % len(cst.COLOR_L)
            topwin.refresh()
        if tck.cmod(6):
            for y in [cst.PLAYWIN_VMAR - 1, cst.PLAYWIN_H - 3]:
                af.colour_strobe(playwin,
                                 '-' * (playwin_x_w - (cst.PLAYWIN_HMAR * 2)),
                                 y,
                                 cst.PLAYWIN_HMAR,
                                 color_offset,
                                 3)
        if tck.cmod(20):
            pacman.tog_anim()
        if tck.cmod(x_speed):
            if rnd.random() > 0.2:
                ghosts.append(vo.Ghost(playwin,
                                       tck,
                                       rnd.randint(20, 80),  # ghosts need to go faster
                                       rnd.randint(29, 33),
                                       rnd.choice(cst.COLOR_L),
                                       rnd.randint(cst.TRACK_UY_BOUND,
                                                   cst.TRACK_DY_BOUND),
                                       track_rx_bound,
                                       cst.TRACK_DY_BOUND,
                                       track_rx_bound,
                                       cst.TRACK_UY_BOUND,
                                       cst.PLAYWIN_HMAR))
            else:
                x_speed = (x_speed - diff_mod) if x_speed > 100 else 100  # first attempt at increasing difficulty
                tck.cmod(x_speed)
        tmp_ghosts = []
        for g in ghosts:
            if g.update():
                tmp_ghosts.append(g)
            if g.y == pacman.y and g.x == pacman.x:
                run = False
        ghosts = tmp_ghosts

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
        tck.update()


def main():
    curses.wrapper(gameloop)
    print('gameover')
    sys.exit(0)
