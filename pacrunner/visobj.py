# if this gets complicated, consider parent class, or composing move, draw, obj
# abstract classes and so on
from pacrunner import constants as cst
from pytick.ticker import IncTicker
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
        self.__default_anim_pair = (cst.HEROCLOSEDCH, cst.HEROOPENCH)
        self.__togidx = 0
        self.ch = self.__default_anim_pair[0]
        self.y = init_y
        self.x = init_x
        self.dy_bound = dy_bound
        self.rx_bound = rx_bound
        self.uy_bound = uy_bound
        self.lx_bound = lx_bound

    def tog_anim(self):
        self.__togidx = (self.__togidx + 1) % len(self.__default_anim_pair)
        self.ch = self.__default_anim_pair[self.__togidx]

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
                 freq,
                 col: int,
                 init_y,
                 init_x,
                 dy_bound,
                 rx_bound,
                 uy_bound=0,
                 lx_bound=0):
        self.__anims = sample(cst.GHOSTCH_L, 2)
        self.__togidx = 0
        self.ch = self.__anims[self.__togidx]
        self.__stdscr = stdscr
        self.__ticker_ref = ticker
        self.__freq = freq
        self.col = col
        self.y = init_y
        self.x = init_x
        self.dy_bound = dy_bound
        self.rx_bound = rx_bound
        self.uy_bound = uy_bound
        self.lx_bound = lx_bound
        self.__update_block = 0

    def tog_anim(self):
        self.__togidx = (self.__togidx + 1) % len(self.__anims)
        self.ch = self.__anims[self.__togidx]

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

    def update(self) -> bool:
        if self.__ticker_ref.mod(self.__freq):
            if not self.__update_block:
                self.move_draw(1, 2)
                self.__update_block = True
        elif self.__update_block:
            self.__update_block = 0
        if self.x <= self.lx_bound:
            self.clear()
            return False
        else:
            return True
