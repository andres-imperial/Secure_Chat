import sys
import os
import socket

def connect(addr, port):
    # Create a TCP socket
    connSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print "attempting to connect"
    # Connect to the server
    connSock.connect((addr, port))
    print "connected"
    return connSock

def createConnect(commandSock):
    # Create a socket
    newSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Bind the socket to port 0
    newSock.bind(('',0))
    connPortStr = str(newSock.getsockname()[1])
    # Prepend 0's to the size string until the size is 10 bytes
    while len(connPortStr) < 10:
        connPortStr = "0" + connPortStr
    # Send dataPort to which client should connect to for data
    sendCommand(connPortStr, commandSock)
    newSock.listen(1)
    print "Data socket waiting for connection"
    connSock, addr = newSock.accept()
    print "Data socket connected ", addr
    return connSock

def receive(sock):
    # The buffer to all command received from the the client.
	command = ""
	# The temporary buffer to store the received
	# command.
	recvBuff = ""
	# The size of the incoming file
	commandSize = 0
	# The buffer containing the file size
	commandSizeBuff = ""
	# Receive the first 10 bytes indicating the size of the command
	commandSizeBuff = recvAll(sock, 10)
	# Get the command size
	commandSize = int(commandSizeBuff)
	# Get the command
	return recvAll(sock, commandSize)


def sendFile(fileName, sock):
	# Open the file
	fileObj = open(fileName, "r")
	# The number of bytes sent
	numSent = 0
	# The file data
	fileData = None
	# Keep sending until all is sent
	while True:
		# Read 65536 bytes of data
		fileData = fileObj.read(65536)
		# Make sure we did not hit EOF
		if fileData:
			# Get the size of the data read
			# and convert it to string
			dataSizeStr = str(len(fileData))
			# Prepend 0's to the size string
			# until the size is 10 bytes
			while len(dataSizeStr) < 10:
				dataSizeStr = "0" + dataSizeStr
			# Prepend the size of the data to the
			# file data.
			fileData = dataSizeStr + fileData
			# The number of bytes sent
			numSent = 0
			# Send the data!
			while len(fileData) > numSent:
				numSent += sock.send(fileData[numSent:])
		# The file has been read. We are done
		else:
			break

	fileObj.close()
	print "Sent file:", fileName, " with # of bytes sent:", numSent

def recvAll(sock, numBytes):
	# The buffer
	recvBuff = ""
	# The temporary buffer
	tmpBuff = ""
	# Keep receiving till all is received
	while len(recvBuff) < numBytes:
		# Attempt to receive bytes
		tmpBuff =  sock.recv(numBytes)
		# The other side has closed the socket
		if not tmpBuff:
			break
		# Add the received bytes to the buffer
		recvBuff += tmpBuff
	return recvBuff

def sendCommand(command, commandSock):
	# The command size
	commandSize = len(command)
	# Get the size of the command and convert it to string
	commandSizeStr = str(commandSize)
	# Prepend 0's to the size string until the size is 10 bytes
	while len(commandSizeStr) < 10:
		commandSizeStr = "0" + commandSizeStr
	# Prepend size of command to the command
	command = commandSizeStr + command
	# The number of bytes sent
	numSent = 0
	# Send the data!
	while commandSize > numSent:
		numSent += commandSock.send(command[numSent:])
