from objects.GameObject import *


class Background(GameObject):
    def __init__(self, frames, pos, timer):
        super(Background, self).__init__(frames, pos, timer)


class Foreground(GameObject):
    def __init__(self, frames, pos, timer):
        super(Foreground, self).__init__(frames, pos, timer)
