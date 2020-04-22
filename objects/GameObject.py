

class GameObject:
    def __init__(self, animationFrames, pos, timer):
        self.animationFrames = animationFrames
        self.frameNumber = 0
        self.frameTimer = 0
        self.timer = timer
        self.x, self.y = pos[0], pos[1]

    def updateAnimation(self, frame=-1):
        if frame > 0:
            self.frameNumber = frame
        else:
            self.frameNumber += 1
            if self.frameNumber > len(self.animationFrames) - 1:
                self.frameNumber = 0

    def update(self):
        if self.timer > 0:
            self.frameTimer += 1
            if self.frameTimer >= self.timer:
                self.frameTimer = 0
                self.updateAnimation()

    def draw(self, display):
        display.blit(self.animationFrames[self.frameNumber], (self.x, self.y))
