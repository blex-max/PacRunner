import constants as cst


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

    def draw(self, stdscr, attr):
        stdscr.addch(self.y,
                     self.x,
                     self.ch,
                     attr)

    def move_y_draw(self, stdscr, dir, attr):
        self.move_y(dir)
        self.draw(stdscr)
