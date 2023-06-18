import socketio
import eventlet
import psycopg2
import uuid
from tkinter import messagebox
import threading
import json

#router connect two laps for deployment


sio = socketio.Server()
app = socketio.WSGIApp(sio)


this_game = { #dict
    'state' : 'gameplay', #'gameover'
    'num_players' : 0,
    # 'player_img': None,
    'player_x' : 250, #used to hold pos. of next player
    #'player_y' : 700,
    'player_group': None,
    'vehicle_group': None
    # 'score' : 0
}


# chat stuff

messages=[]


def connect_to_database():
    try:
        connection = psycopg2.connect(
            host="gamedb.cyqyiojugosc.eu-north-1.rds.amazonaws.com",
            port=5432,
            user="PostGres",
            password="123456789",
            dbname="postgres",
            connect_timeout=3
        )
        return connection
    except psycopg2.Error as error:
        print('Error connecting to the database:', error)


# def update_gui(message):
#     #broadcast the message list to all clients, who draw the chat bubbles in their update_gui, 
#     # then bubble.draw all the bubbles in the pg infinite loop. put the bubbles in a bubble group. maybe a sprite group?
#     # no, sprites are images. we want rects
    
#     print("please, client, update your gui. messages: ", dict(messages))
#     sio.emit('update_all_messages', dict(messages))
#     # messagebox.showinfo(message['username'], message['message'])


@sio.event
def login(sid,username):
    print("they never got ethiopia")
    connection = connect_to_database()
    user_id = sid#str(uuid.uuid4())
    if connection: 
        try: #login into postgres...
            cursor = connection.cursor()

            # delete_query = """
            # DELETE FROM "GameSchema".users
            # """
            # cursor.execute(delete_query)

            select_query = """
            SELECT username FROM "GameSchema"."users" WHERE username = %s
            """
            cursor.execute(select_query, (username,))
            result = cursor.fetchone()
            if result:
                print(f'Hello, {username}! Welcome back.')
            else:
                query = """
                INSERT INTO "GameSchema"."users"("user_id", "username")
                VALUES (%s,%s)
                """
                cursor.execute(query, (user_id, username,))
                connection.commit()
                print('Username saved to the database')
        except psycopg2.Error as error:
            print('Error accessing the database1:', error)
        finally:
            cursor.close()
            connection.close()
    #else #error handling, if a successful database conn doesn't return, do nothing 

@sio.event
def message(sid, data):
    username = data['username']
    message_text = data['message']
    print(f'Received message from {username}: {message_text}')
    # Process and save the message on the server

    # Create a message object
    message = {'username': username, 
               'message': message_text}

    # Add the message to the list
    messages.append(message)

    # Broadcast the message to all connected clients
    print("please, client, update your gui. messages: ", message, type(message))
    sio.emit('message', message)#, skip_sid=sid) #this only prints the message on client console
    
    #sio.emit('update_all_messages', list(messages))
    # Update the GUI
    #threading.Thread(target=update_gui, args=(message,)).start() #this calls the client to add a chat bubble
    message_id = str(uuid.uuid4())
    # Create a cursor to interact with the database
    connection = connect_to_database()
    if connection:
        try:
            cursor = connection.cursor()
            print("Successfully connected to the database!")

            insert_query = """
                INSERT INTO "GameSchema"."Messages"("message_id","content","player_id")
                VALUES (%s, %s, %s)
            """
            cursor.execute(insert_query, (message_id,message['message'],sid,))
            connection.commit()
            print("Data inserted successfully!")
            print(insert_query)
            print(message_id, message['message'], sid)
        except psycopg2.Error as error:
            print('Error accessing the database2:', error)
        finally:
            cursor.close()
            #connection.close()



@sio.event
def custom_event(sid):
    print("custom event emitted!")

# @sio.event
# def connect(sid, environ):
#     #sio.emit('history_messages', messages, room=sid) #chat stuff
#     print('Client connected',sid)

# @sio.event
# def disconnect(sid):
#     #save the last message 
#     #save the last state of the disconnected user 
#     print('Client disconnected',sid)


# def run_server():
#     eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 5050)), app)

# if __name__ == '__main__':
#     run_server()



@sio.event
def connect(sid, environ):
    #sio.emit('history_messages', messages, room=sid) #chat stuff
    global this_game
    this_game['num_players'] += 1
    print('Client connected:', sid)

@sio.event
def disconnect(sid):
    #save the last message 
    #save the last state of the disconnected user 
    global this_game
    this_game['num_players'] -= 1
    print('Client disconnected:', sid)


@sio.event
def get_game_state(sid):
    return this_game


@sio.event
def update_game_server_state(sid, data):
    global this_game
    #this_game['state'] = data['state']
    this_game['player_x'] = data['player_x']
    this_game['player_group'] = data['player_group']
    #this_game['vehicle_group'] = data['vehicle_group']

    print("3) Server received emit, game_state changed ONLY")
    sio.emit('update_game_clients_state', data)#, skip_sid=sid) 
    
# @sio.event
# def my_message(sid, data):
#     print('Message received:', data)
#     sio.emit('my_response', {'data': 'Server responded'})

if __name__ == '__main__':
    import eventlet
    eventlet.wsgi.server(eventlet.listen(('', 5050)), app)
