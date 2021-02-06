import sys
import pygame
import os
import random
import subprocess

FPS, NEWENEMYSPAWN, fst_spawn, not_paused, coins, enemies_count, killed, score = 50, 30, 2000, True, 0, 0, 0, 0
MiniG_rate, EnemyG_rate, MetalM_rate = 1, 5, 15
WEAPONS_LIST = ['Green laser gun', 'Purple laser gun', 'Plasma gun']


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    image = pygame.image.load(fullname).convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def info_print():
    global score, killed, coins

    font = pygame.font.Font(None, 30)
    text_coord = 2
    pygame.draw.rect(screen, (100, 100, 100), (0, 0, 200, 100), 3)
    pygame.draw.rect(screen, (150, 150, 150), (3, 3, 194, 94), 3)
    pygame.draw.rect(screen, (250, 250, 250), (5, 5, 190, 90))
    text = [f'Счёт: {score}',
            f'Убито: {killed}',
            f'Монеты: {coins}']
    for line in text:
        string_rendered = font.render(line, 1, (50, 50, 50))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)


class Board:

    def __init__(self, screen, width, height):
        self.width = width
        self.height = height
        self.board = [[0] * width for _ in range(height)]
        self.left = 0
        self.top = 0
        self.cell_size = 70
        self.screen = screen

    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def render(self):
        tp, pp = [[0, 140], [17, 105], [35, 140]], [[17, 105], [35, 140], [52, 105]]
        for y in range(self.height):
            for x in range(self.width):
                if y >= 2:
                    pygame.draw.rect(self.screen, (100, 100, 100), (
                        x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size),
                                     1)
                    pygame.draw.rect(self.screen, (150, 150, 150), (
                        x * self.cell_size + 1, y * self.cell_size + 1, self.cell_size - 2,
                        self.cell_size - 2), 2)
                    pygame.draw.rect(self.screen, (250, 250, 250), (
                        x * self.cell_size + 3, y * self.cell_size + 3, self.cell_size - 4,
                        self.cell_size - 4))
        for i in range(self.width * 2 - 1):
            pygame.draw.polygon(screen, (0, 230, 200), pp)
            pp[0][1] += 2
            pp[0][0] += 4
            pp[1][1] -= 3
            pp[2][1] += 2
            pp[2][0] -= 4
            pygame.draw.polygon(screen, (0, 125, 200), pp)
            pp[0][1] += 4
            pp[0][0] += 6
            pp[1][1] -= 7
            pp[2][1] += 4
            pp[2][0] -= 6
            pygame.draw.polygon(screen, (0, 230, 200), pp)
            pp[0][1] -= 6
            pp[0][0] -= 10
            pp[1][1] += 10
            pp[2][1] -= 6
            pp[2][0] += 10
            for point in pp:
                point[0] += 35
        for i in range(self.width * 2):
            pygame.draw.polygon(screen, (100, 100, 100), tp)
            tp[0][1] -= 2
            tp[0][0] += 4
            tp[1][1] += 4
            tp[2][1] -= 2
            tp[2][0] -= 4
            pygame.draw.polygon(screen, (150, 150, 150), tp)
            tp[0][1] -= 2
            tp[0][0] += 4
            tp[1][1] += 4
            tp[2][1] -= 2
            tp[2][0] -= 4
            pygame.draw.polygon(screen, (250, 250, 250), tp)
            tp[0][1] += 4
            tp[0][0] -= 8
            tp[1][1] -= 8
            tp[2][1] += 4
            tp[2][0] += 8
            for point in tp:
                point[0] += 35


