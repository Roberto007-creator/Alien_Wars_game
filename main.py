import pygame
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

        self.image = pygame.Surface([WIDTH, 50])
        self.rect = pygame.Rect(0, HEIGHT - 50, WIDTH, 50)

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
        self.image.blit(text_kills, (320, 0))

    # у класса особый метод update, требующий определенных аргументов, вызывать только в собственной группе!!!
    def update(self, lives, bullets, kills):
        self.count_lives = lives
        self.count_bullets = bullets
        self.kills = kills
        self.draw_info()


class Bullets(pygame.sprite.Sprite):
    def __init__(self, *group, **kwargs):
        super().__init__(*group)

        self.image = pygame.transform.scale(load_image('bullet.png'), (30, 30))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = kwargs['x'], kwargs['y']
        self.mask = pygame.mask.from_surface(self.image)

        self.direction = kwargs['direction']
        self.speed = 5

    def update(self):
        if self.direction == 'UP':
            self.rect = self.rect.move(0, -self.speed)
        elif self.direction == 'DOWN':
            self.rect = self.rect.move(0, self.speed)


class SpaceShip(pygame.sprite.Sprite):
    def __init__(self, *group):
        super().__init__(*group)

        self.image = pygame.transform.scale(load_image('space_ship.png'), (150, 150))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = WIDTH - WIDTH // 2 - 75, HEIGHT - 200
        self.mask = pygame.mask.from_surface(self.image)

        self.speed = 5
        self.lives = 3
        self.bullets = 5
        self.kills = 0

    def update(self, *args):
        k_left = pygame.key.get_pressed()[pygame.K_LEFT]
        k_right = pygame.key.get_pressed()[pygame.K_RIGHT]

        if k_left and not k_right and 0 < self.rect.x - self.speed:
            self.rect = self.rect.move(-self.speed, 0)
        if k_right and not k_left and self.rect.x + self.speed < WIDTH - self.rect.width:
            self.rect = self.rect.move(self.speed, 0)

    def fire(self, *groups):
        if self.bullets:
            self.bullets -= 1
            Bullets(*groups, x=self.rect.x + 60, y=self.rect.y, direction='UP')

    def add_bullet(self):
        if self.bullets < 5:
            self.bullets += 1


def main():
    fon = pygame.transform.scale(load_image('main_fon.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    clock = pygame.time.Clock()

    all_sprites = pygame.sprite.Group()
    player_group = pygame.sprite.Group()
    info_table_group = pygame.sprite.Group()
    bullets_group = pygame.sprite.Group()

    InfoTable(info_table_group)
    player = SpaceShip(all_sprites, player_group)

    ADDBULLETSEVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(ADDBULLETSEVENT, 1000)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == ADDBULLETSEVENT:
                player.add_bullet()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                player.fire(all_sprites, bullets_group)

        screen.blit(fon, (0, 0))
        all_sprites.draw(screen)
        info_table_group.draw(screen)
        all_sprites.update()
        info_table_group.update(player.lives, player.bullets, player.kills)
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == '__main__':
    pygame.init()
    size = WIDTH, HEIGHT = 800, 750
    screen = pygame.display.set_mode(size)
    FPS = 100

    main()

    terminate()
