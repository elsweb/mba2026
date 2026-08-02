import pygame
from config import *

class Car:

    def __init__(self,x,y):
        self.x=x
        self.y=y
        self.w=90
        self.h=50
        self.speed=4

    def update(self,end_x):
        if self.x<end_x:
            self.x+=self.speed

    def draw(self,screen):

        pygame.draw.rect(screen,BLUE,(self.x,self.y,self.w,self.h),border_radius=10)

        pygame.draw.rect(
            screen,
            (180,220,255),
            (self.x+20,self.y+8,50,18),
            border_radius=4
        )

        pygame.draw.circle(screen,BLACK,(self.x+18,self.y+5),8)
        pygame.draw.circle(screen,BLACK,(self.x+72,self.y+5),8)
        pygame.draw.circle(screen,BLACK,(self.x+18,self.y+45),8)
        pygame.draw.circle(screen,BLACK,(self.x+72,self.y+45),8)

    @property
    def rect(self):
        return pygame.Rect(self.x,self.y,self.w,self.h)


class Obstacle:

    def __init__(self,x,y,w=40,h=40,color=(255,100,0)):
        self.rect=pygame.Rect(x,y,w,h)
        self.color=color

    def draw(self,screen):
        pygame.draw.rect(screen,self.color,self.rect,border_radius=5)