class Bullet(pygame.sprite.Sprite):

    def __init__(self, enemy_sprites, x, damage, kind):
        super().__init__(bullet_sprites)
        self.damage = damage
        if kind == 'Green laser gun':
            self.image = load_image("green.png", -1)
        elif kind == 'Purple laser gun':
            self.image = load_image("purple.png", -1)
        elif kind == 'Plasma gun':
            self.image = pygame.transform.scale(load_image("plasma.png", -1), (25, 25))
        self.rect = self.image.get_rect()
        self.coords = self.rect.x, self.rect.y = x + 30, 665
        self.mask = pygame.mask.from_surface(self.image)
        self.fly(enemy_sprites)

    def fly(self, enemy_sprites):
        if self.rect.y >= 140:
            self.rect.y -= 1
            for enemy in enemy_sprites:
                if pygame.sprite.collide_mask(enemy, self):
                    self.hit(enemy)
        else:
            self.kill()

    def hit(self, enemy):
        enemy.hp -= self.damage
        self.kill()


class Weapon:

    def __init__(self, player, kind):
        self.kind = kind
        self.ability = None
        self.player = player
        if self.kind == 'Green laser gun':
            self.damage = 2
            self.price = 0
        elif self.kind == 'Purple laser gun':
            self.damage = 4
            self.price = 50
        elif self.kind == 'Plasma gun':
            self.damage = 8
            self.price = 150
            self.ability = 'Rage'

    def shoot(self, enemy_sprites):
        bullet = Bullet(enemy_sprites, self.player.rect.x, self.damage, self.kind)


class Player(pygame.sprite.Sprite):

    def __init__(self, group):
        super().__init__(group)
        self.weapon = Weapon(self, 'Green laser gun')
        self.image = load_image("player.jpg", -1)
        self.rect = self.image.get_rect()
        self.coords = self.rect.x, self.rect.y = 75, 635
        self.mask = pygame.mask.from_surface(self.image)

    def shoot(self, enemy_sprites):
        self.weapon.shoot(enemy_sprites)

    def move(self, side):
        x = self.rect.x
        if x < 630 and side == 'right':
            x += 70
        if x > 35 and side == 'left':
            x -= 70
        self.rect.x = x


class Enemy(pygame.sprite.Sprite):
    global enemies_count, MiniG_rate, EnemyG_rate, MetalM_rate

    def __init__(self, group):
        super().__init__(group)
        if enemies_count >= 30 and enemies_count % MetalM_rate == 0:
            self.type = 'MM'
            self.hp = 24
            self.image = pygame.transform.scale(load_image("Metal_Man.png", -1), (120, 140))
            self.rect = self.image.get_rect()
            self.coords = self.rect.x, self.rect.y = random.randrange(10, 560, 70), 140
            self.mask = pygame.mask.from_surface(self.image)
        elif enemies_count >= 15 and enemies_count % EnemyG_rate == 0:
            self.type = 'EG'
            self.hp = 6
            self.image = pygame.transform.scale(load_image('Enemy_glider.png', -1), (70, 70))
            self.rect = self.image.get_rect()
            self.coords = self.rect.x, self.rect.y = random.randrange(0, 700, 70), 140
            self.mask = pygame.mask.from_surface(self.image)
        else:
            self.type = 'MG'
            self.hp = 4
            self.image = pygame.transform.scale(load_image('Mini_glider.png', -1), (70, 70))
            self.rect = self.image.get_rect()
            self.coords = self.rect.x, self.rect.y = random.randrange(0, 700, 70), 140
            self.mask = pygame.mask.from_surface(self.image)

    def death_check(self):
        global killed, score, coins, FPS

        if self.hp <= 0:
            killed += 1
            if self.type == 'MM':
                score += 30
                coins += 15
                FPS += 10
            elif self.type == 'EG':
                score += 15
                coins += 5
            elif self.type == 'MG':
                score += 10
                coins += 2
            self.kill()

    def move(self):
        self.rect.y += 1


