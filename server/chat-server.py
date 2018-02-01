import sys, os , random
import socket
import sock
import thread
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from base64 import b64encode, b64decode

users = {'alice':'wonderland', 'bob':'the builder', 'darth':'maul'}
userStatus = {'alice':'offline', 'bob':'offline', 'darth':'offline'}
userSocket = {'alice':None, 'bob':None, 'darth':None}
userKey = {'alice':None, 'bob':None, 'darth':None}
userChatting = {'alice':False, 'bob':False, 'darth':False}
invited = []
flag = True
randomKey = ""

################################################################################
# Function to handle clients, brings them throught the login in process, invite
# process, sets their status, sets their socket, and imports their public RSA
# key.
################################################################################
def clientThread(clientSock):
	# Import global variables
	global flag
	global randomKey
	global invited
	# Start the login in process and Continue until they give valid credentials
	while True:
		# Get username and password from user
		sock.sendCommand("LOGIN Enter username:", clientSock)
		username = sock.receive(clientSock)
		sock.sendCommand("Enter password:", clientSock)
		password = sock.receive(clientSock)
		# Verify username and password
		if username in users:
			if users[username] == password:
				sock.sendCommand("Verified, would you like to enter the chat?", clientSock)
				print "verified"
				userStatus[username] = 'online'
				# Save the user's socket
				userSocket[username] = clientSock
				# If verified break from login loop
				break;
			else:
				# Invalid credentials
				sock.sendCommand("DISP Incorrect username or password\n", clientSock)
				print "verification failed"
		else:
			# Invalid credentials
			sock.sendCommand("DISP Incorrect username or password\n", clientSock)
			print "verification failed"

	# Ask if they want to go into the chat yet
	while True:
		reply = sock.receive(clientSock)
		if reply == 'yes' or reply == 'y':
			sock.sendCommand("INVITE List your invites to chat:", clientSock)
			break;
		elif reply == 'no' or reply == 'n':
			sock.sendCommand("would you like to join now???:", clientSock)
		else:
			sock.sendCommand("Please enter yes(y) or no(n):", clientSock)

	# Ask for invites and display online statuses to user
	invites = ""
	offline = ""
	online = ""
	invites = sock.receive(clientSock).split()
	for invite in invites:
		# Check if this user is the first one to start the chat
		if len(invited) == 0:
			invited.append(username)
		# Check if invited person is online
		if userStatus[invite] == 'offline':
			offline += invite + ", "
		else:
			if userChatting[invite] == False:
				sock.sendCommand("DISP " + username + " has invited you to chat!", userSocket[invite])
			online += invite + ", "
		# Only append invited user if they aren't on the list
		if not invite in invited and invite != username:
			invited.append(invite)
	# Notify client of who was online or not
	sock.sendCommand("DISP Offline:" + offline + "\nOnline:" + online + "\n",
	 				clientSock)

	# Create symmetric KEY if there is none
	if flag:
		randomKey = os.urandom(16)
		flag = False


	# If they are invited send them the key
	if username in invited:
		# Import users publickey
		with open(username + "-public-key.txt", 'r') as iFile:
			pubKey = RSA.importKey(iFile.read(),)
			# Encrypt key with users public key
			cipherKey = pubKey.encrypt(randomKey,random.randint(1,100))
		# Send key to client
		sock.sendCommand("KEY " + b64encode(cipherKey[0]), clientSock)
		userChatting[username] = True

	else:
		sock.sendCommand("DISP sorry your not invited to the current session", clientSock)
		sock.sendCommand("QUIT", clientSock)
		return 0

	# Continue to do chat stuff
	while True:
		# Create AES object
		aesObj = AES.new(randomKey, AES.MODE_CFB, 'cpsc 452 rules!!')
		# Recieve message from client
		ciphertext = sock.receive(clientSock)
		# Check if user is quiting
		plaintext = aesObj.decrypt(b64decode(ciphertext))
		if plaintext == "QUIT":
			# Set user to offline
			aesObj = AES.new(randomKey, AES.MODE_CFB, 'cpsc 452 rules!!')
			userChatting[username] = False
			userSocket[username] = None
			userStatus[username] = 'offline'
			quitMsg = aesObj.encrypt(username + " has left and is now offline.")
			quitMsg = b64encode(quitMsg)
			for user, socket in userSocket.iteritems():
				if socket and socket != clientSock:
					sock.sendCommand(quitMsg, socket)
			aesObj = AES.new(randomKey, AES.MODE_CFB, 'cpsc 452 rules!!')
			ciphertext = aesObj.encrypt("QUIT")
			ciphertext = b64encode(ciphertext)
			sock.sendCommand(ciphertext, clientSock)
			return 0
		# User asked who is online
		elif plaintext == "online":
			reply = "The following users are online:"
			for user, status in userStatus.iteritems():
				if status == "online":
					reply += " " + user

			aesObj = AES.new(randomKey, AES.MODE_CFB, 'cpsc 452 rules!!')
			ciphertext = aesObj.encrypt(reply)
			ciphertext = b64encode(ciphertext)
			sock.sendCommand(ciphertext, clientSock)
		# Invite users to current chat
		elif plaintext.split()[0] == 'invite':
			invites = plaintext.split()[1:]
			online = offline = ""
			for invite in invites:
				# Check if invited person is online
				if userStatus[invite] == 'offline':
					offline += invite + ", "
				else:
					if userChatting[invite] == False:
						sock.sendCommand("DISP " + username + " has invited you to chat!", userSocket[invite])
					online += invite + ", "
				# Only append invited user if they aren't on the list
				if not invite in invited and invite != username:
					invited.append(invite)
			# Notify client of who was online or not
			aesObj = AES.new(randomKey, AES.MODE_CFB, 'cpsc 452 rules!!')
			ciphertext = aesObj.encrypt("\nOffline:" + offline + "\nOnline:" + online + "\n")
			ciphertext = b64encode(ciphertext)
			sock.sendCommand(ciphertext, clientSock)
		else:
			# Send message to all online clients except the sender
			for user in invited:
				if userSocket[user] and userSocket[user] != clientSock and userChatting[user] == True:
					sock.sendCommand(ciphertext, userSocket[user])

def main():
	# Command line arguments error check
	if len(sys.argv) != 2:
		print "USAGE python " + sys.argv[0] + "<PORT NUMBER>"
	# The port on which to listen
	listenPort = int(sys.argv[1])
	# Create a welcome socket.
	commandSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	# Bind the socket to the port
	commandSock.bind(('', listenPort))
	# Start listening on the socket for up to 5 clients
	commandSock.listen(5)

	while True:
		print "Waiting for connections..."
		# Accept connection form client for a command line
		clientSock, addr = commandSock.accept()
		print "Accepted connection from client: ", addr
		# Start new thread to handle client
		thread.start_new_thread(clientThread,(clientSock,))


### Call the main function ####
if __name__ == "__main__":
	main()
