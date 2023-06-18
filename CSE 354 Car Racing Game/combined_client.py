import os
import pygame
from pygame.locals import *
import tkinter as tk
from tkinter import *
import socketio
import threading
import random
import time
import sys


from trial2_game_vehicle import PlayerVehicle, Coin
from pg_gui_const import Button, TextBox, ChatBubble
from const_game import *


sio = socketio.Client()

username = ''
all_messages = set()
chat_bubbles = set()


width = 1110 #1100-800 = 300 for chatwindow
height = 800


screen = pygame.display.set_mode((width,height))
screen.fill(pygame.Color(255,255,255))
pygame.display.set_caption("Car Game")
pygame.display.init()
pygame.font.init()
pygame.display.update()


####################################################################################################################
GREEN_CAR = pygame.image.load('Vertical Cars/green-car.png')
GREY_CAR = pygame.image.load('Vertical Cars/grey-car.png')
PURPLE_CAR = pygame.image.load('Vertical Cars/purple-car.png')
RED_CAR = pygame.image.load('Vertical Cars/red-car.png')
CAR_NAMES = ['green', 'grey', 'purple', 'red']
CARS = {'green': GREEN_CAR, 
          'grey': GREY_CAR, 
          'purple': PURPLE_CAR, 
          'red': RED_CAR}


# def update_gui():
#     pass
#     #implement on server-side


def emit_msg(dict):
    sio.emit('message', dict)

def send_message():
    global username
    if textbox.text: #new textbox = message box
        dict = {'username': username, 'message': textbox.text}
        print("message and user: ", dict)
        threading.Thread(target=emit_msg, args=(dict,)).start() #this calls the server to append the message to history
        textbox.text = ''
        #message_entry.delete(0, 'end')


def open_new_window():
    global textbox, button, screen, flag_down_lobby
    if textbox.text:
        # Connect to the server
        sio.connect('http://localhost:5050', namespaces=['/'])

        # Hide the login screen and show the chat screen
        new_screen_width = 1100
        new_screen_height = 800
        new_screen = pygame.display.set_mode((new_screen_width, new_screen_height))
        pygame.display.set_caption('New Window')


        new_textbox = TextBox(new_screen, 810, 700, 290, 32)
        new_button = Button(new_screen, 810, 740, 200, 50, 'Send message', send_message)

        textbox = new_textbox
        button = new_button
        screen = new_screen
 
    pygame.display.update()

    flag_down_lobby = True


textbox = TextBox(screen, 50, 50, width - 100, 32)
button = Button(screen, 50, 100, 200, 50, 'Login user', open_new_window)
flag_down_lobby = False


# road and marker sizes
road_width = 600
marker_width = int(road_width  / 40)
marker_height = marker_width * 5

# lane coordinates
lane_1 = 150
lane_2 = 250
lane_3 = 350
lane_4 = 450
lane_5 = 550
lane_6 = 650
lanes = [lane_1, lane_2, lane_3, lane_4, lane_5, lane_6]

# road and edge markers
road = (100, 0, road_width, 800)
left_edge_marker = (95, 0, marker_width, 800)
right_edge_marker = (690, 0, marker_width, 800)

# for animating movement of the lane markers
lane_marker_move_y = 0

# player's starting coordinates
# player_x = 250
# player_y = 700

# frame settings
clock = pygame.time.Clock()
fps = 120

# game settings
gameover = False
speed = 1 #2
score = 0

# sprite groups
player_group = pygame.sprite.Group() #group of players currently on screen
vehicle_group = pygame.sprite.Group() #group of coin sprites currently on screen

# create the player's car
image_name = random.choice(CAR_NAMES)
player = None
# draw the player's car
#player_group.draw(screen)

#in-game timer
ingame_counter = 30
timer_ingame = pygame.USEREVENT+2


###################################################################################################################





#Initially, for all clients:
this_game = { #dict
    'state' : 'gameplay', #'gameover'
    'num_players' : 0,
    'player': None, #sprite #this will be created upon connection
    'player_img': image_name, #just the name
    'player_x' : 0,
    'player_y' : 700,
    'player_group': None, #sprite group #this will be created upon connection
    'vehicle_group': None, #sprite group #this will be created upon connection
    'score' : 0
}


@sio.event
def update_game_clients_state(data):
    # update this_game state to match server's
    #this_game['state'] = data['state']
    this_game['num_players'] = data['num_players']
    this_game['player_x'] = data['player_x']
    this_game['player_group'] = data['player_group']
    this_game['vehicle_group'] = data['vehicle_group']

    print("3) Client received emit, game_state changed and will be displayed")
    #update display
    # draw the player's car
    #player_group.draw(screen)


