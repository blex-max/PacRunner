# if this gets complicated, consider parent class, or composing move, draw, obj
# abstract classes and so on
from pacrunner import constants as cst
from tickpy.ticker import ExtTicker
import curses
import random
from random import sample
from typing import Literal


class Edible:
    def __init__(self,
                 edible: bool = False):
        self.eatme = edible


class Pill:
    def __init__(self,
                 stdscr,
                 ticker: ExtTicker,
                 mvfreq: int,
                 init_y: int,
                 init_x: int,
                 lx_bound: int,
                 rx_bound: int,
                 cols: list):
        self.__stdscr_ref = stdscr
        self.__ticker_ref = ticker
        self._mvfreq = mvfreq
        self._animfreq = 30
        self._mvblock = False
        self._animblock = False
        self.y = init_y
        self.x = init_x
        self.ch = cst.PILLCH
        self.lx_bound = lx_bound
        self.rx_bound = rx_bound
        self._coll = cols
        self._col_idx = 0
        self._col = self._coll[self._col_idx]

    def tog_anim(self):
        self._col_idx = (self._col_idx + 1) % len(self._coll)
        self._col = self._coll[self._col_idx]

    def draw(self):
        self.__stdscr_ref.addch(self.y,
                            self.x,
                            self.ch,
                            self._col)

    def clear(self, repch=cst.GRIDCH):
        self.__stdscr_ref.addch(self.y,
                            self.x,
                            repch)

    def move(self):
        self.x -= 1

    def update(self) -> bool:
        if self.__ticker_ref.mod(self._animfreq):
            if not self._animblock:
                self.tog_anim()
                self._animblock = True
        elif self._animblock:
            self._animblock = False

        if self.__ticker_ref.mod(self._mvfreq):
            if not self._mvblock:
                self.clear()
                self.move()
                self._mvblock = True
        elif self._mvblock:
            self._mvblock = False

        self.draw()
        if self.x <= self.lx_bound:
            self.clear()
            return False
        else:
            return True


class Coin:
    def __init__(self,
                 stdscr,
                 init_y: int,
                 init_x: int,
                 size: int,
                 attr):
        self.__stdscr_ref = stdscr
        self.collected = False
        self.y = init_y
        self.x = init_x
        self.size = size
        self.ch = cst.BIGCOINCH if size == 2 else cst.SMALLCOINCH
        self.attr = attr

    def draw(self,
             y: int | None = None,
             x: int | None = None):
        self.y = y if y else self.y
        self.x = x if x else self.x
        self.__stdscr_ref.addch(self.y,
                                self.x,
                                self.ch,
                                self.attr)

    def clear(self, repch = cst.GRIDCH):
        self.__stdscr_ref.addch(self.y,
                                self.x,
                                repch)

    def collection(self):
        self.ch = cst.GRIDCH
        self.collected = True


class CoinRun:
    def __init__(self,
                 stdscr,
                 ticker: ExtTicker,
                 mvfreq: int,
                 init_y: int,
                 init_lx: int,
                 lx_bound: int,
                 rx_bound: int,
                 attr):
        self.__stdscr_ref = stdscr
        self.__ticker_ref = ticker
        self._mvfreq = mvfreq
        self.x = init_lx
        self.y = init_y
        self.lx_bound = lx_bound
        self.rx_bound = rx_bound
        self.attr = attr
        self._mvblock = False
        
        self.len = random.choices([1,2,3],[3,2,1])[0]
        self.coinl = []
        for i in range(self.len):
            self.coinl.append(Coin(self.__stdscr_ref,
                        init_y,
                        init_lx + i,
                        1,
                        attr))
        if True if random.random() > 0.9 else False:  # add big
            self.coinl.append(Coin(self.__stdscr_ref,
                            init_y,
                            init_lx + i + 1,
                            2,
                            attr))
            self.len += 1
        self.xl = list(range(self.x, self.x + self.len))

    def move_coins(self):
        for coin in self.coinl:
            coin.clear()
            coin.x -= 1

    def remove_loob(self):
        tmp_coinl = []
        for coin in self.coinl:
            if coin.x < self.lx_bound:
                coin.clear()
            else:
                tmp_coinl.append(coin)
        self.coinl = tmp_coinl

    def draw_inbounds_coins(self):
        for coin in self.coinl:
            if self.lx_bound <= coin.x <= self.rx_bound:
                coin.draw()

    def collect_at(self, x) -> int:
        for coin in self.coinl:
            if coin.x == x:
                if not coin.collected:
                    coin.collection()
                    return coin.size
        return 0

    def update(self) -> bool:
        if self.__ticker_ref.mod(self._mvfreq):
            if not self._mvblock:
                self.move_coins()
                self.draw_inbounds_coins()
                self.remove_loob()
                self.x -= 1
                self.xl = list(range(self.x, self.x + self.len))
                self._mvblock = True
        elif self._mvblock:
            self._mvblock = False

        if not self.coinl:
            return False
        else:
            return True




