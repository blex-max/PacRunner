import utility as u
import curses

# hero_open = 'C'
# hero_open_alt = '◔'
# hero_closed = '◯'

TITLE = r"""
__________                __________                                       ._.
\______   \_____     ____ \______   \ __ __   ____    ____    ____ _______ | |
 |     ___/\__  \  _/ ___\ |       _/|  |  \ /    \  /    \ _/ __ \\_  __ \| |
 |    |     / __ \_\  \___ |    |   \|  |  /|   |  \|   |  \\  ___/ |  | \/ \|
 |____|    (____  / \___  >|____|_  /|____/ |___|  /|___|  / \___  >|__|    __
                \/      \/        \/             \/      \/      \/         \/
"""
TITLE_W = u.art_width(TITLE)
TITLE_L = u.art2lines(TITLE)
TITLE_H = len(TITLE_L)

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

HEROCH = 'C'
GRIDCH = '·'

RAINBOW_L = [curses.COLOR_RED, curses.COLOR_YELLOW, curses.COLOR_GREEN, curses.COLOR_CYAN, curses.COLOR_BLUE, curses.COLOR_MAGENTA]

PLAYGRID_W = 19
PLAYGRID_H = 7
OFFSET_FROM_TITLE = 2
PLAYGRID_Y_OFFSET = TITLE_H + OFFSET_FROM_TITLE
PLAYGRID_YC = TITLE_H + OFFSET_FROM_TITLE + (PLAYGRID_H // 2)
HERO_REL_X = 5
PG_REL_Y_BOUND = PLAYGRID_H // 2
PG_ABS_PY_BOUND = PLAYGRID_YC + PG_REL_Y_BOUND
PG_ABS_NY_BOUND = PLAYGRID_YC - PG_REL_Y_BOUND
