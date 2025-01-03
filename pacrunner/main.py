import sys
import curses
from tickpy.ticker import IncTicker
from pacrunner import constants as cst
from pacrunner import visobj as vo
from pacrunner import artfunc as af
import random as rnd
import time
from typing import Literal
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'  # the most egregious bullshit I've ever encountered in programming
from pygame import mixer


# consider config dataclass for accessing
# system-specific (i.e. assinged with in main) constants
# when separating into sub windows and so on
def gameloop(stdscr):
    mixer.init()
    mixer.music.load('sound/intro.wav')
    death = mixer.Sound('sound/gameover.wav')
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
    playwin_x_mar = mw // 6
    playwin_x_w = 50 # int(mw - (playwin_x_mar * 2))  # 50 is a shorter track, preferable for now I think
    track_x_w = (playwin_x_w - (2 * cst.PLAYWIN_HMAR))
    # x_spc is really about hero move dist
    track_x_spc = track_x_w // (cst.TRACK_W - 1)  # this should be reconceptualised
    track_rx_bound = cst.PLAYWIN_HMAR + (cst.TRACK_W - 1) * track_x_spc
    playwin = stdscr.subwin(cst.PLAYWIN_H,
                            playwin_x_w,
                            cst.PLAYWIN_Y_OFFSET,
                            (mw // 2) - (playwin_x_w // 2))

    pmh, pmw = playwin.getmaxyx()
    msgbox = playwin.derwin(cst.PLAYWIN_H - 2,
                            20,
                            1,
                            15)

    # init game loop
    # init vars
    # have an 'corner-of-eye difficulty (I like having it in a second screen region)'
    # implement startup menu with settings
    # implement instructions and score at sides
    # implement yom yom every milestone
    # implement powerpill! on power pill
    # implement increasing track strobe speed with increasing difficulty
    diff_period = 2000  # higher is slower
    ghost_spawn_period = int(diff_period // 4)
    coin_spawn_period = int(diff_period // 2)  # note yet used
    diff_mod = 100  # can't remember if this is active

    init_player_x = (cst.HERO_REL_X * track_x_spc) + cst.PLAYWIN_HMAR
    tck = IncTicker(0.01)
    pacman = vo.Player(
        playwin,
        tck,
        cst.PLAYWIN_YO,
        init_player_x,
        curses.color_pair(1) | curses.A_BOLD,
        cst.TRACK_DY_BOUND,
        track_rx_bound - 1,
        cst.TRACK_UY_BOUND,
        cst.PLAYWIN_HMAR + 1
    )
    ghosts = []
    coins = []
    pill = []
    powerup = vo.Edible()
    powerup_time = 0
    run = True
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
    main_title = vo.MultiLineStrobe(cst.TITLE_L,  # type: ignore
                                    ticker=tck,
                                    animfreq=5,
                                    normal_draw_y=cst.TITLE_Y_OFFSET,
                                    normal_draw_x=((mw // 2) - (cst.TITLE_W // 2)),
                                    color_offset=0,
                                    color_wrap=10)
    # game loop
    state: Literal[0,1,2] = cst.MENU
    playpress = 0
    score = 0
    startup_finished = 0
    intro_finished = 0
    startup1 = 'for-elvira'
    startup2 = '<3'
    menu_play = 'play (y)'
    menu_diff = 'difficulty: 100 (←→)'
    menu_pause = 'pause (p)'
    flip_mute = 0
    mute = 0
    while run:
        if startup_finished:
            stdscr.addstr(1, 0, 'sound: on (m)')
            stdscr.addstr(3, 0, 'score: {}'.format(score))
            stdscr.addstr(2, 0, 'quit (q)')
            if not mixer.music.get_busy():
                intro_finished = 1
            if intro_finished:
                mixer.music.load('sound/mainloop.wav')
                mixer.music.play()
                intro_finished = 0

        if flip_mute:
            if not mute:
                mixer.pause()
                mute = 1
            if mute:
                mixer.unpause()
                mute = 0
            flip_mute = 0

        # probably make anything which has it's own time senstive logic into an object with a timer reference
        # including strings
        match state:
            case cst.STARTUP:
                stdscr.addstr(int(mh // 2), int(mw // 2) - int(len(startup1) // 2), startup1)
                if tck.counter > 200:
                    stdscr.addstr(int(mh // 2), int(mw // 2) + int(len(startup1) // 2) + 1, startup2)
                if tck.counter > 300:
                    stdscr.clear()
                if tck.counter > 400:
                    state = cst.MENU
                    mixer.music.play()
                    startup_finished = 1
            case cst.MENU:
                main_title.strobe(topwin)
                playwin.addstr(1, int(playwin_x_w // 2) - int(len(menu_play) // 2) - 2, menu_play, curses.color_pair(7))
                playwin.addstr(2, int(playwin_x_w // 2) - int(len(menu_diff) // 2) - 2, menu_diff, curses.color_pair(7))  # LR arrows
                c = stdscr.getch()
                match c:
                    case 113:  # q
                        break
                    case 109:  # m
                        flip_mute = 1
                    case curses.KEY_LEFT:
                        pass  # change difficulty
                    case curses.KEY_RIGHT:
                        pass
                    case 121: # y
                        playpress = 1  # state transition
                    case _:
                        pass
                if playpress == 1:
                    playwin.addstr(1, int(playwin_x_w // 2) - int(len(menu_play) // 2) - 2, cst.GRIDCH * len(menu_play))
                    playwin.addstr(2, int(playwin_x_w // 2) - int(len(menu_diff) // 2) - 2, cst.GRIDCH * len(menu_diff))
                    playwin.refresh()
                    main_title.color_wrap = 6
                    playwin.box()
                    state = cst.GAME  # state transition
            case cst.GAME:
                # strobe title and edges
                main_title.strobe(stdscr)
                upper_track.strobe(playwin)
                lower_track.strobe(playwin)

                if tck.cmod(diff_period):
                    x_speed = (diff_period - diff_mod) if diff_mod > 100 else 100  # first attempt at increasing difficulty
                    tck.cmod(diff_period)
                    ghost_spawn_period = int(diff_period // 4)
                    tck.cmod(ghost_spawn_period)
                    coin_spawn_period = int(diff_period // 2)
                    tck.cmod(coin_spawn_period)
                if tck.cmod(ghost_spawn_period):
                    if rnd.random() > 0.2:
                        ghosts.append(vo.Ghost(playwin,
                                               tck,
                                               powerup,
                                               rnd.randint(20, 80),
                                               rnd.randint(29, 33),
                                               rnd.choice(cst.COLOR_L),
                                               [5,7],
                                               rnd.randint(cst.TRACK_UY_BOUND,
                                                           cst.TRACK_DY_BOUND),
                                               track_rx_bound,
                                               cst.TRACK_DY_BOUND,
                                               track_rx_bound,
                                               cst.TRACK_UY_BOUND,
                                               cst.PLAYWIN_HMAR))
                # things with the same period won't be checked...
                if tck.cmod(300):
                    if rnd.random() > 0.2:
                        coins.append(vo.CoinRun(playwin,
                                                tck,
                                                60,
                                                rnd.randint(cst.TRACK_UY_BOUND,
                                                            cst.TRACK_DY_BOUND),
                                                track_rx_bound,
                                                cst.PLAYWIN_HMAR,
                                                track_rx_bound,
                                                curses.color_pair(2)))
                    if not pill and powerup_time < (tck.counter - 2500):
                        if rnd.random() > 0.1:
                            pill.append(vo.Pill(playwin,
                                                tck,
                                                60,
                                                rnd.randint(cst.TRACK_UY_BOUND,
                                                            cst.TRACK_DY_BOUND),
                                                track_rx_bound,
                                                cst.PLAYWIN_HMAR,
                                                track_rx_bound,
                                                [curses.color_pair(7),
                                                 curses.color_pair(5)]))


                playwin.addch(cst.TRACK_UY_BOUND,
                              track_rx_bound,
                              '░',
                              curses.color_pair(7))
                playwin.addch(cst.TRACK_UY_BOUND + 1,
                              track_rx_bound,
                              '░',
                              curses.color_pair(7))
                playwin.addch(cst.TRACK_UY_BOUND + 2,
                              track_rx_bound,
                              '░',
                              curses.color_pair(7))

                # handle collisions
                tmp_ghosts = []
                for g in ghosts:
                    gu = g.update()
                    if g.y == pacman.y and g.x == pacman.x:
                        if powerup.eatme:
                            g.clear()
                            score += 10
                        else:  # state transition
                            msgbox.bkgdset(' ', curses.color_pair(0))
                            msgbox.erase()
                            msgbox.box()
                            msgbox.addstr(3, 5, 'GAME OVER!')
                            msgbox.refresh()
                            mixer.music.stop()
                            state = cst.GAMEOVER
                    elif gu:
                        tmp_ghosts.append(g)
                ghosts = tmp_ghosts

                tmp_coins = []
                for cr in coins:
                    if cr.update():
                        tmp_coins.append(cr)
                    if pacman.y == cr.y and pacman.x in cr.xl:
                        cv = cr.collect_at(pacman.x)
                        match cv:
                            case 1:
                                score += 10
                            case 2:
                                score += 50
                            case _:
                                pass
                coins = tmp_coins

                tmp_pill = []
                for p in pill:
                    if p.update():
                        tmp_pill.append(p)
                    if p.y == pacman.y and p.x == pacman.x:
                        powerup.eatme = True
                        # 16s, plus some random element to keep you on your toes
                        powerup_time = tck.counter + 1600 + rnd.randint(-200, 200)
                        p.clear()
                        tmp_pill = []
                pill = tmp_pill

                if tck.counter > powerup_time:
                    powerup.eatme = False

                # usr input
                c = stdscr.getch()
                match c:
                    case 112:  # p - pause
                        msgbox.bkgdset(' ', curses.color_pair(0))
                        msgbox.erase()
                        msgbox.box()
                        msgbox.addstr(3, 7, 'PAUSE')
                        msgbox.refresh()
                        while True:
                            c = stdscr.getch()
                            if c == 112:
                                break
                            if c == 113:
                                run = False
                                break
                        msgbox.erase()
                        msgbox.clear()
                        msgbox.refresh()
                    case 113:  # q
                        break
                    case 109:  # m
                        flip_mute = 1
                    case curses.KEY_LEFT:
                        pacman.move_x(0)
                    case curses.KEY_RIGHT:
                        pacman.move_x(1)
                    case curses.KEY_DOWN:
                        pacman.move_y(0)
                    case curses.KEY_UP:  # arrow up
                        pacman.move_y(1)
                    case _:
                        pass

                pacman.update()

                if tck.cmod(100):  # 1s
                    score += 1

            case cst.GAMEOVER:
                c = stdscr.getch()
                match c:
                    case 113:  # q
                        run = False
                # while True:
                #     c = stdscr.getch()
                #     if c == 112:
                #         break
                #     if c == 113:
                #         run = False
                #         break
                # msgbox.erase()
                # msgbox.clear()
                # msgbox.refresh()

                

        topwin.refresh()
        playwin.refresh()
        # stdscr.refresh()
        tck.update()


def main():
    curses.wrapper(gameloop)
    print('gameover')
    sys.exit(0)
