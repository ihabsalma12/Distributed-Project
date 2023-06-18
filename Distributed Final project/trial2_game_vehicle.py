import pygame
import uuid

pygame.init()

GREEN_CAR = pygame.image.load('Vertical Cars/green-car.png')
GREY_CAR = pygame.image.load('Vertical Cars/grey-car.png')
PURPLE_CAR = pygame.image.load('Vertical Cars/purple-car.png')
RED_CAR = pygame.image.load('Vertical Cars/red-car.png')
CAR_NAMES = ['green', 'grey', 'purple', 'red']
CARS = {'green': GREEN_CAR, 
          'grey': GREY_CAR, 
          'purple': PURPLE_CAR, 
          'red': RED_CAR}


class Coin(pygame.sprite.Sprite):
    
    def __init__(self, image, x, y):
        pygame.sprite.Sprite.__init__(self)
        
        # scale the image down so it's not wider than the lane
        image_scale = 80 / image.get_rect().width
        new_width = image.get_rect().width * image_scale
        new_height = image.get_rect().height * image_scale
        self.image = pygame.transform.scale(image, (new_width, new_height))
        
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.id = str(uuid.uuid4())



class Vehicle(pygame.sprite.Sprite):
    
    def __init__(self, image_name, x, y):
        pygame.sprite.Sprite.__init__(self)
        
        self.image_name = str(image_name)
        image = CARS[str(self.image_name)]

        # scale the image down so it's not wider than the lane
        image_scale = 80 / image.get_rect().width
        new_width = image.get_rect().width * image_scale
        new_height = image.get_rect().height * image_scale
        
        self.image = pygame.transform.scale(image, (new_width, new_height))
        
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.id = str(uuid.uuid4())
        
class PlayerVehicle(Vehicle):
    
    def __init__(self, image_name, x, y):
        super().__init__(image_name, x, y)


