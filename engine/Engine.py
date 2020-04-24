import sys, os
from objects.Background import *
from objects.Objects import *
from objects.MenuObject import *
from engine.SpriteSheet import *

TYPE_BG = 0
TYPE_FG = 1
TYPE_SP = 2

COND_OPINION = 0
COND_ECONOMY = 1
COND_INFECTION = 2
COND_TIME = 3


def cap(low, high, value):
    return min(high, max(value, low))


def playSound(filename, loops=-1, fadeout=True):
    pygame.mixer.music.set_volume(0.05)
    if fadeout:
        pygame.mixer.music.fadeout(1)
    pygame.mixer.music.load(os.path.join(os.getcwd(), "assets", "sounds", filename))
    pygame.mixer.music.play(loops)


def getSound(filename):
    return pygame.mixer.Sound(os.path.join(os.getcwd(), "assets", "sounds", filename))


def getImage(type, filename):
    if type == TYPE_BG:
        return pygame.image.load(os.path.join(os.getcwd(), "assets", "backgrounds", filename)).convert_alpha()
    elif type == TYPE_FG:
        return pygame.image.load(os.path.join(os.getcwd(), "assets", "foregrounds", filename)).convert_alpha()
    elif type == TYPE_SP:
        return pygame.image.load(os.path.join(os.getcwd(), "assets", "sprites", filename)).convert_alpha()