def game_over():
    global FPS, not_paused, score, killed, coins

    def text_print():
        game_over = '      GAME OVER'
        intro_text = ["",
                      "Нажми клавишу A",
                      "чтобы сыграть еще раз",
                      '',
                      'Нажми на кнопку "Esc", ',
                      'чтобы выйти из игры',
                      f'Счёт: {score}',
                      f'Убито: {killed}',
                      f'Монеты: {coins}']

        fon = pygame.transform.scale(load_image('fon.jpg'), (width, height))
        screen.blit(fon, (0, 0))
        font = pygame.font.Font(None, 50)
        text_coord = 40
        string_rendered = font.render(game_over, 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)
        font = pygame.font.Font(None, 30)
        for line in intro_text:
            string_rendered = font.render(line, 1, pygame.Color('white'))
            intro_rect = string_rendered.get_rect()
            text_coord += 10
            intro_rect.top = text_coord
            intro_rect.x = 10
            text_coord += intro_rect.height
            intro_rect.x += 10
            screen.blit(string_rendered, intro_rect)

    FPS = 30
    pygame.mouse.set_visible(True)
    text_print()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        terminate()
                    if event.key == 97:
                        pygame.quit()
                        subprocess.call("python" + " проект.py", shell=True)
        if not_paused:
            pygame.display.flip()
            clock.tick(FPS)
    terminate()


def terminate():
    pygame.quit()
    sys.exit()


def start_screen(screen, width, height):
    global FPS, not_paused

    def text_print():
        intro_text = ["                             SPACE SOLDIER", "",
                      " Нажми любую клавишу,",
                      "  чтобы начать игру",
                      ' Нажимай на кнопки стрелок, чтобы перемещать персонажа',
                      ' Не дай врагу пролететь мимо тебя!',
                      ' Нажми на кнопку "Esc", ',
                      '  чтобы открыть меню паузы',
                      '  или попасть в магазин']

        fon = pygame.transform.scale(load_image('fon.jpg'), (width, height))
        font = pygame.font.Font(None, 30)
        text_coord = 50
        screen.blit(fon, (0, 0))
        for line in intro_text:
            string_rendered = font.render(line, 1, pygame.Color('black'))
            intro_rect = string_rendered.get_rect()
            text_coord += 10
            intro_rect.top = text_coord
            intro_rect.x = 10
            text_coord += intro_rect.height
            screen.blit(string_rendered, intro_rect)

    pygame.mouse.set_visible(True)
    text_print()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pause_menu(screen, width, height)
                        text_print()
                    else:
                        pygame.mouse.set_visible(False)
                        return
        if not_paused:
            pygame.display.flip()
            clock.tick(FPS)
    terminate()


def pause_menu(screen, width, height):
    global FPS, not_paused

    def text_print():
        intro_text = ["Нажми на кнопку 'S',",
                      "чтобы открыть магазин",
                      '',
                      "Нажми на кнопку 'C',",
                      "чтобы продолжжить игру",
                      '',
                      "УПРАВЛЕНИЕ",
                      '',
                      'Нажимай на кнопки стрелок, чтобы перемещать персонажа',
                      '',
                      'Не дай врагу пролететь мимо тебя!',
                      '',
                      'Нажми на кнопку "Esc", ',
                      'чтобы закрыть меню паузы']

        fon = pygame.transform.scale(load_image('fon.jpg'), (width, height))
        font = pygame.font.Font(None, 30)
        text_coord = 50
        screen.blit(fon, (0, 0))
        for line in intro_text:
            string_rendered = font.render(line, 1, pygame.Color('black'))
            intro_rect = string_rendered.get_rect()
            text_coord += 10
            intro_rect.top = text_coord
            intro_rect.x = 10
            text_coord += intro_rect.height
            screen.blit(string_rendered, intro_rect)

    pygame.mouse.set_visible(True)
    fon = pygame.transform.scale(load_image('fon.jpg'), (width, height))
    screen.blit(fon, (0, 0))
    text_print()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    not_paused = True
                    pygame.mouse.set_visible(False)
                    return
                if event.key == 115:
                    shop(screen, width, height)
                if event.key == 99:
                    return
        pygame.display.flip()
        clock.tick(FPS)
    terminate()


