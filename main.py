import pygame
import random

import sys
import os


def terminate():
    pygame.quit()
    sys.exit()


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)

    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        terminate()
    image = pygame.image.load(fullname)

    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()

    return image


# Нижняя полоска с информацией о кол-ве жизней, пуль, общем счёте и т д
class InfoTable(pygame.sprite.Sprite):
    def __init__(self, *group):
        super().__init__(*group)

        # Создаем поверхность, на которой всё будет отображаться
        self.image = pygame.Surface([WIDTH, 50])
        self.rect = pygame.Rect(0, HEIGHT - 50, WIDTH, 50)

        # Здесь храним инфу о состоянии игрока
        self.count_lives = 3
        self.count_bullets = 8
        self.kills = 0
        self.count_shields = 0

        self.draw_info()

    def draw_info(self):
        pygame.draw.rect(self.image, (100, 100, 100), (0, 0, WIDTH, 50))

        # рисуем сердечки
        hurt = pygame.transform.scale(load_image('hurt.png'), (50, 50))
        for i in range(self.count_lives):
            self.image.blit(hurt, (50 + 50 * i, 0))

        # рисуем количество пуль
        bullet = pygame.transform.scale(load_image('bullet.png'), (50, 50))
        for i in range(self.count_bullets):
            self.image.blit(bullet, (WIDTH - 190 + 20 * i, 0))

        # рисуем количество щитов
        shield = pygame.transform.scale(load_image('shield.png'), (90, 50))
        for i in range(self.count_shields):
            self.image.blit(shield, (WIDTH - 400 + 40 * i, 0))

        # рисуем надпись "Kills"
        font = pygame.font.Font(None, 80)
        text_kills = font.render(f"Kills: {self.kills}", True, (0, 255, 0))
        self.image.blit(text_kills, (WIDTH // 2 - text_kills.get_width() // 2, 0))

    # у класса особый метод update, требующий определенных аргументов, вызывать только в собственной группе!!!
    def update(self, lives, bullets, shields):
        global score
        self.count_lives = lives
        self.count_bullets = bullets
        self.kills = score
        self.count_shields = shields
        self.draw_info()


class Bullets(pygame.sprite.Sprite):
    def __init__(self, *group, **kwargs):
        super().__init__(*group)

        self.image = pygame.transform.scale(load_image('bullet.png'), (30, 30))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = kwargs['x'], kwargs['y']
        self.mask = pygame.mask.from_surface(self.image)

        # Основные параметры пули
        self.direction = kwargs['direction']
        self.speed = 5

    def update(self, player, boss, enemy1, enemy2, enemy3, enemy4, enemy5, enemy6):
        # Проверяем пересечение с игроком
        if pygame.sprite.collide_mask(self, player):
            self.kill()
            player.sub_live()
            player.catch_fire()
        # Проверяем пересечение с боссом, если он существует
        elif boss and pygame.sprite.collide_mask(self, boss) and self.direction == 'UP':
            self.kill()
            boss.sub_live()
            boss.catch_fire()
        # Проверяем пересечение с врагом 1, если он существует
        elif enemy1 and pygame.sprite.collide_mask(self, enemy1) and self.direction == 'UP':
            self.kill()
            enemy1.sub_live()
            enemy1.catch_fire()
        # Проверяем пересечение с врагом 2, если он существует
        elif enemy2 and pygame.sprite.collide_mask(self, enemy2) and self.direction == 'UP':
            self.kill()
            enemy2. sub_live()
            enemy2.catch_fire()
        # Проверяем пересечение с врагом 3, если он существует
        elif enemy3 and pygame.sprite.collide_mask(self, enemy3) and self.direction == 'UP':
            self.kill()
            enemy3.sub_live()
            enemy3.catch_fire()
        # Проверяем пересечение с врагом 4, если он существует
        elif enemy4 and pygame.sprite.collide_mask(self, enemy4) and self.direction == 'UP':
            self.kill()
            enemy4.sub_live()
            enemy4.catch_fire()
        # Проверяем пересечение с врагом 5, если он существует
        elif enemy5 and pygame.sprite.collide_mask(self, enemy5) and self.direction == 'UP':
            self.kill()
            enemy5.sub_live()
            enemy5.catch_fire()
        # Проверяем пересечение с врагом 6, если он существует
        elif enemy6 and pygame.sprite.collide_mask(self, enemy6) and self.direction == 'UP':
            self.kill()
            enemy6.sub_live()
            enemy6.catch_fire()
        else:
            # Двигаем пулю
            if self.direction == 'UP':
                self.rect = self.rect.move(0, -self.speed)
            elif self.direction == 'DOWN':
                self.rect = self.rect.move(0, self.speed)


class SpaceShip(pygame.sprite.Sprite):
    def __init__(self, *group):
        super().__init__(*group)

        self.orig_image = pygame.transform.scale(load_image('space_ship.png'), (120, 120))
        self.image = self.orig_image.copy()
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = WIDTH - WIDTH // 2 - self.image.get_width(), HEIGHT - self.image.get_height() - 50
        self.mask = pygame.mask.from_surface(self.image)

        # Параметры игрока
        self.speed = 5
        self.lives = 5
        self.bullets = 8
        self.kills = 0
        self.timer = 0  # таймер необходимый для обозначения времени возгорания при попадении
        self.fired = False  # Здесь храниться значение: подбили только что корабль или нет
        self.triple_bullets = 0  # Здесь храниться значение: сколько двойных выстрелов можно совершить
        self.shields = 3

    def update(self, *args):
        k_left = pygame.key.get_pressed()[pygame.K_LEFT]
        k_right = pygame.key.get_pressed()[pygame.K_RIGHT]

        # Проверяем нажатие на клавишы лево-право и двигаем игрока
        if k_left and not k_right and 0 < self.rect.x - self.speed:
            self.rect = self.rect.move(-self.speed, 0)
        if k_right and not k_left and self.rect.x + self.speed < WIDTH - self.rect.width:
            self.rect = self.rect.move(self.speed, 0)

        # Проверяем, прошло ли время возгорания, если оно есть (пора ли картинку делать обратно более темной)
        if self.timer == 30:
            self.image = self.orig_image.copy()
            self.fired = False
            self.timer = 0
        # Если корабль горит увеличиваем таймер возгорания
        if self.fired:
            self.timer += 1

    # Функция делает картинку более светлой на время (так обозначается возгорание при попадании)
    def catch_fire(self):
        if not self.fired:
            self.image.fill((100, 100, 100), special_flags=pygame.BLEND_RGB_ADD)
            self.fired = True
            self.timer = 0

    def fire(self, *groups):
        if self.bullets and self.triple_bullets == 0:
            self.bullets -= 1
            Bullets(*groups, x=self.rect.x + self.image.get_width() // 2 - 15, y=self.rect.y - 15, direction='UP')
        elif self.bullets and self.triple_bullets > 0:
            self.triple_bullets -= 1
            Bullets(*groups, x=self.rect.x + self.image.get_width() // 2 - 58, y=self.rect.y + 20, direction='UP')
            Bullets(*groups, x=self.rect.x + self.image.get_width() // 2 - 15, y=self.rect.y - 15, direction='UP')
            Bullets(*groups, x=self.rect.x + self.image.get_width() // 2 + 32, y=self.rect.y + 20, direction='UP')

    def add_bullet(self):
        if self.bullets < 8:
            self.bullets += 1

    def sub_live(self):
        if self.shields == 0:
            self.lives -= 1
        elif self.shields:
            self.shields -= 1


class Boss(pygame.sprite.Sprite):
    def __init__(self, *group):
        super().__init__(*group)

        self.orig_image = pygame.transform.scale(load_image('boss.png'), (450, 200))
        self.image = self.orig_image.copy()
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(0, WIDTH - self.image.get_width())
        self.rect.y = -self.image.get_height()
        self.mask = pygame.mask.from_surface(self.image)

        # Параметры босса
        self.direction = random.choice([1, -1])  # Если +1, то босс движется вправо, если -1, то влево
        self.lives = 15
        self.speed = 1
        self.timer = 0  # таймер необходимый для обозначения времени возгорания при попадении
        self.fired = False  # Здесь храниться значение: подбили только что босса или нет

    def move(self):
        # Проверяем соприкосновение босса со стенками и двигаем его
        if not (0 < self.rect.x and self.rect.x + self.rect.width < WIDTH):
            self.direction *= -1
        self.rect = self.rect.move(self.speed * self.direction, self.speed)

    def fire(self, *groups):
        Bullets(*groups, x=self.rect.x + self.image.get_width() // 2 - 15,
                y=self.rect.y + self.rect.height, direction='DOWN')
        Bullets(*groups, x=self.rect.x + self.image.get_width() // 2 - 15 - 50,
                y=self.rect.y + self.rect.height, direction='DOWN')
        Bullets(*groups, x=self.rect.x + self.image.get_width() // 2 - 15 + 50,
                y=self.rect.y + self.rect.height, direction='DOWN')
        Bullets(*groups, x=self.rect.x + self.image.get_width() // 2 - 15 - 100,
                y=self.rect.y + self.rect.height, direction='DOWN')
        Bullets(*groups, x=self.rect.x + self.image.get_width() // 2 - 15 + 100,
                y=self.rect.y + self.rect.height, direction='DOWN')

    def sub_live(self):
        self.lives -= 1
        if self.lives == 0:
            self.destroy()

    # Функция делает картинку более светлой на время (так обозначается возгорание при попадании)
    def catch_fire(self):
        if not self.fired:
            self.image.fill((100, 100, 100), special_flags=pygame.BLEND_RGB_ADD)
            self.fired = True
            self.timer = 0

    def destroy(self):
        global score
        score += 1
        self.kill()

    # Возвращает None, если босс мёртв (для перезаписи переменной boss)
    def return_alive(self):
        if len(self.groups()) == 0:
            return None
        return self

    # Возвращает True, если босс дошел до нижней границы или пересекся с игроком
    def return_collisions_with_front(self, info_table, player):
        if pygame.sprite.collide_mask(self, info_table) or pygame.sprite.collide_mask(self, player):
            return True
        return False

    def update(self, *args, **kwargs):
        # Проверяем, прошло ли время возгорания, если оно есть (пора ли картинку делать обратно более темной)
        if self.timer == 30:
            self.image = self.orig_image.copy()
            self.fired = False
            self.timer = 0
        # Если корабль горит увеличиваем таймер возгорания
        if self.fired:
            self.timer += 1


class Enemy1(pygame.sprite.Sprite):
    def __init__(self, *group):
        super().__init__(*group)

        self.orig_image = pygame.transform.scale(load_image('enemy1.png'), (90, 55))
        self.image = self.orig_image.copy()
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(0, WIDTH - self.image.get_width())
        self.rect.y = -self.image.get_height()
        self.mask = pygame.mask.from_surface(self.image)

        # Параметры врага 1
        self.direction = random.choice([4, -4])  # Если +2, то враг движется вправо, если -2, то влево
        self.lives = 2
        self.speed = 1
        self.timer = 0  # таймер необходимый для обозначения времени возгорания при попадении
        self.fired = False  # Здесь храниться значение: подбили только что корабль или нет

    def move(self):
        # Проверяем соприкосновение врага 1 со стенками и двигаем его
        if not (0 < self.rect.x and self.rect.x + self.rect.width < WIDTH):
            self.direction *= -1
        self.rect = self.rect.move(self.speed * self.direction, self.speed)

    def fire(self, *groups):
        Bullets(*groups, x=self.rect.x + self.image.get_width() // 2 - 25,
                y=self.rect.y + self.rect.height, direction='DOWN')

    def sub_live(self):
        self.lives -= 1
        if self.lives == 0:
            self.destroy()

    # Функция делает картинку более светлой на время (так обозначается возгорание при попадании)
    def catch_fire(self):
        if not self.fired:
            self.image.fill((100, 100, 100), special_flags=pygame.BLEND_RGB_ADD)
            self.fired = True
            self.timer = 0

    def destroy(self):
        global score
        score += 1
        self.kill()

    # Возвращает None, если враг 1 мёртв (для перезаписи переменной boss)
    def return_alive(self):
        if len(self.groups()) == 0:
            return None
        return self

    # Возвращает True, если враг 1 дошел до нижней границы или пересекся с игроком
    def return_collisions_with_front(self, info_table, player):
        if pygame.sprite.collide_mask(self, info_table) or pygame.sprite.collide_mask(self, player):
            return True
        return False

    def update(self, *args, **kwargs):
        # Проверяем, прошло ли время возгорания, если оно есть (пора ли картинку делать обратно более темной)
        if self.timer == 30:
            self.image = self.orig_image.copy()
            self.fired = False
            self.timer = 0
        # Если корабль горит увеличиваем таймер возгорания
        if self.fired:
            self.timer += 1


class Enemy2(pygame.sprite.Sprite):
    def __init__(self, *group):
        super().__init__(*group)

        self.orig_image = pygame.transform.scale(load_image('enemy2.png'), (150, 70))
        self.image = self.orig_image.copy()
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(0, WIDTH - self.image.get_width())
        self.rect.y = -self.image.get_height()
        self.mask = pygame.mask.from_surface(self.image)

        # Параметры врага 2
        self.direction = random.choice([2, -2])  # Если +2, то враг движется вправо, если -2, то влево
        self.lives = 3
        self.speed = 1
        self.timer = 0  # таймер необходимый для обозначения времени возгорания при попадении
        self.fired = False  # Здесь храниться значение: подбили только что корабль или нет

    def fire(self, *groups):
        Bullets(*groups, x=self.rect.x + self.image.get_width() // 2 - 15 - 20,
                y=self.rect.y + self.rect.height, direction='DOWN')
        Bullets(*groups, x=self.rect.x + self.image.get_width() // 2 - 15 + 30,
                y=self.rect.y + self.rect.height, direction='DOWN')
        Bullets(*groups, x=self.rect.x + self.image.get_width() // 2 - 15 - 70,
                y=self.rect.y + self.rect.height, direction='DOWN')

    def sub_live(self):
        self.lives -= 1
        if self.lives == 0:
            self.destroy()

    def move(self):
        # Проверяем соприкосновение врага 4  со стенками и двигаем его
        if not (0 < self.rect.x and self.rect.x + self.rect.width < WIDTH):
            self.direction *= -1
        self.rect = self.rect.move(self.speed * self.direction, self.speed)

    # Функция делает картинку более светлой на время (так обозначается возгорание при попадании)
    def catch_fire(self):
        if not self.fired:
            self.image.fill((100, 100, 100), special_flags=pygame.BLEND_RGB_ADD)
            self.fired = True
            self.timer = 0

    def destroy(self):
        global score
        score += 1
        self.kill()

    # Возвращает None, если враг 2 мёртв (для перезаписи переменной enemy2)
    def return_alive(self):
        if len(self.groups()) == 0:
            return None
        return self

    # Возвращает True, если враг 2 дошел до нижней границы или пересекся с игроком
    def return_collisions_with_front(self, info_table, player):
        if pygame.sprite.collide_mask(self, info_table) or pygame.sprite.collide_mask(self, player):
            return True
        return False

    def update(self, *args, **kwargs):
        # Проверяем, прошло ли время возгорания, если оно есть (пора ли картинку делать обратно более темной)
        if self.timer == 30:
            self.image = self.orig_image.copy()
            self.fired = False
            self.timer = 0
        # Если корабль горит увеличиваем таймер возгорания
        if self.fired:
            self.timer += 1


class Enemy3(pygame.sprite.Sprite):
    def __init__(self, *group):
        super().__init__(*group)

        self.orig_image = pygame.transform.scale(load_image('enemy3.png'), (150, 70))
        self.image = self.orig_image.copy()
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(0, WIDTH - self.image.get_width())
        self.rect.y = -self.image.get_height()
        self.mask = pygame.mask.from_surface(self.image)

        # Параметры врага 3
        self.direction = random.choice([2, -2])  # Если +2, то враг движется вправо, если -2, то влево
        self.lives = 2
        self.speed = 2
        self.timer = 0  # таймер необходимый для обозначения времени возгорания при попадении
        self.fired = False  # Здесь храниться значение: подбили только что корабль или нет

    def fire(self, *groups):
        Bullets(*groups, x=self.rect.x + self.image.get_width() // 2 - 15 - 20,
                y=self.rect.y + self.rect.height, direction='DOWN')
        Bullets(*groups, x=self.rect.x + self.image.get_width() // 2 - 15 - 70,
                y=self.rect.y + self.rect.height, direction='DOWN')

    def sub_live(self):
        self.lives -= 1
        if self.lives == 0:
            self.destroy()

    def move(self):
        # Проверяем соприкосновение врага 3 со стенками и двигаем его
        if not (0 < self.rect.x and self.rect.x + self.rect.width < WIDTH):
            self.direction *= -1
        self.rect = self.rect.move(self.speed * self.direction, self.speed)

    # Функция делает картинку более светлой на время (так обозначается возгорание при попадании)
    def catch_fire(self):
        if not self.fired:
            self.image.fill((100, 100, 100), special_flags=pygame.BLEND_RGB_ADD)
            self.fired = True
            self.timer = 0

    def destroy(self):
        global score
        score += 1
        self.kill()

    # Возвращает None, если враг 3 мёртв (для перезаписи переменной enemy2)
    def return_alive(self):
        if len(self.groups()) == 0:
            return None
        return self

    # Возвращает True, если враг 3 дошел до нижней границы или пересекся с игроком
    def return_collisions_with_front(self, info_table, player):
        if pygame.sprite.collide_mask(self, info_table) or pygame.sprite.collide_mask(self, player):
            return True
        return False

    def update(self, *args, **kwargs):
        # Проверяем, прошло ли время возгорания, если оно есть (пора ли картинку делать обратно более темной)
        if self.timer == 30:
            self.image = self.orig_image.copy()
            self.fired = False
            self.timer = 0
        # Если корабль горит увеличиваем таймер возгорания
        if self.fired:
            self.timer += 1


class Enemy4(pygame.sprite.Sprite):
    def __init__(self, *group):
        super().__init__(*group)

        self.orig_image = pygame.transform.scale(load_image('enemy4.png'), (170, 90))
        self.image = self.orig_image.copy()
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(0, WIDTH - self.image.get_width())
        self.rect.y = -self.image.get_height()
        self.mask = pygame.mask.from_surface(self.image)

        # Параметры врага 4
        self.direction = random.choice([3, -3])  # Если +2, то враг движется вправо, если -2, то влево
        self.lives = 4
        self.speed = 1
        self.timer = 0  # таймер необходимый для обозначения времени возгорания при попадении
        self.fired = False  # Здесь храниться значение: подбили только что корабль или нет

    def fire(self, *groups):
        Bullets(*groups, x=self.rect.x + self.image.get_width() // 2 - 15 + 15,
                y=self.rect.y + self.rect.height, direction='DOWN')
        Bullets(*groups, x=self.rect.x + self.image.get_width() // 2 - 15 - 35,
                y=self.rect.y + self.rect.height, direction='DOWN')

    def sub_live(self):
        self.lives -= 1
        if self.lives == 0:
            self.destroy()

    def move(self):
        # Проверяем соприкосновение врага 4 со стенками и двигаем его
        if not (0 < self.rect.x and self.rect.x + self.rect.width < WIDTH):
            self.direction *= -1
        self.rect = self.rect.move(self.speed * self.direction, self.speed)

    # Функция делает картинку более светлой на время (так обозначается возгорание при попадании)
    def catch_fire(self):
        if not self.fired:
            self.image.fill((100, 100, 100), special_flags=pygame.BLEND_RGB_ADD)
            self.fired = True
            self.timer = 0

    def destroy(self):
        global score
        score += 1
        self.kill()

    # Возвращает None, если враг 4 мёртв (для перезаписи переменной enemy2)
    def return_alive(self):
        if len(self.groups()) == 0:
            return None
        return self

    # Возвращает True, если враг 4 дошел до нижней границы или пересекся с игроком
    def return_collisions_with_front(self, info_table, player):
        if pygame.sprite.collide_mask(self, info_table) or pygame.sprite.collide_mask(self, player):
            return True
        return False

    def update(self, *args, **kwargs):
        # Проверяем, прошло ли время возгорания, если оно есть (пора ли картинку делать обратно более темной)
        if self.timer == 30:
            self.image = self.orig_image.copy()
            self.fired = False
            self.timer = 0
        # Если корабль горит увеличиваем таймер возгорания
        if self.fired:
            self.timer += 1


class Enemy5(pygame.sprite.Sprite):
    def __init__(self, *group):
        super().__init__(*group)

        self.orig_image = pygame.transform.scale(load_image('enemy5.png'), (170, 90))
        self.image = self.orig_image.copy()
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(0, WIDTH - self.image.get_width())
        self.rect.y = -self.image.get_height()
        self.mask = pygame.mask.from_surface(self.image)

        # Параметры врага 5
        self.direction = random.choice([1, -1])  # Если +2, то враг движется вправо, если -2, то влево
        self.lives = 3
        self.speed = 1
        self.timer = 0  # таймер необходимый для обозначения времени возгорания при попадении
        self.fired = False  # Здесь храниться значение: подбили только что корабль или нет

    def fire(self, *groups):
        Bullets(*groups, x=self.rect.x + self.image.get_width() // 2 - 15 + 15,
                y=self.rect.y + self.rect.height, direction='DOWN')
        Bullets(*groups, x=self.rect.x + self.image.get_width() // 2 - 15 - 35,
                y=self.rect.y + self.rect.height, direction='DOWN')

    def sub_live(self):
        self.lives -= 1
        if self.lives == 0:
            self.destroy()

    def move(self):
        # Проверяем соприкосновение врага 5 со стенками и двигаем его
        if not (0 < self.rect.x and self.rect.x + self.rect.width < WIDTH):
            self.direction *= -1
        self.rect = self.rect.move(self.speed * self.direction, self.speed)

    # Функция делает картинку более светлой на время (так обозначается возгорание при попадании)
    def catch_fire(self):
        if not self.fired:
            self.image.fill((100, 100, 100), special_flags=pygame.BLEND_RGB_ADD)
            self.fired = True
            self.timer = 0

    def destroy(self):
        global score
        score += 1
        self.kill()

    # Возвращает None, если враг 5 мёртв (для перезаписи переменной enemy2)
    def return_alive(self):
        if len(self.groups()) == 0:
            return None
        return self

    # Возвращает True, если враг 5 дошел до нижней границы или пересекся с игроком
    def return_collisions_with_front(self, info_table, player):
        if pygame.sprite.collide_mask(self, info_table) or pygame.sprite.collide_mask(self, player):
            return True
        return False

    def update(self, *args, **kwargs):
        # Проверяем, прошло ли время возгорания, если оно есть (пора ли картинку делать обратно более темной)
        if self.timer == 30:
            self.image = self.orig_image.copy()
            self.fired = False
            self.timer = 0
        # Если корабль горит увеличиваем таймер возгорания
        if self.fired:
            self.timer += 1


class Enemy6(pygame.sprite.Sprite):
    def __init__(self, *group):
        super().__init__(*group)

        self.orig_image = pygame.transform.scale(load_image('enemy6.png'), (247, 229))
        self.image = self.orig_image.copy()
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(0, WIDTH - self.image.get_width())
        self.rect.y = -self.image.get_height()
        self.mask = pygame.mask.from_surface(self.image)

        # Параметры врага 6
        self.direction = random.choice([1, -1])  # Если +2, то враг движется вправо, если -2, то влево
        self.lives = 7
        self.speed = 1
        self.timer = 0  # таймер необходимый для обозначения времени возгорания при попадении
        self.fired = False  # Здесь храниться значение: подбили только что корабль или нет

    def fire(self, *groups):
        Bullets(*groups, x=self.rect.x + self.image.get_width() // 2 + 30,
                y=self.rect.y + self.rect.height, direction='DOWN')
        Bullets(*groups, x=self.rect.x + self.image.get_width() // 2 - 15 - 5,
                y=self.rect.y + self.rect.height, direction='DOWN')
        Bullets(*groups, x=self.rect.x + self.image.get_width() // 2 - 15 - 55,
                y=self.rect.y + self.rect.height, direction='DOWN')
        Bullets(*groups, x=self.rect.x + self.image.get_width() // 2 - 15 + 95,
                y=self.rect.y + self.rect.height, direction='DOWN')

    def sub_live(self):
        self.lives -= 1
        if self.lives == 0:
            self.destroy()

    def move(self):
        # Проверяем соприкосновение врага 6 со стенками и двигаем его
        if not (0 < self.rect.x and self.rect.x + self.rect.width < WIDTH):
            self.direction *= -1
        self.rect = self.rect.move(self.speed * self.direction, self.speed)

    # Функция делает картинку более светлой на время (так обозначается возгорание при попадании)
    def catch_fire(self):
        if not self.fired:
            self.image.fill((100, 100, 100), special_flags=pygame.BLEND_RGB_ADD)
            self.fired = True
            self.timer = 0

    def destroy(self):
        global score
        score += 1
        self.kill()

    # Возвращает None, если враг 6 мёртв (для перезаписи переменной enemy2)
    def return_alive(self):
        if len(self.groups()) == 0:
            return None
        return self

    # Возвращает True, если враг 6 дошел до нижней границы или пересекся с игроком
    def return_collisions_with_front(self, info_table, player):
        if pygame.sprite.collide_mask(self, info_table) or pygame.sprite.collide_mask(self, player):
            return True
        return False

    def update(self, *args, **kwargs):
        # Проверяем, прошло ли время возгорания, если оно есть (пора ли картинку делать обратно более темной)
        if self.timer == 30:
            self.image = self.orig_image.copy()
            self.fired = False
            self.timer = 0
        # Если корабль горит увеличиваем таймер возгорания
        if self.fired:
            self.timer += 1


class HP(pygame.sprite.Sprite):
    def __init__(self, *group):
        super().__init__(*group)

        self.orig_image = pygame.transform.scale(load_image('hp.png'), (80, 70))
        self.image = self.orig_image.copy()
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(0, WIDTH - self.image.get_width())
        self.rect.y = -self.image.get_height()
        self.mask = pygame.mask.from_surface(self.image)

        self.speed = 2

    def move(self):
        self.rect = self.rect.move(0, self.speed)

    def return_alive(self):
        if len(self.groups()) == 0:
            return None
        return self

    # функция проверяет произошло ли пересечение с игроком или нижней границей поля
    def collision(self, info_table, player):
        if pygame.sprite.collide_mask(self, player):
            self.kill()
            if player.lives < 5:
                player.lives += 1
        elif pygame.sprite.collide_mask(self, info_table):
            self.kill()


class TripleBullets(pygame.sprite.Sprite):
    def __init__(self, *group):
        super().__init__(*group)

        self.orig_image = pygame.transform.scale(load_image('double_bullet.png'), (80, 70))
        self.image = self.orig_image.copy()
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(0, WIDTH - self.image.get_width())
        self.rect.y = -self.image.get_height()
        self.mask = pygame.mask.from_surface(self.image)

        self.speed = 2

    def move(self):
        self.rect = self.rect.move(0, self.speed)

    def return_alive(self):
        if len(self.groups()) == 0:
            return None
        return self

    # функция проверяет произошло ли пересечение с игроком или нижней границей поля
    def collision(self, info_table, player):
        if pygame.sprite.collide_mask(self, player):
            self.kill()
            player.triple_bullets += 15
        elif pygame.sprite.collide_mask(self, info_table):
            self.kill()


class Shield(pygame.sprite.Sprite):
    def __init__(self, *group):
        super().__init__(*group)

        self.orig_image = pygame.transform.scale(load_image('shield.png'), (130, 70))
        self.image = self.orig_image.copy()
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(0, WIDTH - self.image.get_width())
        self.rect.y = -self.image.get_height()
        self.mask = pygame.mask.from_surface(self.image)

        self.speed = 2

    def move(self):
        self.rect = self.rect.move(0, self.speed)

    def return_alive(self):
        if len(self.groups()) == 0:
            return None
        return self

    # функция проверяет произошло ли пересечение с игроком или нижней границей поля
    def collision(self, info_table, player):
        if pygame.sprite.collide_mask(self, player) and player.shields < 3:
            self.kill()
            player.shields += 1
        elif pygame.sprite.collide_mask(self, info_table):
            self.kill()


# Основной цикл игры
def main():
    global score
    fon = pygame.transform.scale(load_image('main_fon.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    clock = pygame.time.Clock()

    # Создаем группы спрайтов
    all_sprites = pygame.sprite.Group()
    player_group = pygame.sprite.Group()
    boss_group = pygame.sprite.Group()
    enemy1_group = pygame.sprite.Group()
    enemy2_group = pygame.sprite.Group()
    enemy3_group = pygame.sprite.Group()
    enemy4_group = pygame.sprite.Group()
    enemy5_group = pygame.sprite.Group()
    enemy6_group = pygame.sprite.Group()
    hp_group = pygame.sprite.Group()
    triple_bullets_group = pygame.sprite.Group()
    shield_group = pygame.sprite.Group()
    info_table_group = pygame.sprite.Group()
    bullets_group = pygame.sprite.Group()

    # Создаем основных персонажей и основной виджет
    info_table = InfoTable(all_sprites, info_table_group)
    player = SpaceShip(all_sprites, player_group)
    boss = None
    enemy1 = Enemy1(all_sprites, enemy1_group)
    enemy2 = None
    enemy3 = None
    enemy4 = None
    enemy5 = None
    enemy6 = None
    hp = None
    triple_bullets = None
    shield = None

    # Событие пополнения запаса пуль
    ADDBULLETSEVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(ADDBULLETSEVENT, 500)

    # Событие движения босса
    MOVEBOSSEVENT = pygame.USEREVENT + 2
    pygame.time.set_timer(MOVEBOSSEVENT, 20)

    # Событие стрельбы босса
    FIREBOSSEVENT = pygame.USEREVENT + 3
    pygame.time.set_timer(FIREBOSSEVENT, 3000)

    # Событие движения врага 1
    MOVEENEMY1EVENT = pygame.USEREVENT + 4
    pygame.time.set_timer(MOVEENEMY1EVENT, 17)

    # Событие стрельбы врага 1
    FIREENEMY1EVENT = pygame.USEREVENT + 5
    pygame.time.set_timer(FIREENEMY1EVENT, random.randint(2400, 2700))

    # Событие движения врага 2
    MOVEENEMY2EVENT = pygame.USEREVENT + 6
    pygame.time.set_timer(MOVEENEMY2EVENT, 17)

    # Событие стрельбы врага 2
    FIREENEMY2EVENT = pygame.USEREVENT + 7
    pygame.time.set_timer(FIREENEMY2EVENT, random.randint(2400, 2700))

    # Событие движения врага 3
    MOVEENEMY3EVENT = pygame.USEREVENT + 8
    pygame.time.set_timer(MOVEENEMY3EVENT, 17)

    # Событие стрельбы врага 3
    FIREENEMY3EVENT = pygame.USEREVENT + 9
    pygame.time.set_timer(FIREENEMY3EVENT, random.randint(2400, 2700))

    # Событие движения врага 4
    MOVEENEMY4EVENT = pygame.USEREVENT + 10
    pygame.time.set_timer(MOVEENEMY4EVENT, 19)

    # Событие стрельбы врага 4
    FIREENEMY4EVENT = pygame.USEREVENT + 11
    pygame.time.set_timer(FIREENEMY4EVENT, 2800)

    # Событие движения врага 5
    MOVEENEMY5EVENT = pygame.USEREVENT + 10
    pygame.time.set_timer(MOVEENEMY5EVENT, 18)

    # Событие стрельбы врага 5
    FIREENEMY5EVENT = pygame.USEREVENT + 11
    pygame.time.set_timer(FIREENEMY5EVENT, 2650)

    # Событие движения хп
    MOVEHPEVENT = pygame.USEREVENT + 12
    pygame.time.set_timer(MOVEHPEVENT, 20)

    # Событие движения тройного выстрела
    MOVETBEVENT = pygame.USEREVENT + 13
    pygame.time.set_timer(MOVETBEVENT, 20)

    # Событие движения щита
    MOVESHIELDEVENT = pygame.USEREVENT + 14
    pygame.time.set_timer(MOVESHIELDEVENT, 20)

    # Событие движения врага 6
    MOVEENEMY6EVENT = pygame.USEREVENT + 15
    pygame.time.set_timer(MOVEENEMY6EVENT, 20)

    # Событие стрельбы врага 6
    FIREENEMY6EVENT = pygame.USEREVENT + 16
    pygame.time.set_timer(FIREENEMY6EVENT, 2800)

    # Значение: Дошел ли враг до границы (если да, то игра кончается)
    front_breakthrough = False

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if player.lives <= 0:
                running = False
            if front_breakthrough:
                running = False
            if event.type == ADDBULLETSEVENT:
                player.add_bullet()
            if boss and event.type == MOVEBOSSEVENT:
                boss.move()
            if boss and event.type == FIREBOSSEVENT:
                boss.fire(all_sprites, bullets_group)
            if enemy1 and event.type == MOVEENEMY1EVENT:
                enemy1.move()
            if enemy1 and event.type == FIREENEMY1EVENT:
                enemy1.fire(all_sprites, bullets_group)
            if enemy2 and event.type == MOVEENEMY2EVENT:
                enemy2.move()
            if enemy2 and event.type == FIREENEMY2EVENT:
                enemy2.fire(all_sprites, bullets_group)
            if enemy3 and event.type == MOVEENEMY3EVENT:
                enemy3.move()
            if enemy3 and event.type == FIREENEMY3EVENT:
                enemy3.fire(all_sprites, bullets_group)
            if enemy4 and event.type == MOVEENEMY4EVENT:
                enemy4.move()
            if enemy4 and event.type == FIREENEMY4EVENT:
                enemy4.fire(all_sprites, bullets_group)
            if enemy5 and event.type == MOVEENEMY5EVENT:
                enemy5.move()
            if enemy5 and event.type == FIREENEMY5EVENT:
                enemy5.fire(all_sprites, bullets_group)
            if hp and event.type == MOVEHPEVENT:
                hp.move()
            if triple_bullets and event.type == MOVETBEVENT:
                triple_bullets.move()
            if shield and event.type == MOVESHIELDEVENT:
                shield.move()
            if enemy6 and event.type == MOVEENEMY6EVENT:
                enemy6.move()
            if enemy6 and event.type == FIREENEMY6EVENT:
                enemy6.fire(all_sprites, bullets_group)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                player.fire(all_sprites, bullets_group)

        screen.blit(fon, (0, 0))
        all_sprites.draw(screen)

        # обновления всех спрайтов (выполняется для каждой группы отдельно из-за особенностей):
        player_group.update()
        boss_group.update()
        enemy1_group.update()
        enemy2_group.update()
        enemy3_group.update()
        enemy4_group.update()
        enemy5_group.update()
        enemy6_group.update()
        hp_group.update()
        triple_bullets_group.update()
        shield_group.update()

        # Проверяем есть ли в игре босс:
        if boss:
            boss = boss.return_alive()
        elif score % 30 == 0 and score != 0:
            boss = Boss(all_sprites, boss_group)

        if boss and not front_breakthrough:
            # Проверяем дошел ли босс до нижней границы или пересекся ли с игроком
            front_breakthrough = boss.return_collisions_with_front(info_table, player)

        # Проверяем есть ли в игре враг 1
        if enemy1:
            enemy1 = enemy1.return_alive()
        else:
            enemy1 = Enemy1(all_sprites, enemy1_group)

        if enemy1 and not front_breakthrough:
            # Проверяем дошел ли босс до нижней границы или пересекся ли с игроком
            front_breakthrough = enemy1.return_collisions_with_front(info_table, player)

        # Проверяем есть ли в игре враг 2
        if enemy2:
            enemy2 = enemy2.return_alive()
        elif score % 2 == 0 and score != 0:
            enemy2 = Enemy5(all_sprites, enemy2_group)

        if enemy2 and not front_breakthrough:
            # Проверяем дошел ли враг 3 до нижней границы или пересекся ли с игроком
            front_breakthrough = enemy2.return_collisions_with_front(info_table, player)

        # Проверяем есть ли в игре враг 3
        if enemy3:
            enemy3 = enemy3.return_alive()
        elif score % 4 == 0 and score != 0:
            enemy3 = Enemy4(all_sprites, enemy3_group)

        if enemy3 and not front_breakthrough:
            # Проверяем дошел ли враг 3 до нижней границы или пересекся ли с игроком
            front_breakthrough = enemy3.return_collisions_with_front(info_table, player)

        # Проверяем есть ли в игре враг 4
        if enemy4:
            enemy4 = enemy4.return_alive()
        elif score % 12 == 0 and score != 0:
            enemy4 = Enemy2(all_sprites, enemy4_group)

        if enemy4 and not front_breakthrough:
            # Проверяем дошел ли враг 4 до нижней границы или пересекся ли с игроком
            front_breakthrough = enemy4.return_collisions_with_front(info_table, player)

        # Проверяем есть ли в игре враг 5
        if enemy5:
            enemy5 = enemy5.return_alive()
        elif score % 7 == 0 and score != 0:
            enemy5 = Enemy3(all_sprites, enemy5_group)

        if enemy5 and not front_breakthrough:
            # Проверяем дошел ли враг 5 до нижней границы или пересекся ли с игроком
            front_breakthrough = enemy5.return_collisions_with_front(info_table, player)

        # Проверяем есть ли в игре хп
        if hp:
            hp = hp.return_alive()
        elif score % 10 == 0 and score != 0:
            hp = HP(all_sprites, hp_group)

        if hp and not front_breakthrough:
            hp.collision(info_table, player)

        if triple_bullets:
            triple_bullets = triple_bullets.return_alive()
        elif score % 12 == 0 and score != 0:
            triple_bullets = TripleBullets(all_sprites, triple_bullets_group)

        if triple_bullets and not front_breakthrough:
            triple_bullets.collision(info_table, player)

        if shield:
            shield = shield.return_alive()
        elif score % 8 == 0 and score != 0:
            shield = Shield(all_sprites, shield_group)

        if shield and not front_breakthrough:
            shield.collision(info_table, player)

        if enemy6:
            enemy6 = enemy6.return_alive()
        elif score % 15 == 0 and score != 0 and score % 30 != 0:
            enemy6 = Enemy6(all_sprites, enemy6_group)

        if enemy6 and not front_breakthrough:
            front_breakthrough = enemy6.return_collisions_with_front(info_table, player)

        bullets_group.update(player, boss, enemy1, enemy2, enemy3, enemy4, enemy5, enemy6)
        info_table_group.update(player.lives, player.bullets, player.shields)

        pygame.display.flip()
        clock.tick(FPS)


# Экран концовки игры
def game_over():
    # Создаём текст и кнопку выхода
    font1 = pygame.font.Font(None, 200)
    font2 = pygame.font.Font(None, 100)
    font3 = pygame.font.Font(None, 70)
    text1 = font1.render("GAME OVER", True, (255, 0, 0))
    text2 = font2.render(f"You kills - {score}", True, (255, 0, 0))
    text3 = font3.render("Exit", True, (0, 0, 255))
    button = pygame.transform.scale(load_image('fon_for_buttons.png'), (200, 70))
    button.blit(text3, (button.get_width() // 2 - text3.get_width() // 2,
                        button.get_height() // 2 - text3.get_height() // 2))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            # Обработчик нажатия на кнопку выхода
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                x_button = WIDTH // 2 - button.get_width() // 2
                y_button = HEIGHT // 2 + text2.get_height()
                if x_button < x < x_button + button.get_width() and y_button < y < y_button + button.get_height():
                    running = False

            # Рисуем виджеты
            screen.blit(text1, (WIDTH // 2 - text1.get_width() // 2, HEIGHT // 2 - text1.get_height()))
            screen.blit(text2, (WIDTH // 2 - text2.get_width() // 2, HEIGHT // 2))
            screen.blit(button, (WIDTH // 2 - button.get_width() // 2, HEIGHT // 2 + text2.get_height()))
            pygame.display.flip()


# Экран меню игры
def start_screen():
    fon = pygame.transform.scale(load_image('start_fon.png'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))

    # Создаем кнопку начала игры
    button = pygame.transform.scale(load_image("fon_for_buttons.png"), (200, 70))
    font = pygame.font.Font(None, 70)
    text = font.render("Play", True, (0, 0, 255))
    button.blit(text, (button.get_width() // 2 - text.get_width() // 2,
                       button.get_height() // 2 - text.get_height() // 2))

    # Создаем текст инструкции к игре
    instruction1 = font.render("Fire - space", True, (0, 255, 0))
    instruction2 = font.render("Moving - left and right arrows", True, (0, 255, 0))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            # Обработчик нажатия на кнопку
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                x_button, y_button = WIDTH // 2 - button.get_width() // 2, HEIGHT // 2
                if x_button < x < x_button + button.get_width() and y_button < y < y_button + button.get_height():
                    running = False

        # Рисуем виджеты
        screen.blit(fon, (0, 0))
        screen.blit(instruction1, (WIDTH // 2 - instruction1.get_width() // 2, HEIGHT // 3))
        screen.blit(instruction2, (WIDTH // 2 - instruction2.get_width() // 2,
                                   HEIGHT // 3 + instruction1.get_height()))
        screen.blit(button, (WIDTH // 2 - button.get_width() // 2, HEIGHT // 2))
        pygame.display.flip()


if __name__ == '__main__':
    pygame.init()
    size = WIDTH, HEIGHT = 1000, 750
    screen = pygame.display.set_mode(size)
    FPS = 100

    while True:
        start_screen()
        score = 0  # переменная отвечает за общее число убитых
        main()
        game_over()
