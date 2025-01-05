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
import pickle
from os import path


# consider config dataclass for accessing
# system-specific (i.e. assinged with in main) constants
# when separating into sub windows and so on
def gameloop(stdscr):
    # very fragile high scores
    if not path.exists('sc.dat'):
        high_scores = [('---', 0) for x in range(0,6)]
        with open('sc.dat', 'wb') as f:
            pickle.dump(high_scores, f)
    else:
        with open('sc.dat', 'rb') as f:
            high_scores: list[tuple[str, int]] = pickle.load(f)
        high_scores = high_scores[0:6]
    high_scores = sorted(high_scores, key=lambda x: x[1], reverse=True)

    # sound init
    mixer.init()
    mixer.music.load('sound/intro.wav')
    music_vol = mixer.music.get_volume()  # default seems fine
    death = mixer.Sound('sound/gameover.wav')
    pill_sound = mixer.Sound('sound/pacman_eatfruit.wav')
    eatghost_sound = mixer.Sound('sound/pacman_eatghost.wav')
    sound_vol = 0.55
    death.set_volume(sound_vol)
    pill_sound.set_volume(0.15)
    eatghost_sound.set_volume(0.15)

    # curses init
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
        time.sleep(3)
        exit(1)
    if mw < (100):
        stdscr.addstr('sorry, screen too small! (horizontal)')
        stdscr.refresh()
        time.sleep(3)
        exit(1)

    curses.set_escdelay(1)
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
    playwin.attrset(curses.color_pair(4))
    pmh, pmw = playwin.getmaxyx()
    msgbox = playwin.derwin(cst.PLAYWIN_H - 2,
                            23,
                            1,
                            13)
    msgbox.attrset(curses.color_pair(4))

    # init game loop
    # init vars
    # have an 'corner-of-eye difficulty (I like having it in a second screen region)'
    # implement startup menu with settings
    # implement instructions and score at sides
    # implement yom yom every milestone
    # implement powerpill! on power pill
    # implement increasing track strobe speed with increasing difficulty
    diff_period = 600  # higher is slower
    diff_multiplier = 1600
    ghost_spawn_period = int(diff_multiplier // 4)
    coin_spawn_period = int(diff_multiplier // 7)
    diff_mod = 55
    item_speed = 60

    init_player_x = (cst.HERO_REL_X * track_x_spc) + cst.PLAYWIN_HMAR
    tck = IncTicker(0.01)
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
    hiscore_sign = vo.SingleLineStrobe('HISCORE!',
                                       tck,
                                       30,
                                       draw_y=1,
                                       draw_x=8,
                                       color_offset=3,
                                       color_wrap=5,
                                       default_attr=curses.A_UNDERLINE)
    # game loop
    state: Literal[0,1,2,3,4,5,6,7] = cst.STARTUP  # should be intro
    score = 0
    startup_finished = 0  # for quickstart, 1
    intro_finished = 0
    bell_played = 0
    startup1 = 'for-elvira'
    startup2 = '<3'
    menu_play = 'play! (y)'
    # menu_diff = 'difficulty: 100 (←→)'
    menu_scores = 'scores! (s)'
    menu_manual = 'instructions (i)'
    flip_mute = 0
    mute = 0
    name: str = '???'
    init_game = 1
    move_inst = '↑↓←→ - move!'
    coin_inst = '{}{} - get the coins!'.format(cst.SMALLCOINCH, cst.BIGCOINCH)
    ghost_inst = 'ᗣ - avoid the ghosts!'
    pill_inst = '⦷ - now eat the ghosts!'
    pill_ind = 'powerpill!'
    pw_cntpos = int(playwin_x_w // 2) + 1
    while run:
        if startup_finished:
            stdscr.addstr(cst.PLAYWIN_Y_OFFSET + cst.PLAYWIN_H + 1, (mw // 2) - (playwin_x_w // 2), 'sound: {} (m) '.format('off' if mute else 'on'), curses.color_pair(7))
            stdscr.addstr(cst.PLAYWIN_Y_OFFSET + cst.PLAYWIN_H + 1, (mw // 2) - (playwin_x_w // 2) + 21, '(ESC): quit', curses.color_pair(7))
            stdscr.addstr(cst.PLAYWIN_Y_OFFSET + cst.PLAYWIN_H + 1, (mw // 2) - (playwin_x_w // 2) + 40, '(p): pause', curses.color_pair(7))
            stdscr.addstr(cst.PLAYWIN_Y_OFFSET, 2 + (mw // 2) - (playwin_x_w // 2), 'score: {}'.format(score), curses.color_pair(7))

            # debug displays
            # stdscr.addstr(8, 0, 'diff_multiplier: {}  '.format(diff_multiplier))
            # stdscr.addstr(9, 0, 'ghost_spawn_period: {}  '.format(ghost_spawn_period))
            # stdscr.addstr(10, 0, 'coin_spawn_period: {}  '.format(coin_spawn_period))
            # stdscr.addstr(11, 0, 'diff_mod: {}  '.format(diff_mod))
            # stdscr.addstr(12, 0, 'coin_speed: {}  '.format(item_speed))

            if not mixer.music.get_busy() and not intro_finished:
                mixer.music.load('sound/mainloop.wav')
                mixer.music.play()
                intro_finished = 1

        if flip_mute:
            if not mute:
                mixer.music.set_volume(0)
                death.set_volume(0)
                pill_sound.set_volume(0)
                eatghost_sound.set_volume(0)
                mute = 1
            elif mute:
                mixer.music.set_volume(music_vol)
                death.set_volume(sound_vol)
                pill_sound.set_volume(0.15)
                eatghost_sound.set_volume(0.15)
                mute = 0
            flip_mute = 0

        # probably make anything which has it's own time senstive logic into an object with a timer reference
        # including strings
        match state:
            case cst.STARTUP:
                stdscr.addstr(int(mh // 2), int(mw // 2) - 1 - int(len(startup1) // 2), startup1, curses.color_pair(7))
                if tck.counter > 200:
                    stdscr.addstr(int(mh // 2), int(mw // 2) + int(len(startup1) // 2), startup2, curses.color_pair(7))
                    if not bell_played:
                        pill_sound.play()
                        bell_played = 1
                if tck.counter > 300:
                    stdscr.clear()
                if tck.counter > 400:
                    state = cst.MENU
                    mixer.music.play()
                    startup_finished = 1

            case cst.MENU:
                main_title.color_wrap = 10
                main_title.strobe(topwin)
                playwin.addstr(1, pw_cntpos - int(len(menu_play) // 2), menu_play, curses.color_pair(7))
                # playwin.addstr(2, pw_cntpos - int(len(menu_diff) // 2) - 2, menu_diff, curses.color_pair(7))  # LR arrows
                playwin.addstr(2, pw_cntpos - int(len(menu_scores) // 2), menu_scores, curses.color_pair(7))
                playwin.addstr(3, pw_cntpos - int(len(menu_manual) // 2), menu_manual, curses.color_pair(7))
                c = stdscr.getch()
                match c:
                    case 27:  # q
                        break
                    case 109:  # m
                        flip_mute = 1
                    case curses.KEY_LEFT:
                        pass  # change difficulty
                    case curses.KEY_RIGHT:
                        pass
                    case 121: # y
                        playwin.addstr(1, pw_cntpos - int(len(menu_play) // 2), cst.GRIDCH * len(menu_play))
                        # playwin.addstr(2, pw_cntpos - int(len(menu_diff) // 2) - 2, cst.GRIDCH * len(menu_diff))
                        playwin.addstr(2, pw_cntpos - int(len(menu_scores) // 2), cst.GRIDCH * len(menu_scores))
                        playwin.addstr(3, pw_cntpos - int(len(menu_manual) // 2), cst.GRIDCH * len(menu_manual))
                        playwin.refresh()
                        main_title.color_wrap = 6
                        playwin.box()
                        init_game = 1
                        state = cst.GAME  # state transition
                    case 115:  # s
                        playwin.addstr(1, pw_cntpos - int(len(menu_play) // 2), cst.GRIDCH * len(menu_play))
                        # playwin.addstr(2, pw_cntpos - int(len(menu_diff) // 2) - 2, cst.GRIDCH * len(menu_diff))
                        playwin.addstr(2, pw_cntpos - int(len(menu_scores) // 2), cst.GRIDCH * len(menu_scores))
                        playwin.addstr(3, pw_cntpos - int(len(menu_manual) // 2), cst.GRIDCH * len(menu_manual))
                        playwin.refresh()
                        state = cst.SCORES
                    case 105:  # instructions
                        playwin.addstr(1, pw_cntpos - int(len(menu_play) // 2), cst.GRIDCH * len(menu_play))
                        # playwin.addstr(2, pw_cntpos - int(len(menu_diff) // 2) - 2, cst.GRIDCH * len(menu_diff))
                        playwin.addstr(2, pw_cntpos - int(len(menu_scores) // 2), cst.GRIDCH * len(menu_scores))
                        playwin.addstr(3, pw_cntpos - int(len(menu_manual) // 2), cst.GRIDCH * len(menu_manual))
                        playwin.refresh()  # unnecessary refresh?
                        state = cst.MANUAL
                    case _:
                        pass

            case cst.GAME:
                if init_game:
                    score = 0
                    ghosts = []
                    coins = []
                    pill = []
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
                    init_game = 0
                # strobe title and edges
                main_title.strobe(stdscr)
                upper_track.strobe(playwin)
                lower_track.strobe(playwin)

                if tck.cmod(diff_period):
                    if diff_multiplier > 300:
                        diff_multiplier = diff_multiplier - diff_mod
                        ghost_spawn_period = int(diff_multiplier // 4) if ghost_spawn_period > 100 else 100
                        # tck.cmod(ghost_spawn_period)  # unnecessary?
                        coin_spawn_period = int(diff_multiplier // 7) if coin_spawn_period > 50 else 50
                if tck.cmod(diff_period * 2):
                    item_speed = item_speed - 1 if item_speed > 30 else 30
                    for coin in coins:
                        coin._mvfreq = item_speed
                if tck.cmod(ghost_spawn_period):
                    if rnd.random() > 0.2:
                        ghosts.append(vo.Ghost(playwin,
                                               tck,
                                               powerup,
                                               rnd.randint(10, 40),  # lower = faster
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
                if tck.cmod(coin_spawn_period):
                    if rnd.random() > 0.2:  # max ghosts would be good
                        coins.append(vo.CoinRun(playwin,
                                                tck,
                                                item_speed,
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
                                                item_speed,
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
                    if g.y == pacman.y and g.x == pacman.x:
                        if powerup.eatme:
                            eatghost_sound.play()
                            g.clear()
                            score += 10
                        else:  # state transition
                            g.clear()
                            pacman.clearall()
                            msgbox.bkgdset(' ', curses.color_pair(0))
                            msgbox.erase()
                            msgbox.box()
                            msgbox.refresh()
                            mixer.music.stop()
                            mixer.music.rewind()
                            death.play()
                            if score > high_scores[-1][1]:
                                nch_entered = 0
                                entry_finished = 0
                                state = cst.NAME
                            else:
                                state = cst.GAMEOVER
                            continue  # skip rest of loop for clean transition?
                    else:
                        if g.update():
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
                        pill_sound.play()
                        powerup.eatme = True
                        playwin.addstr(0, playwin_x_w - len(pill_ind) - 2, pill_ind, curses.color_pair(7))
                        # 12s, plus some random element to keep you on your toes
                        powerup_time = tck.counter + 1200 + rnd.randint(-200, 200)
                        p.clear()
                        tmp_pill = []
                pill = tmp_pill

                if tck.counter > powerup_time:
                    if powerup.eatme:
                        playwin.addstr(0, playwin_x_w - len(pill_ind) - 2, '─'*len(pill_ind), curses.color_pair(4))
                    powerup.eatme = False

                # usr input
                c = stdscr.getch()
                match c:
                    case 112:  # p - pause
                        msgbox.bkgdset(' ', curses.color_pair(0))
                        msgbox.erase()
                        mixer.music.pause()
                        state = cst.PAUSE
                        continue
                    case 27:  # q
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

            case cst.SCORES:
                main_title.strobe(topwin)
                playwin.addstr(1, int((playwin_x_w // 2) - 4), '{}: {}'.format(high_scores[0][0][0:3].upper(), str(high_scores[0][1])), curses.color_pair(2) | curses.A_BOLD)
                for i, s in enumerate(high_scores[1:]):
                    playwin.addstr(2 + i, int((playwin_x_w // 2) - 4), '{}: {}'.format(s[0][0:3].upper(), str(s[1])), curses.color_pair(7))
                playwin.addstr(i + 4, int((playwin_x_w // 2) - 4), '(o): ≡←', curses.color_pair(7))
                c = stdscr.getch()
                match c:
                    case 109:
                        flip_mute = 1
                    case 27:
                        break
                    case 111:
                        playwin.clear()
                        playwin.erase()
                        playwin.refresh()
                        state = cst.MENU
                    

            case cst.GAMEOVER:
                pacman.clearall()
                msgbox.box()  # no idea why it's so hard to clear pacman
                msgbox.addstr(3, 7, 'GAME OVER!', curses.color_pair(7))
                msgbox.addstr(5, 6, '(r) ↻', curses.color_pair(7))
                msgbox.addstr(5, 13, '(o) ≡', curses.color_pair(7))
                msgbox.refresh()
                c = stdscr.getch()
                match c:
                    case 109:  # m
                        flip_mute = 1
                    case 27:  # q
                        run = False
                    case 114:  # r
                        # restart!
                        msgbox.erase()
                        msgbox.clear()
                        msgbox.refresh()
                        playwin.erase()
                        playwin.clear()
                        playwin.box()
                        playwin.refresh()
                        mixer.music.play()
                        init_game = 1
                        state = cst.GAME
                    case 111:  # o
                        # go to menu
                        msgbox.erase()
                        msgbox.clear()
                        msgbox.refresh()
                        playwin.erase()
                        playwin.clear()
                        playwin.refresh()
                        mixer.music.play()
                        state = cst.MENU
                    case _:
                        pass

            case cst.NAME:
                pacman.clearall()
                msgbox.box()
                hiscore_sign.strobe(msgbox)
                msgbox.addstr(3, 8, 'NAME:{}'.format(name), curses.color_pair(7))
                if not entry_finished:
                    msgbox.addstr(5, 9, '(↵): ✓', curses.color_pair(7))
                else:
                    msgbox.addstr(5, 6, '(r) ↻', curses.color_pair(7))
                    msgbox.addstr(5, 13, '(o) ≡', curses.color_pair(7))
                c = stdscr.getch()
                if 96 < c < 122 and not entry_finished:
                    if nch_entered == 0:
                        name = chr(c).upper() + name[1:]
                    elif nch_entered == 1:
                        name = name[0] + chr(c).upper() + name[2]
                    elif nch_entered == 2:
                        name = name[0:2] + chr(c).upper()
                    nch_entered += 1
                elif c == 10:
                    entry_finished = 1
                    msgbox.addstr(5, 6, '        ')
                elif c == 27:
                    run = False  # finish iteration
                elif c == 114:  # r
                    # restart!
                    msgbox.erase()
                    msgbox.clear()
                    msgbox.refresh()
                    playwin.erase()
                    playwin.clear()
                    playwin.box()
                    playwin.refresh()
                    mixer.music.play()
                    init_game = 1
                    state = cst.GAME
                elif c == 111:  # o
                    # go to menu
                    msgbox.erase()
                    msgbox.clear()
                    msgbox.refresh()
                    playwin.erase()
                    playwin.clear()
                    playwin.refresh()
                    mixer.music.play()
                    state = cst.MENU
                elif c == 109:  # m
                    flip_mute = 1

                # state exit block
                if not run or state != cst.NAME:
                    high_scores.append((name, score))
                    high_scores = sorted(high_scores, key=lambda x: x[1], reverse=True)
                    high_scores.pop()
                    with open('sc.dat', 'wb') as f:
                        pickle.dump(high_scores, f)
                msgbox.refresh()

            case cst.PAUSE:
                if score > high_scores[-1][1]:
                    hiscore_sign.strobe(msgbox)
                msgbox.box()
                msgbox.addstr(3, 9, 'PAUSE', curses.color_pair(7))
                msgbox.addstr(5, 8, '(o): ≡←', curses.color_pair(7))
                msgbox.refresh()
                c = stdscr.getch()
                match c:
                    case 109:  # m
                        flip_mute = 1
                    case 112:  # p
                        mixer.music.unpause()
                        msgbox.erase()
                        msgbox.clear()
                        state = cst.GAME
                    case 27:
                        run = False
                        break
                    case 111:  # o
                        # go to menu
                        msgbox.erase()
                        msgbox.clear()
                        msgbox.box()
                        msgbox.refresh()
                        if score > high_scores[-1][1]:
                            state = cst.NAME
                            entry_finished = 0
                            nch_entered = 0  # states often could do with init and exit blocks
                        else:
                            playwin.erase()
                            playwin.clear()
                            playwin.refresh()
                            mixer.music.stop()
                            mixer.music.rewind()
                            mixer.music.play()
                            score = 0
                            state = cst.MENU
                msgbox.refresh()

            case cst.MANUAL:
                main_title.strobe(topwin)
                playwin.addstr(2, pw_cntpos - int(len(move_inst) // 2), move_inst, curses.color_pair(7))
                playwin.addstr(3, pw_cntpos - int(len(coin_inst) // 2), coin_inst, curses.color_pair(7))
                playwin.addstr(4, pw_cntpos - int(len(ghost_inst) // 2), ghost_inst, curses.color_pair(7))
                playwin.addstr(5, pw_cntpos - int(len(pill_inst) // 2), pill_inst, curses.color_pair(7))
                playwin.addstr(7, pw_cntpos - int(3), '(o): ≡←', curses.color_pair(7))
                c = stdscr.getch()
                match c:
                    case 27:  # ESC
                        break
                    case 109:  # m
                        flip_mute = 1
                    case 111:
                        playwin.clear()
                        state = cst.MENU
                    

        topwin.refresh()
        playwin.refresh()
        # stdscr.refresh()
        tck.update()


def main():
    curses.wrapper(gameloop)
    print('thanks for playing!')
    sys.exit(0)
