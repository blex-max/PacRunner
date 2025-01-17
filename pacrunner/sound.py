from os import environ, PathLike
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'  # the most egregious bullsh*t I've ever encountered in programming
from pygame.mixer import Sound
from typing import Union, IO


# extend pygame.mixer.Sound to add some conveniences
class Sound(Sound):
    def __init__(self,
                 file: Union[str, bytes, PathLike[str], PathLike[bytes], IO[bytes], IO[str]],
                 default_vol: float):
        super().__init__(file)
        self.set_volume(default_vol)
        self.default_vol = self.get_volume()

    def mute(self):
        self.set_volume(0)

    def unmute(self):
        self.set_volume(self.default_vol)
    
