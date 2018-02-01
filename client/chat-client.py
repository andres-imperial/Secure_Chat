import socket
import os
import sys
import sock
import thread
import time
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from base64 import b64decode, b64encode

username = ""
quit = False

def chatThread(chatSock, symmKey):
	global quit
	while True:
		# Create new AES object
		aesObj = AES.new(symmKey, AES.MODE_CFB, 'cpsc 452 rules!!')
		# Receive servers messge and decode and display
		ciphertext = sock.receive(chatSock)
		plaintext = aesObj.decrypt(b64decode(ciphertext))
		if plaintext == 'QUIT':
			chatSock.close()
			quit = True
			return 0
		elif plaintext == "online status":
			print "statuses"
		else:
			print "\t\t\t\t", plaintext

def main():
	# Command line checks
	if len(sys.argv) != 3:
		print "USAGE:python " + sys.argv[0] + "<servermachine> <serverport>"
	# Server address
	serverAddr = sys.argv[1]
	# Server port
	serverPort = int(sys.argv[2])
	# Create a TCP socket
	chatSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	# Connect to the server
	chatSock.connect((serverAddr, serverPort))

	# We have connected now let the client issue commands:
	while True:
		# Receive server's reply
		serverReply = sock.receive(chatSock)
		# If it is the key then initiate chat sequence
		if serverReply.split()[0] == 'KEY':
			cipherSymmKey = b64decode(serverReply.split()[1])
			# Import users private key
			with open(username + "-private-key.txt", 'r') as iFile:
				key = RSA.importKey(iFile.read(),)
			# decrypt symmetric key from server
			symmKey = key.decrypt(cipherSymmKey)
			# Start new thread for recieving messages
			thread.start_new_thread(chatThread,(chatSock,symmKey))
			#Enter chat loop
			print "Begin Chat"
			while True:
				# Create new aes object
				aesObj = AES.new(symmKey, AES.MODE_CFB, 'cpsc 452 rules!!')
				# Read user's input
				userInput = raw_input("")
				# Check if user wants to quit
				if userInput == 'quit'or userInput == 'QUIT' or userInput == 'q':
					# Tell the server your quiting
					ciphertext = aesObj.encrypt("QUIT")
					ciphertext = b64encode(ciphertext)
					sock.sendCommand(ciphertext, chatSock)
					print "quiting . . . "
					while not quit:
						sys.stdout.write(".")
						time.sleep(.01)
					return 0
					#quit program/close socket
				else:
					# Encrypt input and encode to base 64
					ciphertext = aesObj.encrypt(userInput)
					ciphertext = b64encode(ciphertext)
					# Send ciphertext
					sock.sendCommand(ciphertext,chatSock)
		# Display only
		elif serverReply.split()[0] == "DISP":
			print serverReply[5:]
		# Check if command is the Invite sequence
		elif serverReply.split()[0] == 'INVITE':
			# Display server message
			sys.stdout.write(serverReply[7:])
			# Read user's input and send it to the server
			userInput = raw_input("")
			sock.sendCommand(userInput,chatSock)
		# Check if command is the Login sequence
		elif serverReply.split()[0] == 'LOGIN':
			# Display server message
			sys.stdout.write(serverReply[6:])
			# Read user's input and save their login name
			userInput = raw_input("")
			username = userInput
			# Send the server your login name
			sock.sendCommand(userInput,chatSock)
			# Display servers reply
			serverReply = sock.receive(chatSock)
			sys.stdout.write(serverReply)
			# Read user's password and send to server
			userInput = raw_input("")
			sock.sendCommand(userInput,chatSock)
		elif serverReply == 'QUIT':
			return 0;
		else:
			# Defualt case for reading server messages and replying
			sys.stdout.write(serverReply)
			userInput = raw_input("")
			sock.sendCommand(userInput,chatSock)

### Call the main function ####
if __name__ == "__main__":
	main()
