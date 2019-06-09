# CS594 final project
# Daniel Lee & Chunyan Bao
# Implementing multiple clients chatroom using python socket programming
# This is the Server code

import socket
import select
import sys
from thread import *

"""The first argument AF_INET is the address domain of the 
socket. This is used when we have an Internet Domain with 
any two hosts The second argument is the type of socket. 
SOCK_STREAM means that data or characters are read in 
a continuous flow."""

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# checks whether sufficient arguments have been provided
if len(sys.argv) != 3:
	print "Correct usage: script, IP address, port number"
	exit()

# takes the first argument from command prompt as IP address
IP_address = str(sys.argv[1])

# takes second argument from command prompt as port number
Port = int(sys.argv[2])

""" 
binds the server to an entered IP address and at the 
specified port number. 
The client must be aware of these parameters 
"""
server.bind((IP_address, Port))

""" 
listens for 100 active connections. This number can be 
increased as per convenience. 
"""
server.listen(100)
list_of_rooms = {"main": []}
#list_of_clients = []
client_conn = []
client_name = []


def clientthread(conn, addr):

	# sends a message to the client whose user object is conn
	conn.send("Welcome to the chatroom!\ntype \help or \? for commands\n")
	# user name print out label, clients send their username first and then their message
	socket_label = True
	# When users connect to the server at the first, their name and connection will be added to the client list
	name_tag = 0
	# label for a user leaves a room
	leave_label = 0
	# label for joining a user to a chat room
	join_label = 0
	# label for sending message to the selected room
	select_label = 0
	# label for sending a private message
	private_label = 0
	# label for listing all the members in the room
	member_label = False
	# label for disconnecting with a client
	quit_label = False
	# A temp string for joining a client
	name_to_join = ''

	while True:
			try:
				message = conn.recv(2048)
				if message:
					"""Clients send either command or normal message to the server.
						If the message is recognized as a command, the server will 
						do the process and return the proper result. If it just a 
						normal message, the server will broadcast the message to the
						clients who stay in the same room."""

                                        # create a new room
					if message == "\create\n":
							room_num = len(list_of_rooms)
							room_name = 'room' + str(room_num)
							list_of_rooms[room_name] = []
                                                        print room_name + " has been created"
                                                        conn.send(room_name + " has been created")

                                        # At the first timg client connect, they will be added to the client list.
                                       	elif name_tag == 1:
						if message in client_name:
							conn.send("The user name has already been used.")
							conn.close()
						else:
							client_conn.append(conn)
							client_name.append(message)
							print message + 'has connected to the server.'
						name_tag = 0
                                        
					elif message == "name_coming":
						name_tag = 1
                                        
                                        # join a room
                                        elif join_label == 2:
						for room in list_of_rooms:
							if room == message:
								if name_to_join in list_of_rooms[room]:
									conn.send("You are already in that room.")
								else:
									list_of_rooms[room].append(name_to_join)
									conn.send("You have joined " + message)
									print name_to_join + "has been added to " + message
						join_label = 0
                                                #name_to_join = ''

					elif join_label == 1:
						name_to_join = message
						join_label = 2

					elif message == "\join\n":
						join_label = 1
				
                                        # list all rooms
					elif message == '\listroom\n':
						conn.send("Here's the list of available rooms: ")
						for room in list_of_rooms:
							conn.send(room + ' ')
                                                
					# help display
					elif message == "\help\n" or message == "\?\n":
						conn.send("help menu commands\n\n")
						conn.send("\create <room name> - creates a room with the room name\n\n")
						conn.send("\listroom - list the available rooms\n\n")
						conn.send("\join-executes the join command and prompts you for room you want to join\n\n")
						conn.send("\leave - executes the leave command and asks you what room you want to leave\n\n")
						conn.send("\memberlist-prompts user for the room input to check what members are in the targetted room\n\n")
						conn.send("\printall-prints all rooms with it's members\n\n\n")
						conn.send("\quit-disconnects from server\n\n")
						conn.send("\private-prompts user for target user to send message and prompts user for message input\n\n")
						conn.send("\selectroom-prompts user for target room and prompts message from user to send to a room\n\n")
					# list all rooms with all their member
					elif message == "\printall\n":
						conn.send("Here's the list of user in each room: ")
						for room in list_of_rooms:
							conn.send(room + " : ")
							for name in list_of_rooms[room]:
								conn.send(name)
				
                                        # send a private message
					elif private_label == 1:
						to_send = message
						private_label = 2
					elif private_label == 2:
						such_user = True
						for i in client_name:
							temp = i[:len(i)-1]
							if temp == to_send:
                                                        #if i[:len(i)-1] == to_send:
                                                                # client_name.index(i) -- index of user i in the list
								client_conn[client_name.index(i)].send(conn_to_name(conn)+'>')
								client_conn[client_name.index(i)].send(message)
								such_user = False
						if such_user:
							conn.send("There's no such user")
						private_label = 0
						such_user = True

					elif message == "\private\n":
						private_label = 1

                                        #leave a room
					elif leave_label == 2:
						for room in list_of_rooms:
							if room == message:
								if name_to_leave in list_of_rooms[room]:
									list_of_rooms[room].remove(name_to_leave)
									conn.send("You have lefted " + message)
									print name_to_leave + " has left " + message
								else:
									conn.send("You are not in that room. Can't leave. ")
						leave_label = 0
					elif leave_label == 1:
						name_to_leave = message
						leave_label = 2
					elif message == "\leave\n":
						leave_label = 1

					# list members of a room
					elif member_label:
						for room in list_of_rooms:
							if room == message:
								conn.send(room + ": ")
								for user in list_of_rooms[room]:
									conn.send(user)
						member_label = False

					elif message == "\memberlist\n":
						member_label = True

					# send a message to the selected room
					elif select_label == 1:
						select_room = message
						select_label = 2
					elif select_label == 2:
						selectcast(conn_to_name(conn)+'>', select_room, conn)
						selectcast(message, select_room, conn)
						select_label = 0

					elif message == "\selectroom\n":
						select_label = 1

					# disconnect to the server
					elif quit_label:
						remove_con(conn, message)
						quit_label = False

					elif message == "\quit\n":
						quit_label = True

					# display the name of the client before send the message
					elif socket_label:
                                                #print "socket_label " + str(socket_label)
						current_user = message
						message = message+'> '
						message_to_send = message
						broadcast(message_to_send, conn, current_user)
						socket_label = False
				
                                        # send the message
					else:
						message_to_send = message
						broadcast(message_to_send, conn, current_user)
						socket_label = True


				else:
					"""Nothing to do"""


			except:
				continue
