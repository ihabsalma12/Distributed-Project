import socketio
import eventlet
import psycopg2
import uuid
from tkinter import messagebox
import threading
import uuid


# import psycopg2.extras

# # call it in any place of your program
# # before working with UUID objects in PostgreSQL
# psycopg2.extras.register_uuid()



# router connect two laps for deployment


sio = socketio.Server()
app = socketio.WSGIApp(sio)

messages = []


def connect_to_database():
    try:
        connection = psycopg2.connect(
            host="gamedb.cyqyiojugosc.eu-north-1.rds.amazonaws.com",
            port=5432,
            user="PostGres",
            password="123456789",
            dbname="postgres"
        )
        return connection
    except psycopg2.Error as error:
        print('Error connecting to the database:', error)


# @sio.event
# def start_game(sid):
#     game.run()

# game = Game(800, 800, sio)

players = {'1': [], '2': [], '3': [], '4': []}
cars1 = {}
num_players = 0


def update_gui(message):
    pass


def add_player(sid):
    global num_players
    num_players += 1
    players[str(num_players)].append('player '+str(num_players))
    print(players)
    #dictionary players empty -> player 1 , player 2
    print("There are currently ", str(num_players), "players.")
    sio.emit('log', data = sid + ", You were added to the game!", room=sid) #
    #run_game_logic(game)
    # threading.Thread(target=map_car, args=(sid,)).start() #args=(game,)).start()
    if (num_players>1):
        map_car(sid)
    elif (num_players==1):
        players['1'].append('Vertical Cars/red-car.png')

def map_car(sid):
        players['1'].append('Vertical Cars/red-car.png')
        players['2'].append('Vertical Cars/purple-car.png')


@sio.event
def connect(sid, environ):
    sio.emit('history_messages', messages, room=sid)
    # threading.Thread(target=add_player, args=(sid,)).start() #args=(game,)).start()
    # add_player(sid)
    # global num_players
    # num_players +=1
    # print(num_players)
    # sio.emit('number',num_players)
    print('Client connected', sid)

    # global num_players


@sio.event
def disconnect(sid):
    # save the last message
    # save the last state of the disconnected user

    print('Client disconnected', sid)


@sio.event
def login(sid,username):
    # username = username_entry.get()
    connection = connect_to_database()
    #user_id = uuid.uuid4()
    if connection:
        try:
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
                INSERT INTO "GameSchema"."users"(username)
                VALUES (%s)
                """
                cursor.execute(query, (username,))
                connection.commit()
                print('Username saved to the database')

        except psycopg2.Error as error:
            print('Error accessing the database1:', error)
        finally:
            cursor.close()
            connection.close()
        


@sio.event
def message(sid, data):
    username = data['username']
    message_text = data['message']
    print(f'Received message from {username}: {message_text}')
    # Process and save the message on the server

    # Create a message object
    message = {'username': username, 'message': message_text}

    # Add the message to the list
    messages.append(message)

    # Broadcast the message to all connected clients
    sio.emit('message', message, skip_sid=sid)

    # Update the GUI
    threading.Thread(target=update_gui, args=(message,)).start()
    message_id = str(uuid.uuid4())
    #sid = uuid.uuid4()
    #sid = str(uuid.uuid4())
    # Create a cursor to interact with the database
    # conn.connect()

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


def run_server():
    eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 5050)), app)


if __name__ == '__main__':
    run_server()
