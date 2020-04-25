import pygame


class SpriteSheet:
    def __init__(self, sheet):
        self.sheet = sheet.convert_alpha()

    def cut(self, sizeX, sizeY):
        images = []
        x = self.sheet.get_width() // sizeX
        y = self.sheet.get_height() // sizeY

        for i in range(y):
            for j in range(x):
                cutImage = pygame.Surface((sizeX, sizeY), pygame.SRCALPHA)
                cutImage.blit(self.sheet, (0, 0), (j * sizeX, i * sizeY, sizeX, sizeY))

                images += [cutImage]

        return images
