from objects.GameObject import *
import pygame, string


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


class Player(GameObject):
    def __init__(self, frames, pos, timer):
        super(Player, self).__init__(frames, pos, timer)


class UIElement(GameObject):
    def __init__(self, frames, pos):
        super(UIElement, self).__init__(frames, pos, 0)

    def updateSelf(self, data):
        self.frameNumber = data // 10


class Paper(GameObject):
    def __init__(self, frames, pos):
        super(Paper, self).__init__(frames, pos, 0)


class DayCounter(GameObject):
    def __init__(self, frames, pos, numberFrames):
        super(DayCounter, self).__init__(frames, pos, 0)
        self.numberFrames = numberFrames
        self.num1 = 0
        self.num2 = 1

    def draw(self, display):
        image = pygame.Surface((20, 19), pygame.SRCALPHA)
        image.blit(self.animationFrames[0], (0, 0))
        image.blit(self.numberFrames[self.num1], (4, 11))
        image.blit(self.numberFrames[self.num2], (11, 11))
        display.blit(image, (self.x, self.y))

    def add(self, days=1):
        self.num2 += days
        if self.num2 > 9:
            self.num2 = 0
            self.num1 += 1


class Banner(GameObject):
    def __init__(self, frames, pos):
        super(Banner, self).__init__(frames, pos, 0)
        self.show = False


class Bill:
    def __init__(self, message, alphabet, effects):
        self.effects = effects
        letters = []
        self.lines = []
        i = 0
        for char in message.lower():
            if char == " ":
                letters += [alphabet[26]]
            elif char == ",":
                letters += [alphabet[27]]
            elif char == ".":
                letters += [alphabet[28]]
            elif char == "!":
                letters += [alphabet[29]]
            else:
                letters += [alphabet[string.ascii_lowercase.index(char)]]
            i += 1
            if i >= 19:
                i = 0
                self.lines += [letters]
                letters = []
        self.lines += [letters]

    def draw(self, display):
        for i in range(len(self.lines)):
            for j in range(len(self.lines[i])):
                display.blit(self.lines[i][j], (6 + (j * 6), 6 + (i * 7)))
