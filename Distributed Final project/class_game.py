import pygame
from pygame.locals import *
import random
import socketio
import eventlet
import psycopg2
import uuid
from tkinter import messagebox
import threading


from const_game import *

class Vehicle(pygame.sprite.Sprite):
    
    def __init__(self, image, x, y):
        pygame.sprite.Sprite.__init__(self)
        
        # scale the image down so it's not wider than the lane
        image_scale = 80 / image.get_rect().width
        new_width = image.get_rect().width * image_scale
        new_height = image.get_rect().height * image_scale
        self.image = pygame.transform.scale(image, (new_width, new_height))
        
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        
class PlayerVehicle(Vehicle):
    
    def __init__(self, image, x, y):
        super().__init__(image, x, y)


class Game:
    def __init__(self, w, h):
        #self.net = Network()
        self.width = w
        self.height = h

        pygame.init()

        # create the window
        self.screen_size = (self.width, self.height)
        self.screen = pygame.display.set_mode(self.screen_size, flags=pygame.HIDDEN)
        pygame.display.set_caption('Car Game')

        self.CARS = []
        self.CARS.append(pygame.image.load('Vertical Cars/green-car.png'))
        self.CARS.append(pygame.image.load('Vertical Cars/grey-car.png'))
        self.CARS.append(pygame.image.load('Vertical Cars/purple-car.png'))
        self.CARS.append(pygame.image.load('Vertical Cars/red-car.png'))

        # road and marker sizes
        self.road_width = 600
        self.marker_width = int(self.road_width  / 40)
        self.marker_height = self.marker_width * 5

        # lane coordinates
        self.left_lane = 150
        self.center_lane = 250
        self.right_lane = 350
        self.left2_lane = 450
        self.center2_lane = 550
        self.right2_lane = 650
        self.lanes = [self.left_lane, self.center_lane, self.right_lane, self.left2_lane, self.center2_lane]

        # road and edge markers
        self.road = (100, 0, self.road_width, self.height)
        self.left_edge_marker = (95, 0, self.marker_width, self.height)
        self.right_edge_marker = (690, 0, self.marker_width, self.height)

        # for animating movement of the lane markers
        self.lane_marker_move_y = 0

        # player's starting coordinates
        self.player_x = 250
        self.player_y = 700

        # frame settings
        self.clock = pygame.time.Clock()
        self.fps = 120

        # game settings
        self.gameover = False
        self.speed = 2
        self.score = 0

        # sprite groups
        self.player_group = pygame.sprite.Group()
        self.vehicle_group = pygame.sprite.Group()

        # create the player's car
        image = random.choice(self.CARS)
        self.player = PlayerVehicle(image, self.player_x, self.player_y)
        self.player_group.add(self.player)

        #lobby timer
        self.counter = 10
        self.font_timer = pygame.font.SysFont(None, 100)
        self.text_timer = self.font_timer.render(str(self.counter), True, (0, 128, 0))

        self.timer_event = pygame.USEREVENT+1        
        self.timeout = False

        #in-game timer
        self.ingame_counter = 30
        self.timer_ingame = pygame.USEREVENT+2
        

    def run(self):
        pygame.time.set_timer(self.timer_event, 1000)
        pygame.time.set_timer(self.timer_ingame, 1000)
        self.screen = pygame.display.set_mode(self.screen_size, flags=pygame.SHOWN)
        running = True
        while running:
            
            self.clock.tick(self.fps)
            self.score_add = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == self.timer_event:
                    print(self.counter)
                    self.counter -= 1
                    self.text_timer = self.font_timer.render(str(self.counter), True, (0, 128, 0))
                    if self.counter < 0:
                        pygame.time.set_timer(self.timer_event, 0)
                        self.timeout = True    
                # move the player's car using the left/right arrow keys
                elif event.type == KEYDOWN and self.timeout == True:
                    if event.key == K_LEFT and self.player.rect.center[0] > self.left_lane:
                        self.player.rect.x -= 100
                    elif event.key == K_RIGHT and self.player.rect.center[0] < self.right2_lane:
                        self.player.rect.x += 100

                    # check if there's a side swipe collision after changing lanes
                    for vehicle in self.vehicle_group:
                        if pygame.sprite.collide_rect(self.player, vehicle):
                            
                            self.score_add = True
                
                if self.timeout == True and event.type == self.timer_ingame:
                    self.ingame_counter -= 1
                    print("one sec")

            if self.timeout == False: #no more players will join
                self.screen.fill((255, 255, 255))
                self.text_timer_rect = self.text_timer.get_rect(center = self.screen.get_rect().center)
                self.screen.blit(self.text_timer, self.text_timer_rect)
            else:
                # new background for the game
                pygame.draw.rect(self.screen, (0,128,0), pygame.Rect(0, 0, 800, 500))
                #self.start_game()
            
                # clock.tick(fps)
                # score_add = False
 
                # draw the grass
                self.screen.fill(green) 
                
                # draw the road
                pygame.draw.rect(self.screen, gray, self.road)
                
                # draw the edge markers
                pygame.draw.rect(self.screen, yellow, self.left_edge_marker)
                pygame.draw.rect(self.screen, yellow, self.right_edge_marker)
                
                # draw the lane markers
                self.lane_marker_move_y += self.speed * 2
                if self.lane_marker_move_y >= self.marker_height * 2:
                    self.lane_marker_move_y = 0
                for y in range(self.marker_height * -2, self.height, self.marker_height * 2):
                    pygame.draw.rect(self.screen, white, (self.left_lane + 45, y + self.lane_marker_move_y, self.marker_width, self.marker_height))
                    pygame.draw.rect(self.screen, white, (self.center_lane + 45, y + self.lane_marker_move_y, self.marker_width, self.marker_height))
                    pygame.draw.rect(self.screen, white, (self.right_lane + 45, y + self.lane_marker_move_y, self.marker_width, self.marker_height))
                    pygame.draw.rect(self.screen, white, (self.left2_lane + 45, y + self.lane_marker_move_y, self.marker_width, self.marker_height))
                    pygame.draw.rect(self.screen, white, (self.center2_lane + 45, y + self.lane_marker_move_y, self.marker_width, self.marker_height))
                                      

                # draw the player's car
                self.player_group.draw(self.screen)
                
                # add a vehicle
                if len(self.vehicle_group) < 5:
                    
                    #ensure there's enough gap between vehicles
                    add_vehicle = True
                    for vehicle in self.vehicle_group:
                        if vehicle.rect.top < vehicle.rect.height * 0.01:
                            add_vehicle = False
                            
                    if add_vehicle:
                        
                    # select a random lane
                        lane = random.choice(self.lanes)
                        
                        # select a random vehicle image
                        #image = random.choice(vehicle_images)
                        image = pygame.image.load("dollar gold coin.png")
                        vehicle = Vehicle(image, lane, self.height / -2)
                        self.vehicle_group.add(vehicle)
                    
                # make the vehicles move
                for vehicle in self.vehicle_group:
                    vehicle.rect.y += self.speed
                    
                    # remove vehicle once it goes off screen
                    if vehicle.rect.top >= self.height:
                        vehicle.kill()
                        
                        # add to score
                        # score += 1
                        
                        # speed up the game after passing 5 vehicles
                        # if score > 0 and score % 5 == 0:
                        #    speed += 1
                
                # draw the vehicles
                self.vehicle_group.draw(self.screen)
                
                # display the score
                font_score = pygame.font.Font(pygame.font.get_default_font(), 16)
                text_score = font_score.render('Score: ' + str(self.score), True, white)
                text_score_rect = text_score.get_rect()
                text_score_rect.center = (50, 400)
                self.screen.blit(text_score, text_score_rect)
                
                # check if there's a head on collision
                if pygame.sprite.spritecollide(self.player, self.vehicle_group, True):
                    # add to score
                    #score += 1
                    self.score_add = True
                    #gameover = True
                    #self.crash_rect.center = [self.player.rect.center[0], self.player.rect.top]

                if self.score_add == True:
                    self.score += 1

                if self.ingame_counter < 0:
                    self.gameover = True
                # display game over
                if self.gameover:
                    #screen.blit(crash, crash_rect)
                    
                    pygame.draw.rect(self.screen, red, (0, 50, self.width, 100))
                    
                    font_go = pygame.font.Font(pygame.font.get_default_font(), 16)
                    text_go= font_go.render('Game over. Play again? (Enter Y or N)', True, white)
                    text_go_rect = text_go.get_rect()
                    text_go_rect.center = (self.width / 2, 100)
                    self.screen.blit(text_go, text_go_rect)
                    #screen.blit(text_score, text_score_rect)

                pygame.display.update()

                # wait for user's input to play again or exit
                while self.gameover:
                    
                    self.clock.tick(self.fps)
                    
                    for event in pygame.event.get():
                        
                        if event.type == QUIT:
                            self.gameover = False
                            running = False
                            
                        # get the user's input (y or n)
                        if event.type == KEYDOWN:
                            if event.key == K_y:
                                # reset the game
                                self.gameover = False
                                self.speed = 2
                                self.score = 0
                                self.ingame_counter = 30
                                self.vehicle_group.empty()
                                self.player.rect.center = [self.player_x, self.player_y]
                            elif event.key == K_n:
                                # exit the loops
                                self.gameover = False
                                running = False
            pygame.display.flip()
        pygame.quit()




# game = Game(800,800)
# run = input("run now? ")
# if run == True:
#     game.run()
