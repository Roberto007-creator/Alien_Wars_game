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
        self.count_bullets = 5
        self.kills = 0

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
            self.image.blit(bullet, (WIDTH - 150 + 20 * i, 0))

        # рисуем надпись "Kills"
        font = pygame.font.Font(None, 80)
        text_kills = font.render(f"Kills: {self.kills}", True, (0, 255, 0))
        self.image.blit(text_kills, (WIDTH // 2 - text_kills.get_width() // 2, 0))

    # у класса особый метод update, требующий определенных аргументов, вызывать только в собственной группе!!!
    def update(self, lives, bullets):
        global score
        self.count_lives = lives
        self.count_bullets = bullets
        self.kills = score
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

    def update(self, player, boss):
        # Проверяем пересечение с игроком
        if pygame.sprite.collide_mask(self, player):
            self.kill()
            player.sub_live()
        # Проверяем пересечение с боссом, если он существует
        elif boss and pygame.sprite.collide_mask(self, boss):
            self.kill()
            boss.sub_live()
        else:
            # Двигаем пулю
            if self.direction == 'UP':
                self.rect = self.rect.move(0, -self.speed)
            elif self.direction == 'DOWN':
                self.rect = self.rect.move(0, self.speed)


class SpaceShip(pygame.sprite.Sprite):
    def __init__(self, *group):
        super().__init__(*group)

        self.image = pygame.transform.scale(load_image('space_ship.png'), (120, 120))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = WIDTH - WIDTH // 2 - self.image.get_width(), HEIGHT - self.image.get_height() - 50
        self.mask = pygame.mask.from_surface(self.image)

        # Параметры игрока
        self.speed = 5
        self.lives = 3
        self.bullets = 5
        self.kills = 0

    def update(self, *args):
        k_left = pygame.key.get_pressed()[pygame.K_LEFT]
        k_right = pygame.key.get_pressed()[pygame.K_RIGHT]

        # Проверяем нажатие на клавишы лево-право и двигаем игрока
        if k_left and not k_right and 0 < self.rect.x - self.speed:
            self.rect = self.rect.move(-self.speed, 0)
        if k_right and not k_left and self.rect.x + self.speed < WIDTH - self.rect.width:
            self.rect = self.rect.move(self.speed, 0)

    def fire(self, *groups):
        if self.bullets:
            self.bullets -= 1
            Bullets(*groups, x=self.rect.x + self.image.get_width() // 2 - 15, y=self.rect.y - 15, direction='UP')

    def add_bullet(self):
        if self.bullets < 5:
            self.bullets += 1

    def sub_live(self):
        self.lives -= 1


class Boss(pygame.sprite.Sprite):
    def __init__(self, *group):
        super().__init__(*group)

        self.image = pygame.transform.scale(load_image('boss.png'), (450, 200))
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(0, WIDTH - self.image.get_width())
        self.rect.y = -self.image.get_height()
        self.mask = pygame.mask.from_surface(self.image)

        # Параметры босса
        self.direction = random.choice([1, -1]) # Если +1, то босс движется вправо, если -1, то влево
        self.lives = 10
        self.speed = 1

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


# Основной цикл игры
def main():
    fon = pygame.transform.scale(load_image('main_fon.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    clock = pygame.time.Clock()

    # Создаем группы спрайтов
    all_sprites = pygame.sprite.Group()
    player_group = pygame.sprite.Group()
    boss_group = pygame.sprite.Group()
    info_table_group = pygame.sprite.Group()
    bullets_group = pygame.sprite.Group()

    # Создаем основных персонажей и основной виджет
    info_table = InfoTable(all_sprites, info_table_group)
    player = SpaceShip(all_sprites, player_group)
    boss = Boss(all_sprites, boss_group)

    # Событие пополнения запаса пуль
    ADDBULLETSEVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(ADDBULLETSEVENT, 700)

    # Событие движения босса
    MOVEBOSSEVENT = pygame.USEREVENT + 2
    pygame.time.set_timer(MOVEBOSSEVENT, 20)

    # Событие стрельбы босса
    FIREBOSSEVENT = pygame.USEREVENT + 3
    pygame.time.set_timer(FIREBOSSEVENT, 3000)

    # Значение: Дошел ли враг до границы (если да, то игра кончается)
    front_breakthrough = False

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if player.lives == 0:
                running = False
            if front_breakthrough:
                running = False
            if event.type == ADDBULLETSEVENT:
                player.add_bullet()
            if boss and event.type == MOVEBOSSEVENT:
                boss.move()
            if boss and event.type == FIREBOSSEVENT:
                boss.fire(all_sprites, bullets_group)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                player.fire(all_sprites, bullets_group)

        screen.blit(fon, (0, 0))
        all_sprites.draw(screen)

        # обновления всех спрайтов (выполняется для каждой группы отдельно из-за особенностей):
        player_group.update()
        boss_group.update()

        # Проверяем есть ли в игре босс:
        if boss:
            boss = boss.return_alive()
        else:
            boss = Boss(all_sprites, boss_group)

        if boss:
            # Проверяем дошел ли босс до нижней границы или пересекся ли с игроком
            front_breakthrough = boss.return_collisions_with_front(info_table, player)

        bullets_group.update(player, boss)
        info_table_group.update(player.lives, player.bullets)

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
        score = 0 # переменная отвечает за общее число убитых
        main()
        game_over()