def event_main_pygame():
    
    global clock, score_add, score
    clock.tick(fps)
    score_add = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == KEYDOWN: #and self.timeout == True:
            if event.key == K_LEFT and this_game['player_group'][player.id][0] > lane_1 and this_game['player_group']!=None:
                this_game['player_group'][player.id][0] -= 100
                print("There is car movement. Now we emit the new players pos")
                sio.emit('update_game_server_state', data = this_game)
            elif event.key == K_RIGHT and this_game['player_group'][player.id][0] < lane_6 and this_game['player_group']!=None:
                this_game['player_group'][player.id][0] += 100
                print("There is car movement. Now we emit the new players pos")
                sio.emit('update_game_server_state', data = this_game)
            
            # check if there's a side swipe collision after changing lanes
            for vehicle in vehicle_group:
                if pygame.sprite.collide_rect(player, vehicle):
                    score_add = True
        
        textbox.handle_event(event)
        button.handle_event(event)

    # new background for the game
    pygame.draw.rect(screen, (0,128,0), pygame.Rect(0, 0, 800, 500))  
    # draw the grass
    screen.fill(green) 
    # draw the road
    pygame.draw.rect(screen, gray, road)
    # draw the edge markers
    pygame.draw.rect(screen, yellow, left_edge_marker)
    pygame.draw.rect(screen, yellow, right_edge_marker)
    # draw the lane markers
    global lane_marker_move_y
    lane_marker_move_y += speed * 2
    if lane_marker_move_y >= marker_height * 2:
        lane_marker_move_y = 0
    for y in range(marker_height * -2, height, marker_height * 2):
        pygame.draw.rect(screen, white, (lane_1 + 45, y + lane_marker_move_y, marker_width, marker_height))
        pygame.draw.rect(screen, white, (lane_2 + 45, y + lane_marker_move_y, marker_width, marker_height))
        pygame.draw.rect(screen, white, (lane_3 + 45, y + lane_marker_move_y, marker_width, marker_height))
        pygame.draw.rect(screen, white, (lane_4 + 45, y + lane_marker_move_y, marker_width, marker_height))
        pygame.draw.rect(screen, white, (lane_5 + 45, y + lane_marker_move_y, marker_width, marker_height))


    # draw the cars
    player_group.empty()
    #current_game['player_group'][player.id] = (player.rect, player.image_name)
    if this_game['player_group'] != None:
        for p in this_game['player_group'].values(): #recreate sprites group from the json list
            player_group.add(PlayerVehicle(p[2], p[0], p[1]))
        # if player_group != None:
        player_group.draw(screen)
        
    # add a coin
    if len(vehicle_group) < 5:
        #ensure there's enough gap between coins
        add_vehicle = True
        for vehicle in vehicle_group:
            if vehicle.rect.top < vehicle.rect.height * 0.01:
                add_vehicle = False
        if add_vehicle:
        # select a random lane
            lane = random.choice(lanes)
            # gold coin
            image = pygame.image.load("dollar gold coin.png")
            vehicle = Coin(image, lane, height / -2)
            vehicle_group.add(vehicle)
    # make the coins move
    for vehicle in vehicle_group:
        vehicle.rect.y += speed
        # remove coin once it goes off screen
        if vehicle.rect.top >= height:
            vehicle.kill()
            # add to score
            # score += 1

            # speed up the game after passing 5 vehicles
            # if score > 0 and score % 5 == 0:
            #    speed += 1
    
    # draw the vehicles
    vehicle_group.draw(screen)
    
#     # display the score
#     font_score = pygame.font.Font(pygame.font.get_default_font(), 16)
#     text_score = font_score.render('Score: ' + str(score), True, white)
#     text_score_rect = text_score.get_rect()
#     text_score_rect.center = (50, 400)
#     screen.blit(text_score, text_score_rect)
    
    # check if there's a head on collision
    if player != None and pygame.sprite.spritecollide(player, vehicle_group, True):
        # add to score
        score_add = True
    
    if score_add == True:
        this_game['score'] += 1
    
    #draw chat window
    pygame.draw.rect(screen, (144, 238, 144), pygame.Rect(800, 0, 300, 800))
    # draw chat bubbles of all messages so far
    #print("all messages are:", all_messages) every single frame ya mo2men
    try:
        for bubble in chat_bubbles:
            bubble.draw()
    except:
        pass
 

    # draw chat input
    textbox.draw()
    button.draw()

    pygame.display.update()






def event_lobby_pygame():    
    global clock, score_add, score
    clock.tick(fps)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        textbox.handle_event(event)
        button.handle_event(event)
    
    # new background for the game
    screen.fill((255,255,255))
    # if flag_down_lobby:
    #     #draw chat window
    #     pygame.draw.rect(screen, (144, 238, 144), pygame.Rect(800, 0, 300, 800))
    #     # draw chat bubbles of all messages so far
    #     #print("all messages are:", all_messages) every single frame ya mo2men
    #     for bubble in chat_bubbles:
    #         bubble.draw()  
    # draw the grass
    textbox.draw()
    button.draw()
        
    pygame.display.update()



