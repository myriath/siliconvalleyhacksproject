import random
import sys, os
from objects.Background import *
from objects.Objects import *
from objects.MenuObject import *
from engine.SpriteSheet import *


class Game:
    window = (1280, 960)
    resolution = (128, 96)

    TYPE_BG = 0
    TYPE_FG = 1
    TYPE_SP = 2

    CHOICE_NULL = 0
    CHOICE_YES = 1
    CHOICE_NO = 2

    TIME_DAY = 0
    TIME_NIGHT = 2

    white = (255, 255, 255)
    black = (0, 0, 0)

    def __init__(self):
        pygame.init()
        self.clicked = []
        self.display = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.window = (self.display.get_width(), self.display.get_height())
        pygame.display.set_icon(self.getImage(self.TYPE_SP, "icon.png"))
        self.clock = pygame.time.Clock()
        self.quit = False
        self.pause = False
        self.showingBill = False
        self.showingMap = False
        self.hasRead = False
        self.choice = self.CHOICE_NULL
        self.days = 0

        self.bills = []
        self.alphabet = SpriteSheet(self.getImage(self.TYPE_FG, "letters.png")).cut(5, 6)
        self.counter = DayCounter([self.getImage(self.TYPE_FG, "counter.png")], (102, 6),
                                  SpriteSheet(self.getImage(self.TYPE_FG, "daynumbers.png")).cut(5, 6))

        self.surface = pygame.Surface(self.resolution)
        self.scale = self.window[1] // self.resolution[1]
        self.scaledResolution = (self.resolution[0] * self.scale, self.resolution[1] * self.scale)
        self.offset = ((self.window[0] // 2) - (self.scaledResolution[0] // 2),
                       (self.window[1] // 2) - (self.scaledResolution[1] // 2))

        self.time = self.TIME_DAY

        image = self.getImage(self.TYPE_BG, "background1.png")
        banner1 = self.getImage(self.TYPE_SP, "banner_economy.png")
        banner2 = self.getImage(self.TYPE_SP, "banner_opinion.png")
        banner3 = self.getImage(self.TYPE_SP, "banner_infection.png")
        self.objects = [Background([image], (0, 0), 0), Banner([banner1], (48, 64)), Banner([banner2], (59, 64)), Banner([banner3], (70, 64))]
        images = SpriteSheet(self.getImage(self.TYPE_FG, "candle.png")).cut(5, 10)
        self.candle = Candle(images, (48, 51), 30)
        self.player = Player(SpriteSheet(self.getImage(self.TYPE_SP, "leader.png")).cut(8, 10), (60, 46), 40)

        self.buttons = [
            GameButton(SpriteSheet(self.getImage(self.TYPE_FG, "pausebutton.png")).cut(10, 10), (6, 6, 10, 10),
                       self.scale, self.offset)]
        self.buttons[0].function = self.pauseGame
        self.buttons += [
            GameButton(SpriteSheet(self.getImage(self.TYPE_FG, "mapbutton.png")).cut(10, 10), (22, 6, 10, 10),
                       self.scale, self.offset)]
        self.buttons[1].function = self.toggleMap
        self.buttons += [
            GameButton(SpriteSheet(self.getImage(self.TYPE_FG, "readbutton.png")).cut(10, 10), (38, 6, 10, 10),
                       self.scale, self.offset)]
        self.buttons[2].function = self.toggleBill
        self.buttons += [
            GameButton(SpriteSheet(self.getImage(self.TYPE_FG, "passbutton.png")).cut(10, 10), (54, 6, 10, 10),
                       self.scale, self.offset)]
        self.buttons[3].function = self.voteYes
        self.buttons += [
            GameButton(SpriteSheet(self.getImage(self.TYPE_FG, "vetobutton.png")).cut(10, 10), (70, 6, 10, 10),
                       self.scale, self.offset)]
        self.buttons[4].function = self.voteNo
        self.buttons += [
            GameButton(SpriteSheet(self.getImage(self.TYPE_FG, "nextday.png")).cut(10, 10), (86, 6, 10, 10), self.scale,
                       self.offset)]
        self.buttons[5].function = self.changeTime

        self.uiEconomy = UIElement(SpriteSheet(self.getImage(self.TYPE_FG, "economy.png")).cut(32, 10), (6, 80))
        self.economy = 0
        self.uiInfection = UIElement(SpriteSheet(self.getImage(self.TYPE_FG, "infection.png")).cut(32, 10), (90, 80))
        self.infection = 0
        self.uiOpinion = UIElement(SpriteSheet(self.getImage(self.TYPE_FG, "opinion.png")).cut(32, 10), (48, 80))
        self.opinion = 0

        self.paper = Paper(SpriteSheet(self.getImage(self.TYPE_FG, "bill.png")).cut(10, 6), (59, 57))

        menubg = self.getImage(self.TYPE_BG, "menubackground.png")
        pauseButtons = [
            GameButton(SpriteSheet(self.getImage(self.TYPE_FG, "quit.png")).cut(27, 10), (95, 80, 27, 10), self.scale,
                       self.offset),
            GameButton(SpriteSheet(self.getImage(self.TYPE_FG, "back.png")).cut(10, 10), (6, 6, 10, 10), self.scale,
                       self.offset)]
        pauseButtons[0].function = self.stop
        pauseButtons[1].function = self.pauseGame
        pauseLabels = []
        self.pauseMenu = Menu(menubg, pauseButtons, pauseLabels)

        billbg = self.getImage(self.TYPE_BG, "billbackground.png")
        billButtons = [
            GameButton(SpriteSheet(self.getImage(self.TYPE_FG, "back.png")).cut(10, 10), (6, 80, 10, 10), self.scale,
                       self.offset)]
        billButtons[0].function = self.toggleBill
        billLabels = []
        self.billMenu = Menu(billbg, billButtons, billLabels)

        cities = []
        for i in range(4):
            cities += [City((random.randint(25, 100), random.randint(25, 75)))]
        cities += [City((random.randint(25, 100), random.randint(25, 75)))]
        cities[4].infection = 20
        cities[3].infection = 100
        mapButtons = [GameButton(SpriteSheet(self.getImage(self.TYPE_FG, "back.png")).cut(10, 10), (6, 80, 10, 10), self.scale, self.offset)]
        mapButtons[0].function = self.toggleMap
        self.map = Map(self.getImage(self.TYPE_FG, "worldmap.png"), cities, mapButtons, [])

        self.dayShader = Background([self.getImage(self.TYPE_BG, "day.png")], (0, 0), 0)
        self.nightShader = Background([self.getImage(self.TYPE_BG, "night.png")], (0, 0), 0)

        self.generateBills()
        self.bill = random.choice(self.bills)

    def getImage(self, type, filename):
        if type == self.TYPE_BG:
            return pygame.image.load(os.path.join(os.getcwd(), "assets", "backgrounds", filename)).convert_alpha()
        elif type == self.TYPE_FG:
            return pygame.image.load(os.path.join(os.getcwd(), "assets", "foregrounds", filename)).convert_alpha()
        elif type == self.TYPE_SP:
            return pygame.image.load(os.path.join(os.getcwd(), "assets", "sprites", filename)).convert_alpha()

    def getSound(self, filename):
        return os.path.join(os.getcwd(), "assets", "sprites", filename)

    def start(self):
        self.loop()

    def generateBills(self):
        self.bills += [Bill(
            "hey", self.alphabet, (10, 20, 10, -10, -20, -10))]
        self.bills += [Bill("Hello", self.alphabet, (0, 0, 0, 0, 0, 0))]

    def toggleMap(self):
        self.showingMap = not self.showingMap

    def toggleBill(self):
        self.showingBill = not self.showingBill

    def voteYes(self):
        self.choice = self.CHOICE_YES

    def voteNo(self):
        self.choice = self.CHOICE_NO

    def changeTime(self):
        if self.choice != self.CHOICE_NULL:
            if self.time == self.TIME_DAY:
                self.time = self.TIME_NIGHT
            else:
                self.time = self.TIME_DAY
                self.counter.add()
                self.days += 1
            effects = self.bill.effects
            if self.choice == self.CHOICE_YES:
                self.economy += effects[0]
                self.opinion += effects[1]
                self.infection += effects[2]
            elif self.choice == self.CHOICE_NO:
                self.economy += effects[3]
                self.opinion += effects[4]
                self.infection += effects[5]
            self.choice = self.CHOICE_NULL
            self.bill = random.choice(self.bills)

    def pauseGame(self):
        self.pause = not self.pause

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
                elif event.key == pygame.K_d:
                    self.time = self.TIME_DAY
                elif event.key == pygame.K_a:
                    self.economy += 1
                    if self.economy > 100:
                        self.economy = 0
                elif event.key == pygame.K_q:
                    self.opinion += 1
                    if self.opinion > 100:
                        self.opinion = 0
                elif event.key == pygame.K_z:
                    self.infection += 1
                    if self.infection > 100:
                        self.infection = 0
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.pause:
                        self.pauseMenu.click(pygame.mouse.get_pos())
                    elif self.showingBill:
                        self.billMenu.click(pygame.mouse.get_pos())
                    elif self.showingMap:
                        self.map.click(pygame.mouse.get_pos())
                    else:
                        for button in self.buttons:
                            if button.checkClicked(pygame.mouse.get_pos()):
                                button.frameNumber = 1
                                self.clicked += [button]
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    if self.pause:
                        self.pauseMenu.unclick()
                    elif self.showingBill:
                        self.billMenu.unclick()
                    elif self.showingMap:
                        self.map.unclick()
                    else:
                        for button in self.clicked:
                            button.frameNumber = 0
                            button.function()
                        self.clicked = []

    def update(self):
        if not self.pause:
            for obj in self.objects:
                obj.update()

            if self.economy > 100:
                self.economy = 100
            elif self.economy < 0:
                self.economy = 0
            if self.economy == 100:
                self.objects[1].show = True

            if self.opinion > 100:
                self.opinion = 100
            elif self.opinion < 0:
                self.opinion = 0
            if self.opinion == 100:
                self.objects[2].show = True

            if self.infection > 100:
                self.infection = 100
            elif self.infection < 0:
                self.infection = 0
            if self.infection == 0:
                self.objects[3].show = True

            self.candle.updateSelf(self.time)
            self.player.update()
            self.uiEconomy.updateSelf(self.economy)
            self.uiInfection.updateSelf(self.infection)
            self.uiOpinion.updateSelf(self.opinion)

            self.paper.frameNumber = self.choice

    def draw(self):
        self.display.fill(self.black)
        self.surface.fill(self.white)
        for obj in self.objects:
            if obj.show:
                obj.draw(self.surface)
        self.candle.draw(self.surface)
        self.paper.draw(self.surface)

        if self.time == self.TIME_DAY:
            self.dayShader.draw(self.surface)
        elif self.time == self.TIME_NIGHT:
            self.nightShader.draw(self.surface)

        for button in self.buttons:
            button.draw(self.surface)

        self.counter.draw(self.surface)

        self.uiEconomy.draw(self.surface)
        self.uiInfection.draw(self.surface)
        self.uiOpinion.draw(self.surface)
        self.player.draw(self.surface)

        if self.showingBill:
            self.billMenu.draw(self.surface)
            self.bill.draw(self.surface)

        if self.showingMap:
            self.map.draw(self.surface)

        if self.pause:
            self.pauseMenu.draw(self.surface)

        self.display.blit(
            pygame.transform.scale(self.surface, (self.resolution[0] * self.scale, self.resolution[1] * self.scale)),
            self.offset)
        pygame.display.flip()