class SingleLineStrobe():
    def __init__(self,
                 text: str,
                 ticker: ExtTicker,
                 animfreq: int,
                 draw_y: int,
                 draw_x: int,
                 color_offset: int,
                 color_wrap: int,
                 default_attr: int = 0):
        self.__ticker_ref = ticker
        self.__anim_block = False
        self.__color_idx = 0
        self.anim_freq = animfreq
        self.text = text
        self.y = draw_y
        self.x = draw_x
        self.color_offset = color_offset
        self.color_wrap = color_wrap
        self.attr = default_attr

    def strobe(self,
               stdscr,
               y: int | None = None,
               x: int | None = None,
               attr: int | None = None):
        if self.__ticker_ref.mod(self.anim_freq):
            if not self.__anim_block:
                self.y = y if y else self.y
                self.x = x if x else self.x
                attr = attr if attr else self.attr
                for i, char in enumerate(self.text):
                    color_index = (i + self.color_offset + self.__color_idx) % (self.color_wrap - self.color_offset)
                    stdscr.addch(self.y,
                                 self.x + i,
                                 char,
                                 curses.color_pair(color_index + 1) | attr)
                self.__color_idx = (self.__color_idx + 1) % (self.color_wrap - self.color_offset)
                self.__anim_block = True
        elif self.__anim_block:
            self.__anim_block = False

    def clear(self,
              stdscr,
              repch = cst.GRIDCH):
        for i, _ in enumerate(self.text):
            stdscr.addch(self.y,
                         self.x + i,
                         repch)


class MultiLineStrobe():
    def __init__(self,
                 strl: list[str],
                 ticker: ExtTicker,
                 animfreq: int,
                 normal_draw_y: int,
                 normal_draw_x: int,
                 color_offset: int,
                 color_wrap: int,
                 default_attr: int = curses.A_BOLD):
        self.__ticker_ref = ticker
        self.__anim_block = False
        self.__color_idx = 0
        self.anim_freq = animfreq
        self.y = normal_draw_y
        self.x = normal_draw_x
        self.strl = strl
        self.color_offset = color_offset
        self.color_wrap = color_wrap
        self.attr = default_attr

    def strobe(self,
               stdscr,
               y: int | None = None,
               x: int | None = None,
               attr: int | None = None):
        if self.__ticker_ref.mod(self.anim_freq):
            if not self.__anim_block:
                y = y if y else self.y
                x = x if x else self.x
                attr = attr if attr else self.attr
                for i, line in enumerate(self.strl):
                    for j, char in enumerate(line):
                        color_index = (j + self.color_offset + self.__color_idx) % (self.color_wrap - self.color_offset)
                        stdscr.addch(y + i,
                                     x + j,
                                     char,
                                     curses.color_pair(color_index + 1) | attr)
                self.__color_idx = (self.__color_idx + 1) % (self.color_wrap - self.color_offset)
                self.__anim_block = True
        elif self.__anim_block:
            self.__anim_block = False
        
        

