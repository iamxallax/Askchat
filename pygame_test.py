import pygame

pygame.init()

WIDTH, HEIGHT = 160, 100
screen = pygame.display.set_mode((WIDTH, HEIGHT))

background = pygame.transform.scale(pygame.image.load('parchment_paper.jpeg'), (1600, 1000))
button = pygame.image.load('button_blue.svg')
text_box = pygame.transform.scale(pygame.image.load('box.png'), (1600 - 200 - 200, 1000 - 125 - 125))
screen.fill((255, 255, 255))
screen.blit(background, (0, 0))
#screen.blit(button, (0, 0))
screen.blit(text_box, (200, 125))
pygame.display.flip()

running = True
while running:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False
    