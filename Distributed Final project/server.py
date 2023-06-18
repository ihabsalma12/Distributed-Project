import socketio
import eventlet
import psycopg2
import uuid
from tkinter import messagebox
import threading


sio = socketio.Server()
app = socketio.WSGIApp(sio)

messages=[]

# def connect_to_database():
#     try:
#         connection = psycopg2.connect(
#             host="database-2.cr99gf9eqcuq.eu-north-1.rds.amazonaws.com",
#             port=5432,
#             user="postgres",
#             password="12345678",
#             dbname= "postgres"
#         )
#         return connection
#     except psycopg2.Error as error:
#         print('Error connecting to the database:', error)

def update_gui(message):
   pass
# messagebox.showinfo(message['username'], message['message'])

@sio.event
def connect(sid, environ):
    sio.emit('history_messages', messages, room=sid)
    print('Client connected',sid)

@sio.event
def disconnect(sid):
    #save the last message 
    #save the last state of the disconnected user 

    print('Client disconnected',sid)

@sio.event
def login(sid,username):
    pass
    # #username = username_entry.get()
    # connection = connect_to_database()
    # if connection:
    #     try:
    #         cursor = connection.cursor()
    #         select_query = """
    #         SELECT username FROM "GameSchema"."users" WHERE username = %s
    #         """
    #         cursor.execute(select_query, (username,))
    #         result = cursor.fetchone()
    #         if result:
    #             print(f'Hello, {username}! Welcome back.')
    #         else:
    #             query = """
    #             INSERT INTO "GameSchema"."users" (username)
    #             VALUES (%s)
    #             """
    #             cursor.execute(query, (username,))
    #             connection.commit()
    #             print('Username saved to the database')

    #     except psycopg2.Error as error:
    #         print('Error accessing the database:', error)
    #     finally:
    #         cursor.close()
    #         connection.close()

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
    # Create a cursor to interact with the database
    #conn.connect()
    # connection = connect_to_database()
    # if connection:
    #     try:
    #         cursor = connection.cursor()
    #         print("Successfully connected to the database!")

    #         insert_query = """
    #             INSERT INTO "GameSchema"."Messages" (message_id, content , player_id)
    #             VALUES (%s, %s, %s)
    #         """
    #         cursor.execute(insert_query, (message_id, message['message'], sid))
    #         connection.commit()
    #         print("Data inserted successfully!")
    #         print(insert_query)
    #         print(message_id, message['message'], sid)
    #     except psycopg2.Error as error:
    #         print('Error accessing the database:', error)
    #     finally:
    #         cursor.close()
    #         #connection.close()

if __name__ == '__main__':
 
    app = socketio.WSGIApp(sio)
    socketio.Middleware(sio, app)
    eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 5050)), app)