class Player:
    def __init__(self,
                 stdscr,
                 ticker: ExtTicker,
                 init_y,
                 init_x,
                 init_attr: int,
                 dy_bound,
                 rx_bound,
                 uy_bound=0,
                 lx_bound=0,
                 animfreq: int = 24):
        self.__stdscr_ref = stdscr
        self.__ticker_ref = ticker
        self.anim_ch = (cst.HEROCLOSEDCH, cst.HEROOPENCH)
        self.anim_freq = animfreq
        self.__anim_block = False
        self._togidx = 0
        self.ch = self.anim_ch[0]
        self.y = init_y
        self.x = init_x
        self.py = self.y
        self.px = self.x 
        self.dy_bound = dy_bound
        self.rx_bound = rx_bound
        self.uy_bound = uy_bound
        self.lx_bound = lx_bound
        self.init_attr = init_attr
        self.attr = self.init_attr

    def tog_anim(self):
        self._togidx = (self._togidx + 1) % len(self.anim_ch)
        self.ch = self.anim_ch[self._togidx]

    def move_y(self, dir):
        if dir:
            if self.y > self.uy_bound:
                self.y -= 1
        else:
            if self.y < self.dy_bound:
                self.y += 1

    def move_x(self, dir):
        if dir:
            if self.x < self.rx_bound:
                self.x += 1
        else:
            if self.x > self.lx_bound:
                self.x -= 1

    def draw(self, attr = None):
        self.attr = attr if attr else self.attr
        self.__stdscr_ref.addch(self.y,
                     self.x,
                     self.ch,
                     self.attr)

    def clear(self,
              repch = cst.GRIDCH):
        self.__stdscr_ref.addch(self.py,
                                self.px,
                                repch)

    def clearall(self,
                 repch = cst.GRIDCH):
        self.__stdscr_ref.addch(self.py,
                                self.px,
                                repch)
        self.__stdscr_ref.addch(self.y,
                                self.x,
                                repch)

    def update(self):
        if self.__ticker_ref.mod(self.anim_freq):
            if not self.__anim_block:
                self.tog_anim()
                self.__anim_block = True
        elif self.__anim_block:
            self.__anim_block = False

        if self.y != self.py or self.x != self.px:
            self.clear()
            if self.y != self.py:
                self.py = self.y
            if self.x != self.px:
                self.px = self.x

        self.draw()

        


class Ghost:
    def __init__(self,
                 stdscr,
                 ticker: ExtTicker,
                 edible_ref: Edible,
                 mvfreq: int,
                 animfreq: int,
                 col: int,
                 edible_cols: list[int],
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
        self._edible_ref = edible_ref
        self._ediblefreq = 30
        self._edible_col_idx = 0
        self._edible_coll = edible_cols
        self._edible_col = edible_cols[self._edible_col_idx]
        self._edible_block = False
        self._mvfreq = mvfreq
        self.anim_freq = animfreq
        self.col = col
        self.y = init_y
        self.x = init_x
        self.dy_bound = dy_bound
        self.rx_bound = rx_bound
        self.uy_bound = uy_bound
        self.lx_bound = lx_bound
        self._mvblock = False
        self.__anim_block = False

    def tog_anim(self):
        self._togidx = (self._togidx + 1) % len(self._anims)
        self.ch = self._anims[self._togidx]

    def tog_col(self):
        self._edible_col_idx = (self._edible_col_idx + 1) % len(self._edible_coll)
        self._edible_col = self._edible_coll[self._edible_col_idx]

    def draw(self):
        self.__stdscr.addch(self.y,
                            self.x,
                            self.ch,
                            (curses.color_pair(self.col) if not self._edible_ref.eatme else curses.color_pair(self._edible_col) |
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

    def update(self) -> bool:
        if self.__ticker_ref.mod(self.anim_freq):
            if not self.__anim_block:
                self.tog_anim()
                self.__anim_block = True
        elif self.__anim_block:
            self.__anim_block = False

        if self.__ticker_ref.mod(self._mvfreq):
            if not self._mvblock:
                self.clear()
                self.move_x(1, 1)
                self._mvblock = True
        elif self._mvblock:
            self._mvblock = False

        if self._edible_ref.eatme and self.__ticker_ref.mod(self._ediblefreq):
            if not self._edible_block:
                self.tog_col()
                self._edible_block = True
        elif self._edible_block:
            self._edible_block = False

        self.draw()
        if self.x <= self.lx_bound:
            self.clear()
            return False
        else:
            return True