# thread
def client_state():

    # get last known game state
    current_game = sio.call('get_game_state')

    # update game_state
    global player_group, vehicle_group, player, image_name

    player = PlayerVehicle(image_name, current_game['player_x'], this_game['player_y'])
    this_game['player'] = dict()
    this_game['player'][player.id] = [player.rect.center[0], player.rect.center[1], player.image_name]

    if current_game['player_group'] == None:
        current_game['player_group'] = dict()
        
    current_game['player_group'][player.id] = [player.rect.center[0], player.rect.center[1], player.image_name]
    print("current_game['player_group']: ", current_game['player_group'])

    current_game['player_x'] += 100
    
    print("2) There is a change in display. Now we must emit.")

    # emit game_state
    sio.sleep(0)
    print("3) Emitting to server...")
    sio.emit('update_game_server_state', current_game) 
    sio.sleep(0)
    pygame.display.update()

    
# @sio.event
# def connect():
#     # chat stuff
#     global username
#     username =  textbox.text
#     print("my username!! is", username)
#     sio.emit('login', username)
#     print('Connected to server')
#     #flag_down_lobby = True
#     #sio.start_background_task(target=client_state) #inherent async model


# @sio.event
# def disconnect():
#     print('Disconnected from the server')


# @sio.event
# def message(data):
#     username = data['username']
#     message_text = data['message']
#     print(f'Received message from {username}: {message_text}')
#     # Update the GUI
#     # t1 = threading.Thread(target=update_gui, args=(data,text_box,)).start()
#     # t1.start()
#     #update_gui(username, message_text)



# # chat stuff
# """
# def login):
#     global username
#     username = username_entry.get()
#     if username:
#         # Connect to the server
#         sio.connect('http://localhost:5050', namespaces=['/'])
#         # Hide the login screen and show the chat screen
#         login_button.pack_forget()
#         username_label.pack_forget()
#         username_entry.pack_forget()
#         chat_screen()
        

# #login button
# login_button = Button(chatwin, text='Login', command=login)
# login_button.pack(padx=5, pady=5)
# """


# #sio.connect('http://localhost:5050', namespaces=['/'])



# # chat stuff
# """
# # Chat Screen
# def chat_screen():
#     # Message Entry
#     message_entry = Entry(chatwin)
#     message_entry.pack(padx=5, pady=5)

#     # Send Message Button
#     def send_message():
#         message_text = message_entry.get()
#         if message_text:
#             sio.emit('message', {'username': username_entry.get(), 'message': message_text})
#             message_entry.delete(0, 'end')
#         #Update the GUI
#         # t1 = threading.Thread(target=update_gui, args=
#         #                       ({'username': username_entry.get(), 'message': message_text}, text_box,)).start()
#         # t1.start()
#         update_gui({'username': username_entry.get(), 'message': message_text}, text_box)

#     send_button = Button(chatwin, text='Send', command=send_message)
#     send_button.pack(padx=5, pady=5)

# # Function to handle GUI updates
# def update_gui(message, text_box):
#     text_box.config(state='normal')  # Enable editing the text box
#     text_box.insert('end', f'{message["username"]}: {message["message"]}\n')
#     text_box.see('end')  # Scroll to the end of the text box
#     text_box.config(state='disabled')  # Disable editing the text box
#     time.sleep(0)


# @sio.event
# def history_messages(messages):
#     for message in messages:
#         username = message['username']
#         message_text = message['message']
#         print(f'Received history message from {username}: {message_text}')
#         # Update the GUI
#         # t1 = threading.Thread(target=update_gui, args=(message,text_box,)).start()
#         # t1.start()
#         update_gui(message, text_box)
# """

        
# if __name__ == '__main__':

#     sio.sleep(0)
#     while True:

#         sio.sleep(0)
#         event_lobby_pygame()
#         sio.sleep(0)

#         pygame.display.update()








@sio.event
def connect():
    global username
    username = textbox.text

    sio.emit('login', username)
    sio.start_background_task(target=client_state) #inherent async model
    print('Connected to server, from client-side')

# @sio.event
# def connect():
#     # chat stuff
#     global username
#     username =  textbox.text
#     print("my username!! is", username)
#     sio.emit('login', username)
#     print('Connected to server')
#     #flag_down_lobby = True
#     #sio.start_background_task(target=client_state) #inherent async model

@sio.event
def message(data):
    username = data['username']
    message_text = data['message']
    print(f'Received message from {username}: {message_text}')
    
    msg_str = username + " said: " + message_text
    #updating gui
    all_messages.add(msg_str)
    update_gui(msg_str)

@sio.event
def update_gui(msg_str):
    # a new message has been passed, create its chat bubble
    global all_messages
    print("all_messages: ", all_messages, "message: ", msg_str) 
    
    iter = len(all_messages)
    chat_bubbles.add(ChatBubble(screen, 810, 30*iter, 300, 20, text=msg_str))
    # iter +=1
        



@sio.event
def disconnect():
    print('Disconnected from server, from client-side')


if __name__ == '__main__':
    while True:
        sio.sleep(0)
        if(flag_down_lobby):
            event_main_pygame()
        else:
            event_lobby_pygame()
        sio.sleep(0)
        pygame.display.update()
