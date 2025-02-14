import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 400, 400
DICE_SIZE = 100
FPS = 30

# Colors
WHITE = (255, 255, 255)

# Dice faces
dice_faces = [pygame.image.load(f'dice{str(i)}.png') for i in range(1, 7)]

# Initialize screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rolling 3D6 Dice")

def main():
    clock = pygame.time.Clock()
    rolling = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and not rolling:
                rolling = True
                roll_dice()

        screen.fill(WHITE)

        if rolling:
            display_roll_animation()

        pygame.display.update()
        clock.tick(FPS)

def roll_dice():
    global result
    result = random.randint(1, 6)

def display_roll_animation():
    x, y = WIDTH // 2 - DICE_SIZE // 2, HEIGHT // 2 - DICE_SIZE // 2
    screen.blit(dice_faces[result - 1], (x, y))

if __name__ == "__main__":
    main()
