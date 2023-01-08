import pygame
import random
import os
import sys


pygame.init()
size = width, height = 800, 800
screen = pygame.display.set_mode(size)
screen_rect = (0, 0, width, height)
V = 300
FPS = 60


def load_image(name, colorkey=None):
    fullname = os.path.join('pygame/data', name)
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
    ship_image = pygame.transform.scale(image, (125, 100))

    def __init__(self, group):
        super().__init__(group)
        self.image = Ship.ship_image
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = 0, 700
        self.mask = pygame.mask.from_surface(self.ship_image)
        self.hp = 100

    def update(self):
        meteor = pygame.sprite.spritecollideany(self, meteor_group)
        if meteor:
            if pygame.sprite.collide_mask(self, meteor):
                meteor.kill()
                self.take_damage()
        if self.hp <= 0:
            self.kill()
            return True
        return False
    
    def take_damage(self):
        self.hp -= random.choice([5, 10, 15])


class Bullet(pygame.sprite.Sprite):
    image = load_image('bullet.png')
    bullet_image = pygame.transform.scale(image, (75, 75))
    bullet_image = pygame.transform.rotate(bullet_image, 90)

    def __init__(self, *group, x):
        super().__init__(*group)
        self.image = Bullet.bullet_image
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.bullet_image)
        self.rect.x, self.rect.y = x, 650

    def update(self):
        self.rect.y -= V / FPS
        meteor = pygame.sprite.spritecollideany(self, meteor_group)
        if meteor:
            if pygame.sprite.collide_mask(self, meteor):
                self.kill()
                meteor.kill()
        if not self.rect.colliderect(screen_rect):
            self.kill()
        

class Meteor(pygame.sprite.Sprite):
    image = load_image('asteroid.png')
    meteor_image = pygame.transform.scale(image, (80, 80))

    def __init__(self, *group):
        super().__init__(*group)
        self.image = Meteor.meteor_image
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.meteor_image)
        self.rect.x, self.rect.y = random.randrange(720), 0

    def update(self):
        self.rect.y += V / FPS / 2
        if not self.rect.colliderect(screen_rect):
            self.kill()


class Heath:
    def __init__(self):
        self.font = pygame.font.Font(None, 30)
        
    def update(self, ship_hp):
        text = self.font.render(f'Hp {ship_hp}', True, (100, 255, 100))
        return text


if __name__ == '__main__':
    pygame.display.set_caption('Game')
    running, direction = True, 1
    clock = pygame.time.Clock()
    all_sprites = pygame.sprite.Group()
    meteor_group = pygame.sprite.Group()
    bullet_group = pygame.sprite.Group()
    ship = Ship(all_sprites)
    hp_indicator = Heath()
    new_meteor = 0
    bg = load_image('background.jpg')
    while running:
        screen.blit(bg, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    direction = -1
                elif event.key == pygame.K_RIGHT:
                    direction = 1
                if event.key == pygame.K_SPACE:
                    Bullet((bullet_group, all_sprites), x=ship.rect.x + 25)
        if 0 <= ship.rect.x + V / FPS * direction <= width - ship.rect.width:
            ship.rect.x += V / FPS * direction
        new_meteor += 1
        if new_meteor == 60:
            new_meteor = 0
            Meteor((meteor_group, all_sprites))
        bullet_group.update()
        meteor_group.update()
        if ship.update():
            screen.blit(hp_indicator.update(0), (0, 0))
            running = False
        else:
            screen.blit(hp_indicator.update(ship.hp), (0, 0))
        all_sprites.draw(screen)
        clock.tick(FPS)
        pygame.display.flip()
    pygame.quit()