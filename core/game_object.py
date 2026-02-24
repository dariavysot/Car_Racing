# GameObject is a base class for all drawable/movable entities
# PlayerCar and Obstacle should inherit from it

import pygame as pg

class GameObject:
    def __init__(self, image, x, y):
        self.image = image
        self.rect = image.get_rect(center=(x, y))

    def update(self, *args, **kwargs):
        """Overridden in subclasses"""
        pass

    def draw(self, screen):
        screen.blit(self.image, self.rect)
