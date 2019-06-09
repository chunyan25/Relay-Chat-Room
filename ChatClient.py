# CS594 final project
# Daniel Lee & Chunyan Bao
# Socket implementing multiple clients chatroom using python
# -- Client Side Code --

import socket
import select
import sys
import time
"""
check the usage first and then build up the connection
"""
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
if len(sys.argv) != 3:
	print "Correct usage: script, IP address, port number"
	exit()
IP_address = str(sys.argv[1])
Port = int(sys.argv[2])
server.connect((IP_address, Port))

# Send the user name to the server for user information management
print "Please enter your name."
user_name = sys.stdin.readline()
server.send("name_coming")
time.sleep(0.5)
server.send(user_name)
socket_label = True
try:
	while True:

		# maintains a list of possible input streams
		sockets_list = [sys.stdin, server]

		""" There are three possible input situations. One is the 
		user wants to give manual input to send to other people, 
		the server is sending a message to be printed on the 
		screen, or the user give command to the server for expected
		return. Select returns from sockets_list, the stream that 
		is reader for input. So for example, if the server wants 
		to send a message, then the if condition will hold true 
		below. If the user wants to send a message, the else 
		condition will evaluate as true"""
		read_sockets, write_socket, error_socket = select.select(sockets_list,[],[])

		for socks in read_sockets:
			# the message for other user, print the user name of sender and then the message
			if socks == server:
				if(socket_label):
					message = socks.recv(2048)
					print message
					socket_label = False
				else:
					message = socks.recv(2048)
					print message
					socket_label =True
			else:
				# input the message and recognize it if it is a command
				message = sys.stdin.readline()
				# list all rooms
				if message == "\listroom\n":
					server.send(message)
				# send a message to the selected room
				elif message == "\selectroom\n":
					server.send(message)
					time.sleep(0.5)
					to_select = raw_input("Which room do you want to send message?")
					server.send(to_select)
					time.sleep(0.5)
					to_say = raw_input("What do you want to say?")
					server.send(to_say)
				# send private message
				elif message == "\private\n":
					server.send(message)
					time.sleep(0.5)
					to_whom = raw_input("Who are you sending?")
					server.send(to_whom)
					time.sleep(0.5)
					to_say = raw_input("What do you want to say?")
					server.send(to_say)
				# disconnect with the server
				elif message == "\quit\n":
					server.send(message)
					time.sleep(0.5)
					server.send(user_name)
					time.sleep(0.5)
					server.close()
				# create a new room 
                                elif message == "\create\n":
					server.send(message)
				# list all rooms with the user in it
				elif message == "\printall\n":
					server.send(message)
				# list all user in a specific room
				elif message == "\memberlist\n":
					server.send(message)
					time.sleep(0.5)
					to_list = raw_input("Which room do you want to display?")
					server.send(to_list)
				# leave a room
				elif message == "\leave\n":
					server.send(message)
					time.sleep(0.5)
					server.send(user_name)
					to_leave = raw_input("Which room do you want to leave?")
					time.sleep(0.5)
					server.send(to_leave)

				# join a room
				elif message == "\join\n":
					server.send(message)
					time.sleep(0.5)
					server.send(user_name)
					to_join = raw_input("Which room do you want to join?")
					time.sleep(0.5)
					server.send(to_join)
				# help function
				elif message == "\help\n" or message == "\?\n":
					server.send(message)
				# send message to all the users who is in the same room
				else:
					server.send(user_name)
					sys.stdout.write("%s> " % user_name)
					time.sleep(0.5)
					server.send(message)
					sys.stdout.write(message)
					sys.stdout.flush()
except:
	print "The client has disconnected from the server."
server.close()

