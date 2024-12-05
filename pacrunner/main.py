import sys
import curses
from tickpy.ticker import IncTicker
from pacrunner import constants as cst
from pacrunner import visobj as vo
from pacrunner import artfunc as af
import random as rnd
import time
from typing import Literal


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
    # check for screen too small
    mh, mw = stdscr.getmaxyx()
    if mh < (cst.PLAYWIN_Y_OFFSET + cst.PLAYWIN_H):
        stdscr.addstr('sorry, screen too small! (vertical)')
        stdscr.refresh()
        time.sleep(10)
        exit(1)
    if mw < (100):
        stdscr.addstr('sorry, screen too small! (horizontal)')
        stdscr.refresh()
        time.sleep(10)
        exit(1)

    topwin = stdscr.subwin(cst.TITLE_H,
                           mw,
                           cst.TITLE_Y_OFFSET,
                           0)
    playwin_x_mar = mw // 6  # changing 8 to 6 here fucked up the ghost clearing
    playwin_x_w = 50 # int(mw - (playwin_x_mar * 2))  # 50 is a shorter track, preferable for now I think
    track_x_w = (playwin_x_w - (2 * cst.PLAYWIN_HMAR))
    # x_spc is really about hero move dist
    track_x_spc = track_x_w // (cst.TRACK_W - 1)  # this should be reconceptualised
    track_rx_bound = cst.PLAYWIN_HMAR + (cst.TRACK_W - 1) * track_x_spc
    playwin = stdscr.subwin(cst.PLAYWIN_H,
                            playwin_x_w,
                            cst.PLAYWIN_Y_OFFSET,
                            (mw // 2) - (playwin_x_w // 2))
    playwin.box()  # move to on transition from menu to game

    # init game loop
    # init vars
    # have an 'corner-of-eye difficulty (I like having it in a second screen region)'
    # implement startup menu with settings
    # implement pause
    # implement forward/backward movement of pacman
    # implement coins and powerups
    # implement sound
    # implement instructions and score at sides
    # implement yom yom every milestone
    # implement powerpill! on power pill
    # fix ghost anim
    # implement increasing track strobe speed with increasing difficulty
    diff_mod = 100
    x_speed = 500  # higher is slower
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
    # try alternative track animations as this might be too distracting
    # like moving - space - space
    upper_track = vo.SingleLineStrobe('─' * (playwin_x_w - (cst.PLAYWIN_HMAR * 2)),
                                      ticker=tck,
                                      animfreq=8,
                                      draw_y=cst.PLAYWIN_VMAR - 1,
                                      draw_x=cst.PLAYWIN_HMAR,
                                      color_offset=0,
                                      color_wrap=3)
    lower_track = vo.SingleLineStrobe('─' * (playwin_x_w - (cst.PLAYWIN_HMAR * 2)),
                                      ticker=tck,
                                      animfreq=8,
                                      draw_y=cst.PLAYWIN_H - 3,
                                      draw_x=cst.PLAYWIN_HMAR,
                                      color_offset=0,
                                      color_wrap=3)
    main_title = vo.MultiLineStrobe(cst.TITLE_L,
                                    ticker=tck,
                                    animfreq=5,
                                    normal_draw_y=cst.TITLE_Y_OFFSET,
                                    normal_draw_x=((mw // 2) - (cst.TITLE_W // 2)),
                                    color_offset=0,
                                    color_wrap=10)
    # game loop
    state: Literal[0,1] = 0
    playpress = 0
    menu_play = 'play (y)'
    menu_diff = 'difficulty: 100 ←→'
    stdscr.addstr(1, 0, 'sound: on (m)')
    stdscr.addstr(2, 0, 'quit (q)')
    while run:
        # state-independent actions
        # probably make anything which has it's own time senstive logic into an object with a timer reference
        # including strings
        match state:
            case cst.MENU:
                main_title.strobe(topwin)
                playwin.addstr(1, 1, 'play (y)', curses.color_pair(1))
                playwin.addstr(2, 1, 'difficulty: 100 ←→', curses.color_pair(7))  # LR arrows
                c = stdscr.getch()
                match c:
                    case 113:  # q
                        break
                    case curses.KEY_LEFT:
                        pass  # change difficulty
                    case curses.KEY_RIGHT:
                        pass
                    case 121: # y
                        playpress = 1  # state transition
                    case _:
                        pass
                if playpress == 1:
                    playwin.addstr(1, 1, cst.GRIDCH * len(menu_play))
                    playwin.addstr(2, 1, cst.GRIDCH * len(menu_diff))
                    playwin.refresh()
                    main_title.color_wrap = 6
                    state = cst.GAME  # state transition
            case cst.GAME:
                # strobe title and edges
                main_title.strobe(stdscr)
                upper_track.strobe(playwin)
                lower_track.strobe(playwin)
                # if tck.cmod(6):
                #     for y in [cst.PLAYWIN_VMAR - 1, cst.PLAYWIN_H - 3]:
                #         af.colour_strobe(playwin,
                #                          '-' * (playwin_x_w - (cst.PLAYWIN_HMAR * 2)),
                #                          y,
                #                          cst.PLAYWIN_HMAR,
                #                          color_offset,  # not working because not incremented - change to object
                #                          3)
                if tck.cmod(20):  # definite make this a part of player obj
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
                    if g.y == pacman.y and g.x == pacman.x:  # collision
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

            case _:
                pass

        topwin.refresh()
        playwin.refresh()
        # stdscr.refresh()
        tck.update()


def main():
    curses.wrapper(gameloop)
    print('gameover')
    sys.exit(0)
