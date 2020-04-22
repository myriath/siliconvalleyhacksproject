from objects.GameObject import *

class Candle(GameObject):
    def __init__(self, frames, pos, timer):
        super(Candle, self).__init__(frames, pos, timer)

    def checkTime(self, time):
        from engine.Engine import Game
        return time == Game.TIME_NIGHT

    def updateSelf(self, time):
        if self.checkTime(time):
            if self.frameNumber == 0:
                self.frameNumber = 1
            if self.timer > 0:
                self.frameTimer += 1
                if self.frameTimer >= self.timer:
                    self.frameTimer = 0
                    self.updateAnimation()
        else:
            self.frameNumber = 0

    def updateAnimation(self, frame=-1):
        if frame > 0:
            self.frameNumber = frame
        else:
            self.frameNumber += 1
            if self.frameNumber > len(self.animationFrames) - 1:
                self.frameNumber = 1
