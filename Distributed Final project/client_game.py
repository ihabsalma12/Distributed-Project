import socketio
#import psycopg2
from tkinter import Tk, Button, Text, Label, Scrollbar, Entry
from threading import Thread



sio = socketio.Client()

# GUI setup
root = Tk()
root.title('Chat Application')

# Message Box
text_box = Text(root)
text_box.pack()

# Username Label
username_label = Label(root, text='Enter Your Username ')
username_label.pack(padx=10, pady=10)

# Username Entry
username_entry = Entry(root)
username_entry.pack(padx=5, pady=5)
username = username_entry.get()






@sio.event
def connect():
    sio.emit('login', username)
    print('Connected to server')
    # sio.start_background_task(demo_task)
    #thread for game OR global 'login' state
    #sio.emit('get_history_messages')
 
 
def login():
    username = username_entry.get()
    if username:
        # Connect to the server
        sio.connect('http://localhost:5050', namespaces=['/'])
        # Hide the login screen and show the chat screen
        login_button.pack_forget()
        username_label.pack_forget()
        username_entry.pack_forget()
        chat_screen()
        # game_screen()
        

#login button
login_button = Button(root, text='Login', command=login)
login_button.pack(padx=5, pady=5)



# Game Screen
# def game_screen():
#     my_game_state = sio.call('start_game')
    # Message Entry
    # message_entry = Entry(root)
    # message_entry.pack(padx=5, pady=5)

    # # Send Message Button
    # def send_message():
    #     message_text = message_entry.get()
    #     if message_text:
    #         sio.emit('message', {'username': username_entry.get(), 'message': message_text})
    #         message_entry.delete(0, 'end')
    #     #Update the GUI
    #     update_gui({'username': username_entry.get(), 'message': message_text}, text_box)

    # send_button = Button(root, text='Send', command=send_message)
    # send_button.pack(padx=5, pady=5)






# Chat Screen
def chat_screen():
    # Message Entry
    message_entry = Entry(root)
    message_entry.pack(padx=5, pady=5)

    # Send Message Button
    def send_message():
        message_text = message_entry.get()
        if message_text:
            sio.emit('message', {'username': username_entry.get(), 'message': message_text})
            message_entry.delete(0, 'end')
        #Update the GUI
        update_gui({'username': username_entry.get(), 'message': message_text}, text_box)

    send_button = Button(root, text='Send', command=send_message)
    send_button.pack(padx=5, pady=5)

# Function to handle GUI updates
def update_gui(message, text_box):
    text_box.config(state='normal')  # Enable editing the text box
    text_box.insert('end', f'{message["username"]}: {message["message"]}\n')
    text_box.see('end')  # Scroll to the end of the text box
    text_box.config(state='disabled')  # Disable editing the text box

@sio.event
def disconnect():
    print('Disconnected from the server')

@sio.event
def message(data):
    username = data['username']
    message_text = data['message']
    print(f'Received message from {username}: {message_text}')
    # Update the GUI
    update_gui(data, text_box)

@sio.event
def history_messages(messages):
    for message in messages:
        username = message['username']
        message_text = message['message']
        print(f'Received history message from {username}: {message_text}')
        # Update the GUI
        update_gui(message, text_box)

if __name__ == '__main__':

    root.mainloop()
    #username = username_entry.get() 
    #input("Enter your username: ")

    # while True:
    #     message_text = input("Enter your message (or 'quit' to exit): ")
    #     if message_text.lower() == 'quit':
    #         break
    #     # Send the message to the server
    #     sio.emit('message', {'username': username, 'message': message_text})