"""
This function helps find the user name depending on its socket connection.
"""
def conn_to_name(connection):
	if connection in client_conn:
		return client_name[client_conn.index(connection)]
	else:
		return "conn_to_name error"

"""
        Using this function, we send the message to the selected room.
	message: the message to send
	roomname: the name of selected room
	conn: the connection of sender
"""
def selectcast(message, roomname, conn):
	if roomname in list_of_rooms:
		for name in list_of_rooms[roomname]:
				client_conn[client_name.index(name)].send(conn_to_name(conn) + '> ')
				client_conn[client_name.index(name)].send(message)
	else:
		conn.send("Room name doesn't exist")


"""
        Using the function, we broadcast the message to all clients who's in the same room as the sender except the sender.
	message: the message to send
	connection: the connection of sender
	name: the name of the sender
 """
def broadcast(message, connection, name):
	client_to_send = []
	for room in list_of_rooms:
		if name in list_of_rooms[room]:
			for i in list_of_rooms[room]:
				if i not in client_to_send:
					client_to_send.append(i)
	for client in client_to_send:
			try:
				if client_conn[client_name.index(client)] is not connection:
					client_conn[client_name.index(client)].send(message)
			except:
				client_conn[client_name.index(client)].close()
				# if the link is broken, we remove the client
				remove_con(client_conn[client_name.index(client)], client)

"""The following function simply removes the object 
from the list that was created at the beginning of 
the program"""
def remove_con(connection, name):
	for room in list_of_rooms:
		for i in list_of_rooms[room]:
			if i == name:
				list_of_rooms[room].remove(name)
	if connection in client_conn:
		client_conn.remove(connection)
	if name in client_name:
		client_name.remove(name)
		print name + "has disconnected."
	else:
		sys.stdout.write("There's no " + name + " to remove.")

try:
	while True:

		"""Accepts a connection request and stores two parameters, 
		conn which is a socket object for that user, and addr 
		which contains the IP address of the client that just 
		connected"""
                    
		conn, addr = server.accept()

		# creates and individual thread for every user
		# that connects
		start_new_thread(clientthread,(conn,addr))


	conn.close()
	server.close()
except:
	# server crash handling
	print "The server has been shut down."

