import pygame, sys


class Game:
    windowX = 1000
    windowY = 750

    def __init__(self):
        self.display = pygame.display.set_mode((self.windowX, self.windowY))
        self.quit = False

        self.white = (255, 255, 255)

        self.objects = []

    def start(self):
        self.loop()

    def loop(self):
        while not self.quit:
            self.handle()
            self.update()
            self.draw()

    def stop(self):
        self.quit = True
        pygame.quit()
        sys.exit(0)

    def handle(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.stop()

        pressed = pygame.key.get_pressed()

    def update(self):
        for obj in self.objects:
            obj.update()

    def draw(self):
        self.display.fill(self.white)
        for obj in self.objects:
            obj.draw()
        pygame.display.flip()
