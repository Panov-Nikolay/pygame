import os
import sys
import pygame
import random
import sqlite3
from datetime import datetime


pygame.init()
size1 = width, height = 800, 800
size2 = WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode(size1)
screen_rect = (0, 0, width, height)
FONT1 = pygame.font.Font(None, 50)
FONT2 = pygame.font.Font(None, 20)
V = VX = 300
FPS = 60
DB = 'Records0.db'
PART2 = False


def add_record(name, time):
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("""INSERT INTO records(name, time) VALUES(?, ?)""", (name, time))
    con.commit()
    con.close()


def table():
    con = sqlite3.connect(DB)
    cur = con.cursor()
    start = cur.execute("""SELECT time FROM records WHERE time = (SELECT min(time) FROM records)""").fetchone()[0]
    table = []
    for i in range(start, 500):
        res = cur.execute(f"""SELECT * FROM records WHERE time = {i}""").fetchall()
        for j in range(min(10 - len(table), len(res))):
            table.append(res[j])
    con.close()
    return table


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


def first_level(level=None, meteor_number=5, meteor_speed=V, end=None):
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
        image = load_image('bullet1.png')
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

        def __init__(self, *group, strafe):
            super().__init__(*group)
            self.image = Meteor.meteor_image
            self.rect = self.image.get_rect()
            self.mask = pygame.mask.from_surface(self.meteor_image)
            self.rect.x, self.rect.y = random.randrange(720), 0
            self.strafe = strafe

        def update(self):
            self.rect.x += self.strafe / FPS
            self.rect.y += meteor_speed / FPS / 2
            if not self.rect.colliderect(screen_rect):
                self.kill()

    class Heath:
        def __init__(self):
            self.font = pygame.font.Font(None, 30)

        def update(self, ship_hp):
            pygame.init()
            text = self.font.render(f'Hp {ship_hp}', True, (100, 255, 100))
            return text

    running, direction = True, 1
    clock = pygame.time.Clock()
    all_sprites = pygame.sprite.Group()
    meteor_group = pygame.sprite.Group()
    bullet_group = pygame.sprite.Group()
    ship = Ship(all_sprites)
    hp_indicator = Heath()
    new_meteor = 0
    meteor_count = 0
    recharge = 0
    bg = load_image('background_in_game.jpg')
    while running:
        screen.blit(bg, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    direction = -1
                elif event.key == pygame.K_d:
                    direction = 1
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and recharge == 0:
                Bullet((bullet_group, all_sprites), x=ship.rect.x + 25)
                recharge = 25
        if recharge > 0:
            recharge -= 1
        if 0 <= ship.rect.x + V / FPS * direction <= width - ship.rect.width:
            ship.rect.x += V / FPS * direction
        new_meteor += 1
        if new_meteor == 60:
            if meteor_count < meteor_number:
                new_meteor = 0
                Meteor((meteor_group, all_sprites), strafe=random.choice([-60, -50, -40, 0, 40, 50, 60]))
                meteor_count += 1
        if len(meteor_group) == 0 and meteor_count == meteor_number:
            if end is None:
                end_first_level('Конец первого этапа', level)
            else:
                end()
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
    lose_screen()


def second_level():
    first_level(meteor_number=30, meteor_speed=500, level=second_level, end=end_second_level)


def third_level():
    first_level(meteor_number=50, meteor_speed=500, level=third_level, end=end_third_level)


def start_screen():
    bg = load_image('background.jpg')
    running = True
    font_welcome = pygame.font.Font(None, 50)
    font_text = pygame.font.Font(None, 20)
    welcome = font_welcome.render('Добро пожаловать в игру!', True, (100, 255, 100))
    text = font_text.render('(для продолжения нажмите любую кнопку)', True, (100, 255, 100))
    welcome_rect = welcome.get_rect()
    text_rect = text.get_rect()
    while running:
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONUP:
                first_level(meteor_number=10, meteor_speed=250)
        screen.blit(bg, (0, 0))
        screen.blit(welcome, (width // 2 - welcome_rect.width // 2, height // 2 - welcome_rect.height // 2 - 10))
        screen.blit(text, (width // 2 - text_rect.width // 2, height // 2 - text_rect.height // 2 + 20))
        pygame.display.flip()
    return False


def win_screen(time):
    bg = load_image('background.jpg')
    screen = pygame.display.set_mode(size1)
    font = pygame.font.Font(None, 50)
    clock = pygame.time.Clock()
    win = font.render('Вы победили!', True, (0, 255, 0))
    input_name = font.render('Введите своё имя', True, (0, 255, 0))
    input_rect = input_name.get_rect()
    input_box = pygame.Rect(300, 450, 200, 50)
    color_base = pygame.Color((255, 255, 255))
    color_active = pygame.Color((200, 200, 200))
    color = color_base
    active = False
    text = ''
    running = True
    time2 = datetime.now().time()
    time1 = (time2.hour - time.hour) * 3600 + (time2.minute - time.minute) * 60 + (time2.second - time.second) + 250
    res = font.render('Ваш результат: ' + str(time1), True, (0, 255, 0))
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
                
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
                color = color_active if active else color_base
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        text = ''
                        running = False
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                add_record(text, time1)
                running = False
        screen.blit(bg, (0, 0))
        text_return = font.render(text, True, color)
        input_box.w = max(200, text_return.get_width() + 10)
        screen.blit(text_return, (input_box.x + 5, input_box.y + 5))
        pygame.draw.rect(screen, color, input_box, 2)
        screen.blit(input_name, (width // 2 - input_rect.width // 2, height // 2 - input_rect.height // 2 - 10))
        screen.blit(win, (275, 300))
        screen.blit(res, (260, 600))
        clock.tick(30)
        pygame.display.flip()
    result_screen()

def lose_screen():
    bg = load_image('background.jpg')
    screen = pygame.display.set_mode(size1)
    running = True
    font = pygame.font.Font(None, 50)
    text = font.render('Конец игры', True, (100, 255, 100))
    rect = text.get_rect()
    while running:
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONUP:
                running = False
        screen.blit(bg, (0, 0))
        screen.blit(text, (width // 2 - rect.width // 2, height // 2 - rect.height // 2))
        pygame.display.flip()
    terminate()


def result_screen():
    bg = load_image('background.jpg')
    screen = pygame.display.set_mode(size1)
    running = True
    font = pygame.font.Font(None, 50)
    
    results = table()
    while running:
        screen.fill((255, 255, 255))
        name_x = 20
        name_y = 65
        time_x = 520
        time_y = 65
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONUP:
                running = False
        screen.blit(bg, (0, 0))
        screen.blit(font.render('Таблица рекордов', True, (0, 255, 0)), (250, 5))
        pygame.draw.rect(screen, (0, 255, 0), (10, name_y - 10, 500, 50), 1)
        pygame.draw.rect(screen, (0, 255, 0), (510, time_y - 10, 280, 50), 1)
        name = font.render('Игрок', True, (0, 255, 0))
        time = font.render('Время', True, (0, 255, 0))
        screen.blit(name, (name_x, name_y))
        screen.blit(time, (time_x, time_y))
        for i in range(len(results)):
            name_y += 50
            time_y += 50
            name = font.render(f'{results[i][0]}', True, (0, 255, 0))
            time = font.render(f'{results[i][1]}', True, (0, 255, 0))
            screen.blit(name, (name_x, name_y))
            screen.blit(time, (time_x, time_y))
            pygame.draw.rect(screen, (0, 255, 0), (10, name_y - 10, 500, 50), 1)
            pygame.draw.rect(screen, (0, 255, 0), (510, name_y - 10, 280, 50), 1)
        pygame.display.flip()
    terminate()


def end_first_level(text, level):
    bg = load_image('background.jpg')
    screen = pygame.display.set_mode(size1)
    running = True
    font = pygame.font.Font(None, 50)
    text = font.render(text, True, (100, 255, 100))
    rect = text.get_rect()
    while running:
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                break
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONUP:
                running = False
        screen.blit(bg, (0, 0))
        screen.blit(text, (width // 2 - rect.width // 2, height // 2 - rect.height // 2))
        pygame.display.flip()
    if level is None:
        second_level()
    else:
        level()


def end_second_level():
    text = 'Конец второго этапа'
    end_first_level(text, third_level)


def end_third_level():
    text = 'Конец третьего этапа'
    end_first_level(text, main)


def terminate():
    pygame.quit()
    sys.exit()


def load_level(filename):
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def main():
    wall_image = load_image('wall1.png')
    wall_image = pygame.transform.scale(wall_image, (40, 40))

    tile_images = {
        'wall1': wall_image
    }
    tile_width = tile_height = 40

    class Background(pygame.sprite.Sprite):
        image = load_image('fon1.jpg')
        image = pygame.transform.scale(image, (1280, 720))

        def __init__(self, location):
            super().__init__()
            self.image = Background.image
            self.rect = self.image.get_rect()
            self.rect.left, self.rect.top = location

    class Tile(pygame.sprite.Sprite):
        def __init__(self, tile_type, pos_x, pos_y):
            super().__init__(tile_group, all_sprites)
            self.image = tile_images[tile_type]
            self.rect = self.image.get_rect().move(
                tile_width * pos_x, tile_height * pos_y)
            self.mask = pygame.mask.from_surface(self.image)

    class Hero(pygame.sprite.Sprite):
        image = load_image('hero.png')
        hero_image = pygame.transform.scale(image, (80, 100))

        def __init__(self, x, y):
            super().__init__(hero_group)
            self.image = Hero.hero_image
            self.rect = self.image.get_rect()
            self.rect.x = x * 40
            self.rect.y = y * 40 + 40
            self.mask = pygame.mask.from_surface(self.image)
            self.vy = 0
            self.back = 0
            self.in_air = 2
            self.health = 100

        def update(self):
            for i in tile_group:
                if pygame.sprite.collide_mask(self, i) and 0 < self.rect.right - i.rect.left < 40:
                    self.rect.x -= 5
                if pygame.sprite.collide_mask(self, i) and 0 < i.rect.right - self.rect.left < 40:
                    self.rect.x += 5
                if pygame.sprite.collide_mask(self, i) and 0 < self.rect.bottom - i.rect.top < 40:
                    self.rect.y -= self.rect.bottom - i.rect.top + 1
                    self.in_air, self.vy = 0, 0
                if pygame.sprite.collide_mask(self, i) and 0 < i.rect.bottom - self.rect.top < 40:
                    self.rect.y += i.rect.bottom - self.rect.top + 1
                    self.in_air, self.vy = 2, 0
            for j in enemy_group:
                if pygame.sprite.collide_mask(self, j):
                    self.back = 100
                    self.in_air = 2
                    self.health -= 5
                    break
            if self.health <= 0:
                self.kill()
                lose_screen()

    class Bullet(pygame.sprite.Sprite):
        image = load_image('bullet1.png')
        bullet_image = pygame.transform.scale(image, (20, 20))

        def __init__(self, x, y, direct):
            super().__init__(bullet_group, all_sprites)
            self.image = Bullet.bullet_image
            if direct == -1:
                self.image = pygame.transform.rotate(self.image, 180)
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y
            self.direction = direct
            self.mask = pygame.mask.from_surface(self.image)

        def update(self):
            if not -50 <= self.rect.x <= WIDTH or not -50 <= self.rect.y <= HEIGHT:
                self.kill()
            for i in tile_group:
                if pygame.sprite.collide_mask(self, i):
                    self.kill()
            for i in enemy_group:
                if pygame.sprite.collide_mask(self, i):
                    i.health -= 40
                    self.kill()
            self.rect.x += VX * 2 / FPS * self.direction

    class EnBullet(pygame.sprite.Sprite):
        image = load_image('bullet1.png')
        en_bullet_image = pygame.transform.scale(image, (20, 20))

        def __init__(self, x, y, direct):
            super().__init__(en_bullet_group, all_sprites)
            self.image = EnBullet.en_bullet_image
            if direct == -1:
                self.image = pygame.transform.rotate(self.image, 180)
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y
            self.direction = direct
            self.mask = pygame.mask.from_surface(self.image)

        def update(self):
            if not -50 <= self.rect.x <= WIDTH or not -50 <= self.rect.y <= HEIGHT:
                self.kill()
            for i in tile_group:
                if pygame.sprite.collide_mask(self, i):
                    self.kill()
            for i in hero_group:
                if pygame.sprite.collide_mask(self, i):
                    i.health -= 5
                    self.kill()
            self.rect.x += VX * 1.5 / FPS * self.direction

    class Enemy(pygame.sprite.Sprite):
        image = load_image('enemy1.png')
        enemy_image = pygame.transform.scale(image, (80, 100))

        def __init__(self, x, y):
            super().__init__(enemy_group, all_sprites)
            self.image = Enemy.enemy_image
            self.rect = self.image.get_rect()
            self.rect.x = x * 40
            self.rect.y = y * 40 - 60
            self.mask = pygame.mask.from_surface(self.image)
            self.direction = 1
            self.is_bullet = 0
            self.health = 100

        def update(self):
            reverse = True
            for i in tile_group:
                if reverse and i.rect.x <= self.rect.centerx <= i.rect.x + 40 and \
                        i.rect.y <= self.rect.y + 110 <= i.rect.y + 40:
                    reverse = False
                if pygame.sprite.collide_mask(self, i):
                    self.direction *= -1
                    self.image = pygame.transform.flip(self.image, True, False)
                    screen.blit(self.image, self.rect)
            if reverse:
                self.direction *= -1
                self.image = pygame.transform.flip(self.image, True, False)
                screen.blit(self.image, self.rect)
            if ((hero.rect.x - self.rect.x) ** 2 + (hero.rect.y - self.rect.y) ** 2) ** 0.5 <= 500:
                direct_now = self.direction
                self.direction = -1 if self.rect.x > hero.rect.x else 1
                if direct_now != self.direction:
                    self.image = pygame.transform.flip(self.image, True, False)
                    screen.blit(self.image, self.rect)
                if abs(hero.rect.y - self.rect.y) <= 100 and self.is_bullet == 0:
                    EnBullet(x=self.rect.x + 40, y=self.rect.y + 20, direct=self.direction)
                    self.is_bullet = 60
            else:
                self.rect.x += self.direction
            if self.is_bullet > 0:
                self.is_bullet -= 1
            if self.health < 0:
                self.kill()

    class Camera:
        def __init__(self):
            self.dx = 0

        def apply(self, obj):
            obj.rect.x += self.dx

        def update(self, target):
            self.dx = -(target.rect.x + target.rect.w // 2 - WIDTH // 2)

    def generate_level(level):
        new_player, x, y = None, None, None
        for y in range(len(level)):
            for x in range(len(level[y])):
                if level[y][x] == '1':
                    Tile('wall1', x, y)
                elif level[y][x] == '@':
                    new_player = Hero(x, y)
                elif level[y][x] == 'x':
                    Enemy(x, y)
        return new_player, x, y

    def hero_update(player, group, air):
        for i in group:
            if pygame.sprite.collide_mask(player, i):
                hero.rect.bottom = hero.rect.bottom // 40 * 40
                return 0
        return 2 if air == 0 else air

    screen = pygame.display.set_mode(size2)
    time1 = datetime.now().time()
    print(time1)
    pygame.display.set_caption('Robot_attack')
    direction = 0
    side = 1
    bullets, recharge = 8, 0
    to_norm_angle = 31
    up = 0
    clock = pygame.time.Clock()
    all_sprites = pygame.sprite.Group()
    bullet_group = pygame.sprite.Group()
    tile_group = pygame.sprite.Group()
    hero_group = pygame.sprite.Group()
    enemy_group = pygame.sprite.Group()
    en_bullet_group = pygame.sprite.Group()
    hero, level_x, level_y = generate_level(load_level('data/level1.txt'))
    camera = Camera()
    bg = Background([0, 0])
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or hero.rect.y > 1000:
                lose_screen()
            if event.type == pygame.KEYUP:
                if event.key in (pygame.K_d, pygame.K_a):
                    direction = 0
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_d:
                    direction, side = 1, 1
                if event.key == pygame.K_a:
                    direction, side = -1, -1
                if event.key == pygame.K_SPACE and hero.in_air < 2 and to_norm_angle == 31:
                    hero.vy = 400
                    hero.in_air += 1
                if event.key == pygame.K_s and to_norm_angle == 31:
                    hero.image = pygame.transform.rotate(hero.image, 90)
                    hero.rect.y += 40
                    screen.blit(hero.image, hero.rect)
                    to_norm_angle = 0
                    hero.in_air = 2
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and bullets > 0:
                x1 = hero.rect.x + 100 if side == 1 else hero.rect.x - 50
                Bullet(x=x1, y=hero.rect.y + 20, direct=side)
                bullets -= 1
        if 0 <= hero.rect.x + VX / FPS * direction <= 11800:
            hero.rect.x += VX / FPS * direction
        if hero.in_air > 0:
            hero.rect.y -= hero.vy / FPS
            hero.vy -= 10
        if hero.back > 0:
            hero.rect.x += hero.back // 2
            hero.back //= 2
        if bullets == 0:
            recharge += 1
            if recharge == 180:
                recharge = 0
                bullets = 8
        if to_norm_angle == 30:
            hero.image = pygame.transform.rotate(hero.image, 270)
            up = 8
            screen.blit(hero.image, hero.rect)
            to_norm_angle += 1
        elif to_norm_angle < 30:
            to_norm_angle += 1
        if up > 0:
            hero.rect.y -= 5
            up -= 1
        hero.in_air = hero_update(hero, tile_group, hero.in_air)
        bullet_group.update()
        hero_group.update()
        enemy_group.update()
        en_bullet_group.update()
        camera.update(hero)
        camera.apply(hero)
        for sprite in all_sprites:
            camera.apply(sprite)
        screen.fill([255, 255, 255])
        screen.blit(bg.image, bg.rect)
        count_rendered = FONT1.render('bullets: ' + str(bullets), 1, (255, 255, 255))
        screen.blit(count_rendered, (200, 10))
        heath_rendered = FONT1.render('HP: ' + str(hero.health), 1, (255, 255, 255))
        screen.blit(heath_rendered, (30, 10))
        enemy_count = FONT1.render('enemy: ' + str(len(enemy_group.sprites())), 1, (255, 255, 255))
        screen.blit(enemy_count, (400, 10))
        if len(enemy_group.sprites()) == 0:
            win_screen(time1)
        for i in enemy_group:
            screen.blit(FONT2.render(str(i.health), 1, (255, 0, 0)), (i.rect.x + 20, i.rect.y - 20))
        if side == -1:
            screen.blit(pygame.transform.flip(hero.image, True, False), hero.rect)
        else:
            hero_group.draw(screen)
        all_sprites.draw(screen)
        clock.tick(FPS)
        pygame.display.flip()


if __name__ == '__main__':
    start_screen()
