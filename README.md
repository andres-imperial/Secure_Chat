# Secure Chat
Secure Chat offers an implemention of a multi-user secure chat program that used RSA and AES encryption with a single multi-threaded server.

### Instructions on how to run the code:
+ Download/Clone Secure chat repo
+ In terminal1
  `cd server`
+ Start the server:
  `python chat-server.py <port#>`
+ In terminal2
  `cd client`
+ Start the client:
  `python chat-client.py <server addr> <port#>`


### Other information:
Usernames and passwords:  
alice:wonderland  
bob:the builder  
darth:maul

### Introduction:
My program allows multiple users to connect to a server and provides secure chat encryption while hiding the complexity of encryption and socket communication. There are also user authentication in order to login into the server, and chat session based on invitation only. The only exception to the invitation only chat is if you are the first user creating the chat. There is also a method to query who is currently online and who is currently in the chat room.

### Design:
The design of my program is based on client and server interaction. My server will be started and begin to wait for client to join a connection(up to five clients). My server will then start a thread to take the client through the login and authentication process, along with setting up/joining a chat session. The client on the other hand starts off joining the server and once the client has logged in and joined a session the client program starts a thread for receiving and displaying messages only, while the main program handles sending data to the server. 

### Security Protocols:
I wanted to provide secure communication using symmetric encryption, AES encryption to be particular. I used RSA public key encryption in order to distribute the symmetric session keys to each user.  
AES is used for confidentiality in sending chat messages over the socket connection. I use the system in order to create a random 16 byte key for AES encryption. I then send this key to all invited user to the chat. But before I send the key and I take the user’s public key and encrypt it to provide confidentiality when send the session over the socket connection. The Client then is able to decrpyt the session key using their private key. They will now use this key in order to send messages to the server and the server will distribute this message to all other users in the chat.

### Implementation:
For the programming language I chose python for its easy data manipulation and simple libraries. Some of the libraries I used are:
+ import sys, os , random – for output, number generation, file I/O
+ import socket – for socket communication
+ import thread – for multi threading
+ from Crypto.Cipher import AES – for AES encryption
+ from Crypto.PublicKey import RSA – for RSA/public key encryption
+ from base64 import b64encode, b64decode – for encoding messages to a predictable format/no 	spaces
