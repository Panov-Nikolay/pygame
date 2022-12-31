import pygame
import random
import os
import sys


pygame.init()
size = width, height = 800, 800
screen = pygame.display.set_mode(size)
V = 300
FPS = 60


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


class Ship(pygame.sprite.Sprite):
    image = load_image('spaceship.png')
    ship_image = pygame.transform.scale(image, (150, 100))

    def __init__(self, group):
        super().__init__(group)
        self.image = Ship.ship_image
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = 0, 700

    def update(self):
        if pygame.sprite.spritecollideany(self, meteor_group):
            self.kill()
            return True
        return False


class Bullet(pygame.sprite.Sprite):
    image = load_image('bullet.png')
    bullet_image = pygame.transform.scale(image, (75, 75))
    bullet_image = pygame.transform.rotate(bullet_image, 90)

    def __init__(self, *group, x):
        super().__init__(*group)
        self.image = Bullet.bullet_image
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, 650

    def update(self):
        self.rect.y -= V / FPS
        if pygame.sprite.spritecollideany(self, meteor_group):
            self.kill()
        pygame.sprite.spritecollide(self, meteor_group, True)
 

class Meteor(pygame.sprite.Sprite):
    image = load_image('asteroid.jpg')
    meteor_image = pygame.transform.scale(image, (80, 80))

    def __init__(self, *group):
        super().__init__(*group)
        self.image = Meteor.meteor_image
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = random.randrange(720), 0

    def update(self):
        self.rect.y += V / FPS / 2


if __name__ == '__main__':
    pygame.display.set_caption('Game')
    running, direction = True, 1
    clock = pygame.time.Clock()
    all_sprites = pygame.sprite.Group()
    meteor_group = pygame.sprite.Group()
    bullet_group = pygame.sprite.Group()
    ship = Ship(all_sprites)
    new_meteor = 0
    while running:
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    direction = -1
                elif event.key == pygame.K_RIGHT:
                    direction = 1
                if event.key == pygame.K_SPACE:
                    Bullet((bullet_group, all_sprites), x=ship.rect.x + 75)
        if 0 <= ship.rect.x + V / FPS * direction <= 650:
            ship.rect.x += V / FPS * direction
        new_meteor += 1
        if new_meteor == 60:
            new_meteor = 0
            Meteor((meteor_group, all_sprites))
        bullet_group.update()
        meteor_group.update()
        if ship.update():
            running = False
        all_sprites.draw(screen)
        clock.tick(FPS)
        pygame.display.flip()
    pygame.quit()
