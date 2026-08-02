import pygame
from config import *

def draw_road(screen,start_x,end_x):

    screen.fill(GREEN)

    pygame.draw.rect(
        screen,
        GRAY,
        (0,ROAD_Y,WIDTH,ROAD_HEIGHT)
    )

    pygame.draw.line(screen,WHITE,(0,ROAD_Y),(WIDTH,ROAD_Y),3)
    pygame.draw.line(screen,WHITE,(0,ROAD_Y+ROAD_HEIGHT),(WIDTH,ROAD_Y+ROAD_HEIGHT),3)

    for x in range(0,WIDTH,70):
        pygame.draw.rect(screen,WHITE,(x,HEIGHT//2-5,40,10))

    pygame.draw.circle(screen,RED,(start_x+20,HEIGHT//2),14)
    screen.blit(FONT.render("A",True,BLACK),(start_x+10,HEIGHT//2+25))

    pygame.draw.circle(screen,YELLOW,(end_x+70,HEIGHT//2),14)
    screen.blit(FONT.render("B",True,BLACK),(end_x+60,HEIGHT//2+25))