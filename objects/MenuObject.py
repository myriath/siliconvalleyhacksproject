import pygame


class Menu:
    def __init__(self, menuBackground, buttons, labels):
        self.buttons, self.labels = buttons, labels
        self.menuBackground = menuBackground
        self.pos = (3, 3)
        self.clicked = []

    def draw(self, display):
        display.blit(self.menuBackground, self.pos)
        for button in self.buttons:
            button.draw(display)
        for label in self.labels:
            label.draw(display)

    def click(self, pos):
        for button in self.buttons:
            if button.checkClicked(pos):
                button.frameNumber = 1
                self.clicked += [button]

    def unclick(self):
        for button in self.clicked:
            button.frameNumber = 0
            button.function()
        self.clicked = []


class Label:
    def __init__(self, image, dim):
        self.image, self.dim = image, dim

    def draw(self, display):
        display.blit(self.image, (self.dim[0], self.dim[1]))


class Button:
    def __init__(self, image, dim, scale, offset):
        self.image, self.dim = image, dim
        self.scale = scale
        self.offset = offset

    def draw(self, display):
        display.blit(self.image, (self.dim[0], self.dim[1]))

    def checkClicked(self, pos):
        x, y = pos
        dim = \
            (self.dim[0] * self.scale + self.offset[0], self.dim[1] * self.scale + self.offset[1],
             self.dim[2] * self.scale,
             self.dim[3] * self.scale)

        if dim[0] < x < dim[0] + dim[2]:
            if dim[1] < y < dim[1] + dim[3]:
                return True
        return False

    def function(self):
        pass


class GameButton(Button):
    def __init__(self, frames, dim, scale, offset):
        super(GameButton, self).__init__(frames[0], dim, scale, offset)
        self.frames = frames
        self.frameNumber = 0
        self.timer = 0
        self.frameTime = 0

    def draw(self, display):
        display.blit(self.frames[self.frameNumber], (self.dim[0], self.dim[1]))

    def checkClicked(self, pos):
        x, y = pos
        dim = (
            self.dim[0] * self.scale + self.offset[0], self.dim[1] * self.scale + self.offset[1],
            self.dim[2] * self.scale,
            self.dim[3] * self.scale)

        if dim[0] < x < dim[0] + dim[2]:
            if dim[1] < y < dim[1] + dim[3]:
                self.frameNumber = 1
                self.timer = 30
                return True
        return False


class Map(Menu):
    def __init__(self, bg, cities, buttons, labels):
        super(Map, self).__init__(bg, buttons, labels)
        self.cities = cities

    def draw(self, display):
        display.blit(self.menuBackground, self.pos)
        for city in self.cities:
            city.draw(display)
        for button in self.buttons:
            button.draw(display)
        for label in self.labels:
            label.draw(display)


class City:
    def __init__(self, pos):
        self.pos = pos
        self.infection = 0
        self.quarantined = False

    def draw(self, display):
        pygame.draw.rect(display, (self.infection * 2.55, 0, 0), (self.pos[0], self.pos[1], 1, 1))
