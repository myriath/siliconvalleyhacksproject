import sys, os
from objects.Background import *
from engine.SpriteSheet import *
from objects.Objects import *

class Game:
    window = (1280, 960)
    resolution = (128, 96)

    TYPE_BG = 0
    TYPE_FG = 1
    TYPE_SP = 2

    TIME_DAY = 0
    TIME_DUSK = 1
    TIME_NIGHT = 2

    white = (255, 255, 255)
    black = (0, 0, 0)

    def __init__(self):
        pygame.init()
        # self.display = pygame.display.set_mode(self.window)
        self.display = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.window = (self.display.get_width(), self.display.get_height())
        self.clock = pygame.time.Clock()
        self.quit = False

        self.surface = pygame.Surface(self.resolution)
        self.scale = self.window[1]//self.resolution[1]
        self.scaledResolution = (self.resolution[0] * self.scale, self.resolution[1] * self.scale)
        self.time = self.TIME_DAY

        image = self.getImage(self.TYPE_BG, "background1.png")
        self.objects = [Background([image], (0, 0), 0)]
        images = SpriteSheet(self.getImage(self.TYPE_FG, "candle.png")).cut(5, 10)
        self.candle = Candle(images, (48, 51), 30)

        self.dayShader = Background([self.getImage(self.TYPE_BG, "day.png")], (0, 0), 0)
        self.duskShader = Background([self.getImage(self.TYPE_BG, "dusk.png")], (0, 0), 0)
        self.nightShader = Background([self.getImage(self.TYPE_BG, "night.png")], (0, 0), 0)

    def getImage(self, type, filename):
        if type == self.TYPE_BG:
            return pygame.image.load(os.path.join(os.getcwd(), "assets", "backgrounds", filename)).convert_alpha()
        elif type == self.TYPE_FG:
            return pygame.image.load(os.path.join(os.getcwd(), "assets", "foregrounds", filename)).convert_alpha()
        elif type == self.TYPE_SP:
            return pygame.image.load(os.path.join(os.getcwd(), "assets", "sprites", filename)).convert_alpha()


    def start(self):
        self.loop()

    def loop(self):
        while not self.quit:
            self.handle()
            self.update()
            self.draw()

            self.clock.tick(60)

    def stop(self):
        self.quit = True
        pygame.quit()
        sys.exit(0)

    def handle(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.stop()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_n:
                    self.time = self.TIME_NIGHT
                    print(self.time)
                elif event.key == pygame.K_d:
                    self.time = self.TIME_DAY
                    print(self.time)

        pressed = pygame.key.get_pressed()

    def update(self):
        for obj in self.objects:
            obj.update()
        self.candle.updateSelf(self.time)

    def draw(self):
        self.display.fill(self.black)
        self.surface.fill(self.white)
        for obj in self.objects:
            obj.draw(self.surface)
        self.candle.draw(self.surface)

        if self.time == self.TIME_DAY:
            self.dayShader.draw(self.surface)
        elif self.time == self.TIME_DUSK:
            self.duskShader.draw(self.surface)
        elif self.time == self.TIME_NIGHT:
            self.nightShader.draw(self.surface)

        self.display.blit(pygame.transform.scale(self.surface, (self.resolution[0] * self.scale, self.resolution[1] * self.scale)),
                          ((self.window[0] // 2) - (self.scaledResolution[0] // 2), (self.window[1] // 2) - (self.scaledResolution[1] // 2)))
        pygame.display.flip()
