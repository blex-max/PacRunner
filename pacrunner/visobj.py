# if this gets complicated, consider parent class, or composing move, draw, obj
# abstract classes and so on
from pacrunner import constants as cst
from tickpy.ticker import IncTicker
import curses
from random import sample


class Player:
    def __init__(self,
                 init_y,
                 init_x,
                 dy_bound,
                 rx_bound,
                 uy_bound=0,
                 lx_bound=0):
        self._default_anim_pair = (cst.HEROCLOSEDCH, cst.HEROOPENCH)
        self._togidx = 0
        self.ch = self._default_anim_pair[0]
        self.y = init_y
        self.x = init_x
        self.dy_bound = dy_bound
        self.rx_bound = rx_bound
        self.uy_bound = uy_bound
        self.lx_bound = lx_bound

    def tog_anim(self):
        self._togidx = (self._togidx + 1) % len(self._default_anim_pair)
        self.ch = self._default_anim_pair[self._togidx]

    def move_y(self, dir):
        if dir:
            if self.y > self.uy_bound:
                self.y -= 1
        else:
            if self.y < self.dy_bound:
                self.y += 1

    def draw(self, stdscr, attr = 0):
        stdscr.addch(self.y,
                     self.x,
                     self.ch,
                     attr)

    def move_y_draw(self, stdscr, dir, attr = 0):
        self.move_y(dir)
        self.draw(stdscr, attr)


class Ghost:
    def __init__(self,
                 stdscr,
                 ticker: IncTicker,
                 mvfreq: int,
                 animfreq: int,
                 col: int,
                 init_y,
                 init_x,
                 dy_bound,
                 rx_bound,
                 uy_bound=0,
                 lx_bound=0):
        self._anims = sample(cst.GHOSTCH_L, 2)
        self._togidx = 0
        self.ch = self._anims[self._togidx]
        self.__stdscr = stdscr
        self.__ticker_ref = ticker
        self._mvfreq = mvfreq
        self._animfreq = animfreq
        self.col = col
        self.y = init_y
        self.x = init_x
        self.dy_bound = dy_bound
        self.rx_bound = rx_bound
        self.uy_bound = uy_bound
        self.lx_bound = lx_bound
        self._mvblock = False
        self._anim_block = False

    def tog_anim(self):
        self._togidx = (self._togidx + 1) % len(self._anims)
        self.ch = self._anims[self._togidx]

    def draw(self, xattr=0):
        self.__stdscr.addch(self.y,
                            self.x,
                            self.ch,
                            (xattr |
                             curses.color_pair(self.col) |
                             curses.A_BOLD))

    def clear(self, repch=cst.GRIDCH):
        self.__stdscr.addch(self.y,
                            self.x,
                            repch)

    def move_x(self, dir: int, dist: int):
        if dir:
            if self.x > self.lx_bound:
                self.x -= dist
        else:
            if self.x < self.rx_bound:
                self.x += dist

    def move_draw(self, dir: int, dist: int, xattr=0):
        self.__stdscr.addch(self.y,
                            self.x,
                            cst.GRIDCH)
        self.move_x(dir, dist)
        self.draw(xattr)

    # ghost movement fucks up the anim
    def update(self) -> bool:
        if self.__ticker_ref.mod(self._animfreq):
            if not self._anim_block:
                self.tog_anim()
        elif self._anim_block:
            self._anim_block = False

        if self.__ticker_ref.mod(self._mvfreq):
            if not self._mvblock:
                self.clear()
                self.move_x(1, 2)
                self._mvblock = True
        elif self._mvblock:
            self._mvblock = False

        self.draw()
        if self.x <= self.lx_bound:
            self.clear()
            return False
        else:
            return True
