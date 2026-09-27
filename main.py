# ---- Бібліотеки -----
import pygame
import random

# ---- Змінні, потрібні для подальшої роботи коду -----
game_part = "menu"

shoot_delay = 370
last_shot = 0

fade_alpha = 0
fade_direction = 1
fading = False
next_state = None
fade_speed = 5

columns = [i * 80 for i in range(8)]
free_columns = columns.copy()

explosions = []
bullets = []
meteorites = []

YELLOW = (200, 200, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

FPS = 50

HEIGHT = 800
WIDTH = 640

# ---- Основні налаштування pygame та додавання текстур -----
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))

image_space_menu = pygame.image.load("space_menu.png").convert_alpha()
image_space_game = pygame.image.load("space_game.jpg")
image_space_game_over = pygame.image.load("space_gameover.jpg")
image_meteorite = pygame.image.load("meteorite.png")
image_spaceship = pygame.image.load("spaceship(1).png")
image_explosion = pygame.image.load("explosion(1).png")
image_bullet = pygame.image.load("bullet(1).png")

# ---- Батьківський для всіх інших клас -----
class Sprite:
    def __init__(self, x, y, image):
        self.image = image
        self.rect = pygame.Rect(x, y, self.image.get_width(),
                                self.image.get_height())

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def collide(self, other):
        return self.rect.colliderect(other.rect)

# ---- Класи, що відповідають за ігрові об'єкти: метеорити, постріли, вибухи й тощо -----
class Spaceship(Sprite):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)
        self.speed = 5

    def update(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH

class Bullet(Sprite):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)
        self.speed = 8

    def update(self):
        self.rect.y -= self.speed

    def off_screen(self):
        return self.rect.bottom < 0

class Explosion(Sprite):
    def __init__(self, x, y, image):
        self.x = x
        self.y = y
        self.image = image
        self.rect = self.image.get_rect(center=(x, y))
        self.timer = 5

        self.timer = 25
        self.max_timer = 25

    def update(self):
        self.timer -= 1

    def draw(self, screen):
        progress = 1 - (self.timer / self.max_timer)
        scale = 0.5 + progress * 1.5

        size = int(self.image.get_width() * scale)
        image = pygame.transform.scale(self.image, (size, size))

        alpha = int(255 * (self.timer / self.max_timer))
        image.set_alpha(alpha)

        rect = image.get_rect(center=(self.x, self.y))
        screen.blit(image, rect)

    def is_finished(self):
        return self.timer <= 0

class Meteorite(Sprite):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)

        self.base_image = image
        self.angle = 0
        self.rotation_speed = random.uniform(-2, 2)

        self.speed = random.uniform(0.45, 0.8)
        self.y = float(self.rect.y)
        self.x = float(self.rect.x)

        self.column = x

    def update(self):
        self.y += self.speed
        self.rect.y = int(self.y)

        self.angle += self.rotation_speed
        if self.angle > 360:
            self.angle -= 360
        if self.angle < 0:
            self.angle += 360

        old_center = self.rect.center
        self.image = pygame.transform.rotate(self.base_image, self.angle)
        self.rect = self.image.get_rect(center=old_center)

        if self.rect.top > HEIGHT:
            self.y = -50
            self.rect.y = int(self.y)
            self.rect.x = random.randint(0, WIDTH - self.rect.width)

# ---- Створення об'єкта гравця та решта налаштувань pygame -----
player = Spaceship(200, 600, image_spaceship)
player.rect = player.rect.inflate(-20, -20)

for i in range(8):
    x = free_columns.pop(0)
    m = Meteorite(x, 0, image_meteorite)
    m.column = x
    meteorites.append(m)

clock = pygame.time.Clock()
running = True

# ---- Ігровий цикл -----
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # ---- Вихід з меню та початок гри -----
        if game_part == "menu":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    fading = True
                    next_state = "game"
                    fade_direction = 1
                    fade_alpha = 0

        # ---- Дії при програші -----
        if game_part == "game_over":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    fading = True
                    next_state = "menu"
                    fade_direction = 1
                    fade_alpha = 0

                    free_columns = columns.copy()

                    meteorites.clear()
                    for i in range(8):
                        x = free_columns.pop(0)
                        m = Meteorite(x, 0, image_meteorite)
                        m.column = x
                        meteorites.append(m)

                    bullets.clear()
                    explosions.clear()

                    player.rect.x = 200
                    player.rect.y = 600

                    last_shot = 0

    # ---- Виведення на екран тексту -----
    if game_part == "menu":
        screen.blit(image_space_menu, (0, 0))
        font = pygame.font.SysFont(None, 50)
        text = font.render("Press 'F' to play", True, WHITE)
        screen.blit(text, (190, 450))

    elif game_part == "game_over":
        screen.blit(image_space_game_over, (0, 0))
        font = pygame.font.SysFont(None, 50)
        text = font.render("Press 'R' to return to menu", True, WHITE)
        screen.blit(text, (120, 450))

    # ---- Частина циклу, що відповідає за дії безпосередньо під час основної гри -----
    if game_part == "game":
        screen.blit(image_space_game, (0, 0))

        player.update()

        for bullet in bullets:
            bullet.update()

        for meteor in meteorites:
            meteor.update()

        for exp in explosions:
            exp.update()

        # ---- Автоматизація стрільби -----
        current_time = pygame.time.get_ticks()

        if current_time - last_shot > shoot_delay:
            bullets.append(Bullet(player.rect.centerx - image_bullet.get_width() // 2, player.rect.top, image_bullet))
            last_shot = current_time

        # ---- Перевірка зіткнень та дії в результаті зіткнення -----
        for bullet in bullets:
            for meteor in meteorites:
                if bullet.collide(meteor):

                    explosions.append(Explosion(meteor.rect.centerx, meteor.rect.centery, image_explosion))

                    bullet.rect.y = -100

                    free_columns.append(meteor.column)
                    new_x = random.choice(free_columns)
                    free_columns.remove(new_x)

                    meteor.column = new_x
                    meteor.rect.x = new_x
                    meteor.y = -50
                    meteor.rect.y = int(meteor.y)

        # ---- Умова програшу (зіткнення з метеоритом) -----
        for meteor in meteorites:
            if player.collide(meteor):
                fading = True
                next_state = "game_over"
                fade_direction = 1
                fade_alpha = 0

        if game_part == "game_over":
            screen.blit(image_space_game_over, (0, 0))

        # ---- Відображення деяких текстур -----
        explosions = [e for e in explosions if not e.is_finished()]
        bullets = [b for b in bullets if not b.off_screen()]

        screen.blit(image_space_game, (0, 0))

        player.draw(screen)

        for bullet in bullets:
            bullet.draw(screen)

        for meteor in meteorites:
            meteor.draw(screen)

        for exp in explosions:
            exp.draw(screen)

    # ---- Затемнення екрана при програші та виході з меню -----
    if fading:
        fade_alpha += fade_speed * fade_direction

        if fade_alpha >= 255:
            fade_alpha = 255
            game_part = next_state
            fade_direction = -1

        elif fade_alpha <= 0:
            fade_alpha = 0
            fading = False

        fade_surface = pygame.Surface((WIDTH, HEIGHT))
        fade_surface.fill((0, 0, 0))
        fade_surface.set_alpha(fade_alpha)

        screen.blit(fade_surface, (0, 0))

    # ---- оновлення екрана (FPS) -----
    pygame.display.flip()
    clock.tick(60)

(pygame

 .quit())