import pygame
import sys

# Inicialização
pygame.init()

# Tela (Paisagem)
WIDTH, HEIGHT = 1000, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Carro - Ponto A até Ponto B")

clock = pygame.time.Clock()

# Cores
GREEN = (40, 150, 40)
GRAY = (70, 70, 70)
WHITE = (255, 255, 255)
YELLOW = (255, 220, 0)
RED = (220, 40, 40)
BLUE = (30, 144, 255)
BLACK = (0, 0, 0)

# Fonte
font = pygame.font.SysFont(None, 36)

# Pista
ROAD_Y = HEIGHT // 2 - 80
ROAD_HEIGHT = 160

# Carro
car_w = 90
car_h = 50

start_x = 80
end_x = WIDTH - 170

car_x = start_x
car_y = HEIGHT // 2 - car_h // 2

speed = 4

running = True

while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Movimento do carro
    if car_x < end_x:
        car_x += speed

    # Fundo
    screen.fill(GREEN)

    # Pista
    pygame.draw.rect(screen, GRAY, (0, ROAD_Y, WIDTH, ROAD_HEIGHT))

    # Bordas da pista
    pygame.draw.line(screen, WHITE, (0, ROAD_Y), (WIDTH, ROAD_Y), 3)
    pygame.draw.line(screen, WHITE, (0, ROAD_Y + ROAD_HEIGHT), (WIDTH, ROAD_Y + ROAD_HEIGHT), 3)

    # Faixa central
    for x in range(0, WIDTH, 70):
        pygame.draw.rect(screen, WHITE, (x, HEIGHT // 2 - 5, 40, 10))

    # Ponto A
    pygame.draw.circle(screen, RED, (start_x + 20, HEIGHT // 2), 14)
    screen.blit(font.render("A", True, BLACK), (start_x + 10, HEIGHT // 2 + 25))

    # Ponto B
    pygame.draw.circle(screen, YELLOW, (end_x + 70, HEIGHT // 2), 14)
    screen.blit(font.render("B", True, BLACK), (end_x + 60, HEIGHT // 2 + 25))

    # Carro
    pygame.draw.rect(screen, BLUE, (car_x, car_y, car_w, car_h), border_radius=10)

    # Vidros
    pygame.draw.rect(screen, (180, 220, 255), (car_x + 20, car_y + 8, 50, 18), border_radius=4)

    # Rodas
    pygame.draw.circle(screen, BLACK, (car_x + 18, car_y + 5), 8)
    pygame.draw.circle(screen, BLACK, (car_x + 72, car_y + 5), 8)
    pygame.draw.circle(screen, BLACK, (car_x + 18, car_y + 45), 8)
    pygame.draw.circle(screen, BLACK, (car_x + 72, car_y + 45), 8)

    pygame.display.flip()

pygame.quit()
sys.exit()