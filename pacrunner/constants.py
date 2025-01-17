from pacrunner import artfunc as af
import curses
from enum import IntEnum, auto


# ExitCodes
class EC(IntEnum):
    EXIT_SUCCESS = 0
    EXIT_HORIZONTAL = auto()
    EXIT_VERTICAL = auto()


# FSM states
class S(IntEnum):
    MENU = 0
    GAME = auto()
    STARTUP = auto()
    GAMEOVER = auto()
    SCORES = auto()
    NAME = auto()
    PAUSE = auto()
    MANUAL = auto()

TITLE = r"""
__________                __________                                       ._.
\______   \_____     ____ \______   \ __ __   ____    ____    ____ _______ | |
 |     ___/\__  \  _/ ___\ |       _/|  |  \ /    \  /    \ _/ __ \\_  __ \| |
 |    |     / __ \_\  \___ |    |   \|  |  /|   |  \|   |  \\  ___/ |  | \/ \|
 |____|    (____  / \___  >|____|_  /|____/ |___|  /|___|  / \___  >|__|    __
                \/      \/        \/             \/      \/      \/         \/
"""
TITLE_W = af.art_width(TITLE)
TITLE_L = af.art2lines(TITLE)
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

HEROOPENCH = 'ᗧ'
HEROCLOSEDCH = 'ᗡ'
GRIDCH = ' '
EDGECH = '-'
GHOSTCH_L = ['ᗣ', 'ᙁ', 'ᙉ', 'ᑛ', 'ᑜ', 'ᗩ']
BIGCOINCH = 'Ø'
SMALLCOINCH = '·'
PILLCH = '⦷'  # or θ (note italics)

COLOR_L = [curses.COLOR_RED,
           curses.COLOR_YELLOW,
           curses.COLOR_GREEN,
           curses.COLOR_CYAN,
           curses.COLOR_BLUE,
           curses.COLOR_MAGENTA,
           curses.COLOR_WHITE]

TITLE_Y_OFFSET = 0

TRACK_W = 17
TRACK_H = 3
TITLE_PG_PAD = 2
PLAYWIN_Y_OFFSET = TITLE_Y_OFFSET + TITLE_H + TITLE_PG_PAD
PLAYWIN_VMAR = 3  # inclusive margin
PLAYWIN_H = TRACK_H + (PLAYWIN_VMAR * 2)
PLAYWIN_HMAR = 6
PLAYWIN_YO = PLAYWIN_H // 2
HERO_REL_X = 4
TRACK_REL_Y_BOUND = TRACK_H // 2
TRACK_DY_BOUND = PLAYWIN_YO + TRACK_REL_Y_BOUND
TRACK_UY_BOUND = PLAYWIN_YO - TRACK_REL_Y_BOUND