class Game:
    window = (1280, 960)
    resolution = (128, 96)

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
        pygame.display.set_icon(getImage(TYPE_SP, "icon.ico"))
        self.clock = pygame.time.Clock()
        self.quit = False
        self.pause = False
        self.showingBill = False
        self.showingMap = False
        self.hasRead = False
        self.closingStart = False
        self.closingDone = False
        self.gameover = True
        self.firstrun = True
        self.choice = self.CHOICE_NULL
        self.days = 1

        playSound("day.mp3")
        self.winSound = getSound("win.wav")
        self.winSound.set_volume(0.05)
        self.loseSound = getSound("lose.wav")
        self.loseSound.set_volume(0.05)
        self.clickSound = getSound("click.wav")
        self.clickSound.set_volume(0.05)

        self.infectionRate = 20
        self.uiEconomy = UIElement(SpriteSheet(getImage(TYPE_FG, "economy.png")).cut(32, 10), (6, 80))
        self.economy = 50
        self.uiInfection = UIElement(SpriteSheet(getImage(TYPE_FG, "infection.png")).cut(32, 10), (90, 80))
        self.infection = 10
        self.uiOpinion = UIElement(SpriteSheet(getImage(TYPE_FG, "opinion.png")).cut(32, 10), (48, 80))
        self.opinion = 50

        self.curtainsOpen = Curtain(SpriteSheet(getImage(TYPE_FG, "curtainsopen.png")).cut(128, 96), (0, 0))
        self.curtainsClose = Curtain(SpriteSheet(getImage(TYPE_FG, "curtainsclose.png")).cut(128, 96), (0, 0))
        self.curtainsClose.done = self.closeCurtainsDone
        self.curtainsClose.show = False

        self.winSplash = GameObject(SpriteSheet(getImage(TYPE_FG, "survive.png")).cut(128, 96), (0, 0), 30)
        self.winSplash.show = False
        self.loseEconomy = GameObject(SpriteSheet(getImage(TYPE_FG, "collapse.png")).cut(128, 96), (0, 0), 30)
        self.loseEconomy.show = False
        self.loseOpinion = GameObject(SpriteSheet(getImage(TYPE_FG, "removed.png")).cut(128, 96), (0, 0), 30)
        self.loseOpinion.show = False
        self.loseInfection = GameObject(SpriteSheet(getImage(TYPE_FG, "perished.png")).cut(128, 96), (0, 0), 30)
        self.loseInfection.show = False
        self.loseTime = GameObject(SpriteSheet(getImage(TYPE_FG, "incapable.png")).cut(128, 96), (0, 0), 30)
        self.loseTime.show = False

        self.clicktostart = GameObject(SpriteSheet(getImage(TYPE_FG, "clicktostart.png")).cut(35, 18), (self.resolution[0] // 2 - 17, 60), 30)
        self.logo = GameObject(SpriteSheet(getImage(TYPE_FG, "logo.png")).cut(54, 41), (36, 10), 60)

        self.bills = []
        self.alphabet = SpriteSheet(getImage(TYPE_FG, "letters.png")).cut(5, 6)
        self.counter = DayCounter([getImage(TYPE_FG, "counter.png")], (102, 6),
                                  SpriteSheet(getImage(TYPE_FG, "daynumbers.png")).cut(5, 6))

        self.surface = pygame.Surface(self.resolution)
        self.scale = self.window[1] // self.resolution[1]
        self.scaledResolution = (self.resolution[0] * self.scale, self.resolution[1] * self.scale)
        self.offset = ((self.window[0] // 2) - (self.scaledResolution[0] // 2),
                       (self.window[1] // 2) - (self.scaledResolution[1] // 2))

        self.time = self.TIME_DAY

        image = getImage(TYPE_BG, "background1.png")
        banner1 = getImage(TYPE_SP, "banner_economy.png")
        banner2 = getImage(TYPE_SP, "banner_opinion.png")
        banner3 = getImage(TYPE_SP, "banner_infection.png")
        self.objects = [Background([image], (0, 0), 0), Banner([banner1], (48, 64)), Banner([banner2], (59, 64)), Banner([banner3], (70, 64))]
        images = SpriteSheet(getImage(TYPE_FG, "candle.png")).cut(5, 10)
        self.candle = Candle(images, (48, 51), 30)
        self.player = Player(SpriteSheet(getImage(TYPE_SP, "leader.png")).cut(8, 10), (60, 46), 40)

        self.buttons = [
            GameButton(SpriteSheet(getImage(TYPE_FG, "pausebutton.png")).cut(10, 10), (6, 6, 10, 10),
                       self.scale, self.offset, self.clickSound)]
        self.buttons[0].function = self.pauseGame
        self.buttons += [
            GameButton(SpriteSheet(getImage(TYPE_FG, "mapbutton.png")).cut(10, 10), (22, 6, 10, 10),
                       self.scale, self.offset, self.clickSound)]
        self.buttons[1].function = self.toggleMap
        self.buttons += [
            GameButton(SpriteSheet(getImage(TYPE_FG, "readbutton.png")).cut(10, 10), (38, 6, 10, 10),
                       self.scale, self.offset, self.clickSound)]
        self.buttons[2].function = self.toggleBill
        self.buttons += [
            GameButton(SpriteSheet(getImage(TYPE_FG, "passbutton.png")).cut(10, 10), (54, 6, 10, 10),
                       self.scale, self.offset, self.clickSound)]
        self.buttons[3].function = self.voteYes
        self.buttons += [
            GameButton(SpriteSheet(getImage(TYPE_FG, "vetobutton.png")).cut(10, 10), (70, 6, 10, 10),
                       self.scale, self.offset, self.clickSound)]
        self.buttons[4].function = self.voteNo
        self.buttons += [
            GameButton(SpriteSheet(getImage(TYPE_FG, "nextday.png")).cut(10, 10), (86, 6, 10, 10), self.scale,
                       self.offset, self.clickSound)]
        self.buttons[5].function = self.closeCurtainsDayChange

        self.paper = Paper(SpriteSheet(getImage(TYPE_FG, "bill.png")).cut(10, 6), (59, 57))

        menubg = getImage(TYPE_BG, "menubackground.png")
        pauseButtons = [
            GameButton(SpriteSheet(getImage(TYPE_FG, "quit.png")).cut(27, 10), (95, 80, 27, 10), self.scale,
                       self.offset, self.clickSound),
            GameButton(SpriteSheet(getImage(TYPE_FG, "back.png")).cut(10, 10), (6, 6, 10, 10), self.scale,
                       self.offset, self.clickSound)]
        pauseButtons[0].function = self.stop
        pauseButtons[1].function = self.pauseGame
        pauseLabels = []
        self.pauseMenu = Menu(menubg, pauseButtons, pauseLabels)

        billbg = getImage(TYPE_BG, "billbackground.png")
        billButtons = [
            GameButton(SpriteSheet(getImage(TYPE_FG, "back.png")).cut(10, 10), (6, 80, 10, 10), self.scale,
                       self.offset, self.clickSound)]
        billButtons[0].function = self.toggleBill
        billLabels = []
        self.billMenu = Menu(billbg, billButtons, billLabels)

        self.cities = []
        for i in range(4):
            self.cities += [self.generateCities()]
        self.cities[3].infection = 20
        mapButtons = [GameButton(SpriteSheet(getImage(TYPE_FG, "back.png")).cut(10, 10), (6, 80, 10, 10), self.scale, self.offset, self.clickSound)]
        mapButtons[0].function = self.toggleMap
        self.map = Map(getImage(TYPE_FG, "worldmap.png"), self.cities, mapButtons, [])

        self.dayShader = Background([getImage(TYPE_BG, "day.png")], (0, 0), 0)
        self.nightShader = Background([getImage(TYPE_BG, "night.png")], (0, 0), 0)

        self.generateBills()
        self.bill = random.choice(self.bills)

        self.readConfig()

    def start(self):
        self.loop()

    def restart(self):
        print("restart")
        self.infectionRate = 20
        self.economy = 50
        self.opinion = 50
        self.infection = 10
        self.winSplash.show = False
        self.loseEconomy.show = False
        self.loseOpinion.show = False
        self.loseInfection.show = False
        self.loseTime.show = False
        self.generateBills()
        self.bill = random.choice(self.bills)
        self.gameover = False
        self.cities = []
        for i in range(4):
            self.cities += [self.generateCities()]
        self.cities[3].infection = 20
        self.cities[2].infection = 20
        mapButtons = [
            GameButton(SpriteSheet(getImage(TYPE_FG, "back.png")).cut(10, 10), (6, 80, 10, 10), self.scale, self.offset,
                       self.clickSound)]
        mapButtons[0].function = self.toggleMap
        self.map = Map(getImage(TYPE_FG, "worldmap.png"), self.cities, mapButtons, [])

        self.counter = DayCounter([getImage(TYPE_FG, "counter.png")], (102, 6),
                                  SpriteSheet(getImage(TYPE_FG, "daynumbers.png")).cut(5, 6))

        self.time = self.TIME_DAY
        playSound("day.mp3")

        self.choice = self.CHOICE_NULL
        self.days = 1

        self.curtainsOpen.start = True
        self.curtainsOpen.show = True
        self.firstrun = False

    def generateCities(self):
        no = False
        city = City((random.randint(25, 90), random.randint(20, 65)), self.scale, self.offset, self.clickSound)
        for c in self.cities:
            if abs(c.pos[0] - city.pos[0]) < 11:
                no = True
                break
        if not no:
            return city
        else:
            return self.generateCities()

    def generateBills(self):
        self.bills += [Bill("Declare state of Emergency", self.alphabet, (-3, -3, -3, 3, 3, 5))]
        self.bills += [Bill(
            "Give a grand to every citizen over the age of eighteen and who are NOT claimed as dependent based on their previous taxes.",
            self.alphabet, (3, 3, 0, -3, -3, 0))]
        self.bills += [Bill("Shut down all non essential businesses for two months to prevent the spread of the virus.",
                            self.alphabet, (-5, -3, -3, 3, 3, 3))]
        self.bills += [Bill("Issue a shelter in place order. ", self.alphabet, (-3, -3, -3, 3, 3, 3))]
        self.bills += [Bill("Issue a curfew of seven PM across the nation. ", self.alphabet, (-3, -3, -3, 3, 3, 3))]
        self.bills += [Bill("Allow the police go into civilian housing with a warrant if suspected to have Covid.",
                            self.alphabet, (0, -5, -1, 0, 5, 1))]
        self.bills += [Bill(
            "Instate a Universal Basic Income of two and a half thousand to every citizen for six months on a renewable basis of every six months until Covid subsides.",
            self.alphabet, (3, 5, 3, -3, -5, -3))]
        self.bills += [Bill("Buy back most weapons in an effort to reduce the likelihood of a revolt.", self.alphabet,
                            (0, -3, -3, 0, 3, 3))]
        self.bills += [Bill("Instate a travel ban on all travel to and from other countries.", self.alphabet,
                            (-3, -3, -3, 3, 3, 3))]
        self.bills += [Bill("Place a ban on travel to other states for one month.", self.alphabet, (-3, -3, -1, 3, 3, 1))]
        self.bills += [Bill(
            "Citizens will be fined up to two thousand dollars or jailed up to six months for having Covid and not quarantining.",
            self.alphabet, (-3, -3, -1, 3, 3, 1))]
        self.bills += [Bill("All businesses must shut down for two weeks effective immediately.", self.alphabet,
                            (-3, -3, -3, 3, 3, 3))]
        self.bills += [Bill(
            "Give businesses a chance to apply for a loan that doesnt need payment for six months and accrue no interest over that time for all businesses that made less than one billion dollars.",
            self.alphabet, (3, 0, 0, -3, 0, 0))]
        self.bills += [Bill("Make all treatment and testing of Covid free.", self.alphabet, (3, 3, -3, -3, -3, 3))]
        self.bills += [Bill("Appropriate money to develop a cure for Covid.", self.alphabet, (1, 3, 3, -3, -3, -3))]
        self.bills += [
            Bill("Allocate more money towards making testing more available across the nation.", self.alphabet,
                 (3, 3, -3, -3, -3, 3))]
        self.bills += [Bill("Allow illegal immigrants to get care at hospitals without being sent home right after.",
                            self.alphabet, (0, -3, -3, 0, 3, 3))]
        self.bills += [Bill("Prohibit immigration for the next sixty days effective immediately.", self.alphabet,
                            (-1, 0, -1, 3, 0, 3))]
        self.bills += [
            Bill("Five G service towers must be taken down out of the fear they may harm civilians.", self.alphabet,
                 (0, -3, 0, 0, 3, 0))]
        self.bills += [Bill(
            "Give orders to hospitals that if there are not enough ventilators at the hospital to prioritize those most likely to survive.",
            self.alphabet, (0, -5, 0, 0, 5, 0))]
        self.bills += [
            Bill("Require most businesses to give all employees a mandatory two weeks paid vacation.", self.alphabet,
                 (-1, 3, -3, 3, -3, 3))]
        self.bills += [
            Bill("Give more money to states to aid in the response to Covid.", self.alphabet, (3, 3, -1, -3, -3, 1))]
        self.bills += [Bill("Give airlines a twenty five Billion dollar bailout due to losses in the industry.", self.alphabet,
                            (1, -3, 0, -3, 3, 0))]
        self.bills += [Bill("Force certain businesses capable of producing ventilators to produce them.", self.alphabet,
                            (-1, 3, -1, 3, -3, 1))]
        self.bills += [Bill(
            "Require school to go to online learning using a platform of their choice, give all students a form of wifi temporarily, and a computer if a student does not have one already.",
            self.alphabet, (-3, 3, 0, 3, -3, 0))]
        self.bills += [Bill("Require universities to extend their deadline to accept to June first.", self.alphabet,
                            (0, 3, -1, 0, -3, 1))]
        self.bills += [Bill("Prioritize cities that have the most cases of Covid first for testing and ventilators.",
                            self.alphabet, (-3, -5, -3, 3, 3, 3))]
        self.bills += [Bill(
            "Require grocery stores to have designated times where people sixty and over can shop and it must be at least one hour or more.",
            self.alphabet, (-3, 3, -3, 3, -3, 3))]
        self.bills += [Bill(
            "Allow anyone that is healthy and has been tested to work for any fire department to help combat the fires that are happening across the country.",
            self.alphabet, (3, 3, 3, -3, -3, -3))]
        self.bills += [Bill(
            "Require schools to create other means of learning to help elementary and middle school aged students learn.",
            self.alphabet, (0, 3, 0, 0, -3, 0))]
        self.bills += [Bill(
            "Quarantine all large cities until further notice. Only grocery stores will be open and rent does not have to be paid during that time but will be owed after the time has passed.",
            self.alphabet, (-3, 3, -3, 3, -3, 3))]

    def toggleMap(self):
        self.showingMap = not self.showingMap

    def toggleBill(self):
        self.showingBill = not self.showingBill

    def voteYes(self):
        self.choice = self.CHOICE_YES

    def voteNo(self):
        self.choice = self.CHOICE_NO

    def readConfig(self):
        f = open("config.conf", "r")
        lines = f.readlines()
        f.close()

        values = lines[0].strip().split(",")

        if values[0] == "True":
            self.objects[1].show = True
        else:
            self.objects[1].show = False

        if values[1] == "True":
            self.objects[2].show = True
        else:
            self.objects[2].show = False

        if values[2] == "True":
            self.objects[3].show = True
        else:
            self.objects[3].show = False

    def writeFile(self, banner, value):
        f = open("config.conf", "r")
        lines = f.readlines()
        f.close()

        values = lines[0].split(",")

        if value:
            values[banner] = "True"
        else:
            values[banner] = "False"

        line = ",".join(values)

        f = open("config.conf", "w")
        f.write(line)
        f.close()

    def changeTime(self):
        if self.choice != self.CHOICE_NULL:
            self.closingStart = False
            self.closingDone = False
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
                self.infectionRate += effects[2]
            elif self.choice == self.CHOICE_NO:
                self.economy += effects[3]
                self.opinion += effects[4]
                self.infectionRate += effects[5]
            self.choice = self.CHOICE_NULL
            self.bills.remove(self.bill)
            self.bill = random.choice(self.bills)
            totalInfection = 0
            for city in self.map.cities:
                totalInfection += city.infection
                if city.quarantined:
                    self.economy -= 1
                    self.opinion -= 5
            self.infection = (totalInfection/(100 * len(self.map.cities))) * 100

            self.infection = cap(0, 100, self.infection)
            self.opinion = cap(0, 100, self.opinion)
            self.economy = cap(0, 100, self.economy)

            if self.infection == 0:
                self.win(COND_INFECTION)
            elif self.opinion == 0:
                self.lose(COND_OPINION)
            elif self.economy == 0:
                self.lose(COND_ECONOMY)
            elif self.days == 15:
                if self.infection < 10:
                    self.win(COND_TIME)
                else:
                    self.neutral()
            else:
                if self.time == self.TIME_DAY:
                    playSound("day.mp3")
                else:
                    playSound("night.mp3")
                self.curtainsOpen.start = True
                self.curtainsOpen.show = True
            print(self.days)

    def win(self, condition):
        if condition == COND_TIME:
            self.winSplash.show = True
        elif condition == COND_INFECTION:
            self.winSplash.show = True
        self.gameover = True
        self.winSound.play()

    def lose(self, condition):
        if condition == COND_ECONOMY:
            self.loseEconomy.show = True
        elif condition == COND_OPINION:
            self.loseOpinion.show = True
        elif condition == COND_INFECTION:
            self.loseInfection.show = True
        self.gameover = True
        self.loseSound.play()

    def neutral(self):
        self.loseTime.show = True
        self.gameover = True
        self.loseSound.play()

    def closeCurtainsDayChange(self):
        if self.choice != self.CHOICE_NULL:
            self.curtainsClose.start = True
            self.curtainsClose.show = True
            self.closingStart = True
            self.closingDone = False

    def closeCurtainsDone(self):
        self.closingDone = True

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
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.gameover:
                    self.restart()
                if not (self.curtainsClose.show or self.curtainsOpen.show):
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
                    if not (self.curtainsClose.show or self.curtainsOpen.show):
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
        if not (self.pause or self.gameover):
            for obj in self.objects:
                obj.update()

            if self.economy > 100:
                self.economy = 100
            elif self.economy < 0:
                self.economy = 0
            if self.economy == 100:
                if not self.objects[1].show:
                    self.objects[1].show = True
                    self.writeFile(0, True)

            if self.opinion > 100:
                self.opinion = 100
            elif self.opinion < 0:
                self.opinion = 0
            if self.opinion == 100:
                if not self.objects[2].show:
                    self.objects[2].show = True
                    self.writeFile(1, True)

            if self.infection > 100:
                self.infection = 100
            elif self.infection < 0:
                self.infection = 0
            if self.infection == 0:
                if not self.objects[3].show:
                    self.objects[3].show = True
                    self.writeFile(2, True)

            self.candle.updateSelf(self.time)
            self.player.update()
            self.uiEconomy.updateSelf(self.economy)
            self.uiInfection.updateSelf(self.infection)
            self.uiOpinion.updateSelf(self.opinion)

            self.curtainsOpen.update()
            self.curtainsClose.update()
        else:
            if self.firstrun:
                self.clicktostart.update()
                self.logo.update()

            if self.loseTime.show:
                self.loseTime.update()

            if self.loseEconomy.show:
                self.loseEconomy.update()

            if self.loseOpinion.show:
                self.loseOpinion.update()

            if self.loseInfection.show:
                self.loseInfection.update()

            if self.winSplash.show:
                self.winSplash.update()

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

        if self.curtainsOpen.show:
            self.curtainsOpen.draw(self.surface)
            if not self.curtainsOpen.start:
                self.clicktostart.draw(self.surface)
                self.logo.draw(self.surface)

        if self.curtainsClose.show:
            self.curtainsClose.draw(self.surface)

        if self.closingStart:
            if self.closingDone:
                self.changeTime()

        if self.loseTime.show:
            self.loseTime.draw(self.surface)

        if self.loseEconomy.show:
            self.loseEconomy.draw(self.surface)

        if self.loseOpinion.show:
            self.loseOpinion.draw(self.surface)

        if self.loseInfection.show:
            self.loseInfection.draw(self.surface)

        if self.winSplash.show:
            self.winSplash.draw(self.surface)

        self.display.blit(
            pygame.transform.scale(self.surface, (self.resolution[0] * self.scale, self.resolution[1] * self.scale)),
            self.offset)
        pygame.display.flip()
