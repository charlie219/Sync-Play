import socket
from PyQt5.QtWidgets import *
import sys
import pickle
import json
from mediaplayer import Window
import gui

class Client:

    def __init__(self, user_name, choice, group_id = None, frame = None):
        #print(user_name, choice, group_id, frame)
        if frame:
            frame.destroy()
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = "127.0.0.1"     # For this to work on your machine this must be equal to the ipv4 address of the machine running the server
                                    # You can find this address by typing ipconfig in CMD and copying the ipv4 address. Again this must be the servers
                                    # ipv4 address. This feild will be the same for all your clients.
        self.port = 8080            # Same as the server 
        self.HEADER = 4
        # Important static variables
        self.uname = user_name
        self.choice = choice
        self.group_id = group_id
        
        self.addr = (self.host, self.port)
        self.connect()

    def connect(self):
        self.client.connect(self.addr)
        #print("Connected to server")
        payload = {
            'Username' : self.uname,
            'Choice'   : self.choice,
            'isAdmin'  : True
        }

        if self.choice == 2:    
            payload['Group ID'] = int(self.group_id)
            payload['isAdmin']  = False 
    
        msg = pickle.dumps(payload)
        msg = bytes(f'{len(msg):<{self.HEADER}}', 'utf-8') + msg
        self.client.send(msg)

        flag = self.client.recv(4)
        flag = flag.decode('utf-8')
        if flag == '0':
            gui.Application(self.uname)

        else:
            payload['Group ID'] = int(flag)

        
        app = QApplication(sys.argv)
        window = Window(self.client, payload)
        sys.exit(app.exec_())

        #print("Message sent", payload)

#client1 = Client("karan_236", 2, 6790)

