import time
import sys
import curses

hero_open = 'C'
hero_open_alt = '◔'
hero_closed = '◯'

PACMAN = r"""
__________                __________                                       ._.
\______   \_____     ____ \______   \ __ __   ____    ____    ____ _______ | |
 |     ___/\__  \  _/ ___\ |       _/|  |  \ /    \  /    \ _/ __ \\_  __ \| |
 |    |     / __ \_\  \___ |    |   \|  |  /|   |  \|   |  \\  ___/ |  | \/ \|
 |____|    (____  / \___  >|____|_  /|____/ |___|  /|___|  / \___  >|__|    __
                \/      \/        \/             \/      \/      \/         \/
"""

YOMYOM = r"""
_____.___.             _____.___.             ._.
\__  |   | ____   _____\__  |   | ____   _____| |
 /   |   |/  _ \ /     \/   |   |/  _ \ /     | |
 \____   (  <_> |  Y Y  \____   (  <_> |  Y Y  \|
 / ______|\____/|__|_|  / ______|\____/|__|_|  __
 \/                   \/\/                   \/\/
"""

POWERPILL = r"""
__________                              __________ .__ .__   .__  ._.
\______   \ ____ __  _  __  ____ _______\______   \|__||  |  |  | | |
 |     ___//  _ \\ \/ \/ /_/ __ \\_  __ \|     ___/|  ||  |  |  | | |
 |    |   (  <_> )\     / \  ___/ |  | \/|    |    |  ||  |__|  |__\|
 |____|    \____/  \/\_/   \___  >|__|   |____|    |__||____/|____/__
                               \/                                  \/
"""

COLOR_L = [curses.COLOR_RED, curses.COLOR_YELLOW, curses.COLOR_GREEN, curses.COLOR_CYAN, curses.COLOR_BLUE, curses.COLOR_MAGENTA]


def rainbow_wave(stdscr, text, y_pos, init_x, colors, color_offset):
    for i, char in enumerate(text):
        color_index = (i + color_offset) % len(colors)
        stdscr.addch(y_pos, init_x + i, char, curses.color_pair(color_index + 1) | curses.A_BOLD)


def rainbow_wave_ml(stdscr, line_l, init_y, init_x, colors, color_offset):
    for i, line in enumerate(line_l):
        rainbow_wave(stdscr, line, init_y + i, init_x, colors, color_offset)


def art_width(ml_str):
    return len(ml_str.strip().splitlines()[0])


def art2lines(ml_str):
    return ml_str.strip().splitlines()


LEN_PACMAN = art_width(PACMAN)
PACMAN_L = art2lines(PACMAN)


# now strobe it to the beat! (see nextdoor window)
def main(stdscr):
    stdscr.clear()
    stdscr.nodelay(True)
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()
    for i, color in enumerate(COLOR_L):
        curses.init_pair(i + 1, color, -1)  # -1 for default background
    dh, dw = stdscr.getmaxyx()
    dheady = 0

    color_offset = 1
    while True:
        c = stdscr.getch()
        if c == ord('q'):
            break
        rainbow_wave_ml(stdscr, PACMAN_L, dheady, ((dw // 2) - (LEN_PACMAN // 2)), COLOR_L, color_offset)
        color_offset = (color_offset + 1) % len(COLOR_L)

        stdscr.refresh()
        time.sleep(0.05)

    sys.exit(0)


curses.wrapper(main)
