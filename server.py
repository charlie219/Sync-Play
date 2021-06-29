# Authored By- Akash Kumar Bhagat
# Github Id - @charlie219
# Email - akashkbhagat221199@gmail.com
# Date - 25-6-2021


from collections import defaultdict
from random import randint
import socket
from _thread import *
import sys
import select
import pickle

class Server:
    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        server = ''                    # make it blank for the AWS es2 instance
        port = 5690                    # Enable incoming trafic from security groups

        server_ip = socket.gethostbyname(server)
        self.HEADER = 4

        try:
            self.server_socket.bind((server, port))
        except socket.error as e:
            print(str(e))

        # Important static variables
        self.Groups = {}
        #self.sock_list = [self.server_socket]
        self.Admin_list = {}
        self.client_list = {}


        self.server_socket.listen()
        print(":: Server is Running ::")
        print("Waiting for a connection")
        self.event_loop()
    
    def insert_client(self, client_info, client_sock, isAdmin = 0):
        if isAdmin:
            self.Groups[client_info['Group ID']] = client_sock
            self.Admin_list[client_sock] = [] 
        else:
            self.Admin_list[self.Groups[client_info['Group ID']]].append(client_sock)
        self.client_list[client_sock] = {
            'Username' : client_info['Username'],
            'Group ID' : client_info['Group ID'],
            'Admin'    : self.Groups[client_info['Group ID']]
        }

    def receive_command(self, client_socket):
        try:
            message_header = client_socket.recv(self.HEADER)
            if not len(message_header):
                return False
            message_length = int(message_header.decode('utf-8').strip())

            return pickle.loads(client_socket.recv(message_length))

        except:
            return False

    # Send Command to each member
    def send_command(self, Admin, command):
        
        msg = pickle.dumps(command)
        msg = bytes(f'{len(msg):<{self.HEADER}}', 'utf-8') + msg
        for member in self.Admin_list[Admin]:
            member.send(msg)

    def event_loop(self):

        socket_list = [self.server_socket]
        while True:
            read_socket, write_socket , exception_socket = select.select(socket_list, [], socket_list)
            temp_socket_list = [self.server_socket]

            for sock in read_socket:

                # New incoming Connection
                if sock == self.server_socket:
                    
                    # Accept the client
                    client_sock, addr = self.server_socket.accept()

                    hdr = client_sock.recv(self.HEADER)
                    if not hdr:
                        continue
                    msg_len = int(hdr.decode('utf-8'))
                    msg = client_sock.recv(msg_len)
                    client_info = pickle.loads(msg)

                    print(f"Connection Established : Username - {client_info['Username']}, addr = {addr}")
                    #print(client_info)
                    # If the client wants to join a group
                    if client_info['Choice'] == 1:

                        # Creating randon 4 digit Group_ID
                        new_group = randint(1111,9999)
                        while new_group in self.Groups:        new_group = randint(1111,9999)
                        client_info['Group ID'] = new_group
                        self.insert_client(client_info, client_sock, 1)

                        msg = str(new_group)
                        client_sock.send(bytes(msg, 'utf-8'))

                    else:

                        # If the group doesnot exist
                        if client_info['Group ID'] not in self.Groups:
                            client_sock.send(bytes('0', 'utf-8'))
                            continue
                        else:
                            msg = client_info['Group ID']
                            client_sock.send(bytes(str(msg), 'utf-8'))
                            
                        self.insert_client(client_info, client_sock)
                    
                    socket_list.append(client_sock)
                        
                # Command/Request from the admin
                else:
                    msg = self.receive_command(sock)

                    # Connection Closed
                    if msg is False:
                        exception_socket += [sock]
                    
                    # Command from Admin which will be delivered to the clients
                    else:
                        self.send_command(sock, msg)
            
                            

            for sock in  exception_socket:
                print("Connection Closed by user- " , self.client_list[sock]['Username'])
                
                # if the disconnected socket is an Admin
                if sock in self.Admin_list:
                    
                    # Send message to all members that the admin left
                    self.send_command(sock, dict())

                    # Remove the client info and Group
                    del self.Groups[self.client_list[sock]['Group ID']]
                    del self.client_list[sock]

                    # Removing all members form the client_list
                    for member_sock in self.Admin_list[sock]:
                        del self.client_list[member_sock]
                        socket_list.remove(member_sock)

                    del self.Admin_list[sock]
                
                # other group member
                else:
                    self.Admin_list[self.client_list[sock]['Admin']].remove(sock)
                    del self.client_list[sock]

                socket_list.remove(sock)
                sock.shutdown(socket.SHUT_RDWR)
                sock.close()

            #print(self.Admin_list,len(self.client_list.keys()))
            