def shop(screen, width, height):
    global FPS, not_paused, WEAPONS_LIST, coins

    def text_print():
        intro_text = ["       Нажми на кнопку 'U',",
                      "чтобы улучшить свое оружие",
                      'Нажми на кнопку "Esc", ',
                      'чтобы выйти из магазина', '',
                      'Текущее оружие:',
                      f'{player.weapon.kind}',
                      'Наносимый урон:',
                      f'{player.weapon.damage}',
                      'Следующее улучшение:',
                      f'{next_weapon}',
                      'Урон:',
                      f'{next_damage}',
                      'Стоимость:',
                      f'{next_price}',
                      'Ваши монеты:',
                      f'{coins}']

        fon = pygame.transform.scale(load_image('fon.jpg'), (width, height))
        font = pygame.font.Font(None, 30)
        text_coord = 50
        screen.blit(fon, (0, 0))
        for line in intro_text:
            string_rendered = font.render(line, 1, pygame.Color('black'))
            intro_rect = string_rendered.get_rect()
            text_coord += 10
            intro_rect.top = text_coord
            intro_rect.x = 10
            text_coord += intro_rect.height
            screen.blit(string_rendered, intro_rect)

    if player.weapon.kind != 'Plasma gun':
        next_weapon = WEAPONS_LIST[WEAPONS_LIST.index(player.weapon.kind) + 1]
        if next_weapon == 'Purple laser gun':
            next_damage = 4
            next_price = 50
        else:
            next_damage = 6
            next_price = 150
    else:
        next_weapon = 'Вы имеете лучшее оружие'
        next_damage = 'Наносимый урон максимальный'
        next_price = 'Покупать больше нечего'

    pygame.mouse.set_visible(True)
    fon = pygame.transform.scale(load_image('fon.jpg'), (width, height))
    screen.blit(fon, (0, 0))
    text_print()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.mouse.set_visible(False)
                    screen.blit(fon, (0, 0))
                    return
                if event.key == 117 and player.weapon.kind != 'Plasma gun' and coins >= next_price:
                    coins -= next_price
                    player.weapon = Weapon(player, WEAPONS_LIST[WEAPONS_LIST.index(player.weapon.kind) + 1])
        pygame.display.flip()
        clock.tick(FPS)
    terminate()


pygame.init()
size = width, height = 700, 700
screen = pygame.display.set_mode(size)
pygame.display.set_caption('SPACE SOLDIER')
pygame.display.set_icon(load_image("icon.png", -1))
fon1 = pygame.transform.scale(load_image('fon1.png'), (700, 400))
board = Board(screen, 10, 10)
pygame.mouse.set_visible(True)
enemy_sprites = pygame.sprite.Group()
player_sprites = pygame.sprite.Group()
bullet_sprites = pygame.sprite.Group()
player = Player(player_sprites)
enemy_li = [Enemy(enemy_sprites)]
clock = pygame.time.Clock()
start_screen(screen, width, height)
pygame.time.set_timer(NEWENEMYSPAWN, fst_spawn)
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                not_paused = False
                pause_menu(screen, width, height)
            if not_paused:
                if event.key == 275:
                    player.move('right')
                elif event.key == 276:
                    player.move('left')
                if event.key == 115:
                    player.shoot(enemy_sprites)
        if not_paused and event.type == NEWENEMYSPAWN:
            enemy_li.append(Enemy(enemy_sprites))
            enemies_count += 1

    if not_paused:
        screen.blit(fon1, (0, 0))
        board.render()
        player_sprites.draw(screen)
        enemy_sprites.draw(screen)
        bullet_sprites.draw(screen)
        for enemy in enemy_sprites:
            if enemy.type != 'MM':
                lim = 630
            else:
                lim = 560
            if enemy.rect.y <= lim:
                enemy.move()
            else:
                game_over()
            for bullet in bullet_sprites:
                bullet.fly(enemy_sprites)
            enemy.death_check()
        info_print()
        pygame.display.flip()
        clock.tick(FPS)
terminate()
