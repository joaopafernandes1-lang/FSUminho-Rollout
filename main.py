import pygame
import os
import random
import asyncio

pygame.init()

# Global Constants
SCREEN_HEIGHT = 600
SCREEN_WIDTH = 1100
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Load assets
RUNNING = [pygame.image.load(os.path.join("Assets/Dino.png")),
           pygame.image.load(os.path.join("Assets/Dino2.png"))]
JUMPING = pygame.image.load(os.path.join("Assets/Dinoj.png"))
DUCKING = [pygame.image.load(os.path.join("Assets/Dino.png")),
           pygame.image.load(os.path.join("Assets/Dino.png"))]

SMALL_CACTUS = [pygame.image.load(os.path.join("Assets/cactus.png")),
                pygame.image.load(os.path.join("Assets/cactus2.png")),
                pygame.image.load(os.path.join("Assets/cactus2.png"))]
LARGE_CACTUS = [pygame.image.load(os.path.join("Assets/cactus3.png")),
                pygame.image.load(os.path.join("Assets/cactus3.png")),
                pygame.image.load(os.path.join("Assets/cactus3.png"))]

BIRD = [pygame.image.load(os.path.join("Assets/dragon.png")),
        pygame.image.load(os.path.join("Assets/dragon2.png"))]

CLOUD = pygame.image.load(os.path.join("Assets/Other/Cloud.png"))
BG = pygame.image.load(os.path.join("Assets/Other/Track.png"))


# === Classes (same as your original) ===
class Dinosaur:
    X_POS = 80
    Y_POS = 310
    Y_POS_DUCK = 330
    JUMP_VEL = 8.5

    def __init__(self):
        self.duck_img = DUCKING
        self.run_img = RUNNING
        self.jump_img = JUMPING

        self.dino_duck = False
        self.dino_run = True
        self.dino_jump = False

        self.step_index = 0
        self.jump_vel = self.JUMP_VEL
        self.image = self.run_img[0]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS

    def update(self, userInput):
        if self.dino_duck:
            self.duck()
        if self.dino_run:
            self.run()
        if self.dino_jump:
            self.jump()

        if self.step_index >= 10:
            self.step_index = 0

        if userInput[pygame.K_UP] and not self.dino_jump:
            self.dino_duck = False
            self.dino_run = False
            self.dino_jump = True
        elif userInput[pygame.K_DOWN] and not self.dino_jump:
            self.dino_duck = True
            self.dino_run = False
            self.dino_jump = False
        elif not (self.dino_jump or userInput[pygame.K_DOWN]):
            self.dino_duck = False
            self.dino_run = True
            self.dino_jump = False

    def duck(self):
        self.image = self.duck_img[self.step_index // 5]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS_DUCK
        self.step_index += 1

    def run(self):
        self.image = self.run_img[self.step_index // 5]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS
        self.step_index += 1

    def jump(self):
        self.image = self.jump_img
        if self.dino_jump:
            self.dino_rect.y -= self.jump_vel * 4
            self.jump_vel -= 0.8
        if self.jump_vel < -self.JUMP_VEL:
            self.dino_jump = False
            self.jump_vel = self.JUMP_VEL

    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.dino_rect.x, self.dino_rect.y))


class Cloud:
    def __init__(self):
        self.x = SCREEN_WIDTH + random.randint(800, 1000)
        self.y = random.randint(50, 100)
        self.image = CLOUD
        self.width = self.image.get_width()

    def update(self):
        self.x -= game_speed
        if self.x < -self.width:
            self.x = SCREEN_WIDTH + random.randint(2500, 3000)
            self.y = random.randint(50, 100)

    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.x, self.y))


class Obstacle:
    def __init__(self, image, type):
        self.image = image
        self.type = type
        self.rect = self.image[self.type].get_rect()
        self.rect.x = SCREEN_WIDTH

    def update(self):
        self.rect.x -= game_speed
        if self.rect.x < -self.rect.width:
            obstacles.pop()

    def draw(self, SCREEN):
        SCREEN.blit(self.image[self.type], self.rect)


class SmallCactus(Obstacle):
    def __init__(self, image):
        self.type = random.randint(0, 2)
        super().__init__(image, self.type)
        self.rect.y = 320


class LargeCactus(Obstacle):
    def __init__(self, image):
        self.type = random.randint(0, 2)
        super().__init__(image, self.type)
        self.rect.y = 330


class Bird(Obstacle):
    def __init__(self, image):
        self.type = 0
        super().__init__(image, self.type)
        self.rect.y = 220
        self.index = 0

    def draw(self, SCREEN):
        if self.index >= 9:
            self.index = 0
        SCREEN.blit(self.image[self.index // 5], self.rect)
        self.index += 1


# === Game loop functions ===

async def run_game():
    """Single game session. Returns True if player dies."""
    global game_speed, obstacles, points
    clock = pygame.time.Clock()
    player = Dinosaur()
    cloud = Cloud()
    game_speed = 20
    obstacles = []
    points = 0
    font = pygame.font.Font('freesansbold.ttf', 20)

    def score():
        global points, game_speed
        points += 1
        if points % 100 == 0:
            game_speed += 1
        text = font.render("Points: " + str(points), True, (0, 0, 0))
        SCREEN.blit(text, (1000, 40))

    def background():
        global x_pos_bg
        image_width = BG.get_width()
        SCREEN.blit(BG, (x_pos_bg, 380))
        SCREEN.blit(BG, (image_width + x_pos_bg, 380))
        if x_pos_bg <= -image_width:
            x_pos_bg = 0
        x_pos_bg -= game_speed

    global x_pos_bg
    x_pos_bg = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return True  # Exit game

        SCREEN.fill((255, 255, 255))
        userInput = pygame.key.get_pressed()

        player.update(userInput)
        player.draw(SCREEN)

        if len(obstacles) == 0:
            choice = random.randint(0, 2)
            if choice == 0:
                obstacles.append(SmallCactus(SMALL_CACTUS))
            elif choice == 1:
                obstacles.append(LargeCactus(LARGE_CACTUS))
            else:
                obstacles.append(Bird(BIRD))

        for obstacle in list(obstacles):
            obstacle.update()
            obstacle.draw(SCREEN)
            if player.dino_rect.colliderect(obstacle.rect):
                pygame.time.delay(500)
                return False  # Player died

        cloud.update()
        cloud.draw(SCREEN)

        background()
        score()

        clock.tick(30)
        pygame.display.update()
        await asyncio.sleep(0)


async def show_menu(death_count):
    """Menu screen. Waits for key press to start game."""
    global points
    run = True
    font = pygame.font.Font('freesansbold.ttf', 30)

    while run:
        SCREEN.fill((255, 255, 255))

        if death_count == 0:
            text = font.render("Press any Key to Start", True, (0, 0, 0))
        else:
            text = font.render("Press any Key to Restart", True, (0, 0, 0))
            score_text = font.render(f"Your Score: {points}", True, (0, 0, 0))
            SCREEN.blit(score_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 50))

        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        SCREEN.blit(text, text_rect)
        SCREEN.blit(RUNNING[0], (SCREEN_WIDTH // 2 - 20, SCREEN_HEIGHT // 2 - 140))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            if event.type == pygame.KEYDOWN:
                return True  # Start game
        await asyncio.sleep(0)


# === Top-level loop ===
async def main_loop():
    death_count = 0
    while True:
        # Show menu and wait for key press
        start = await show_menu(death_count)
        if not start:
            break
        # Run the game
        alive = await run_game()
        if not alive:
            death_count += 1


asyncio.run(main_loop())