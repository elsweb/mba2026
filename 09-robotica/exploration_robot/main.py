import pygame

from config import *
from road import draw_road
from objects import Car,Obstacle

screen=pygame.display.set_mode((WIDTH,HEIGHT))
clock=pygame.time.Clock()

start_x=80
end_x=WIDTH-170

car=Car(
    start_x,
    HEIGHT//2-25
)

obstacles=[

    Obstacle(300,170),

    Obstacle(450,200),

    Obstacle(650,160),

    Obstacle(820,220),

]

running=True

while running:

    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            running=False

    car.update(end_x)

    draw_road(screen,start_x,end_x)

    for obstacle in obstacles:
        obstacle.draw(screen)

    car.draw(screen)

    pygame.display.flip()

pygame.quit()