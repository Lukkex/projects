'''
Server.py (port number):
    Start on specified port, TCP socket
    When connects to client, create new thread to handle (POSIX)
    If >10 users registered, send to client “Too many users!” and close connection
    If already registered, discard new JOIN requests and send status back to client
    If command sent that the server doesn’t recognize, send to client “Unknown Command”
    Server will provide updates in terminal on messages sent/received, requests, ID clients by IP and port #
    Show to all clients who joins chatroom and who leaves
    Error checking is thorough

Client.py (hostname) (port number):
    Connect to server on specified port
    JOIN (username) – (15 points)
        Sends JOIN request w/ alphanumeric username, no spaces / special chars
        Username validation not needed
        NO other services provided unless registered through JOIN
    LIST – (15 points)
        Server will send list of all currently registered clients on individual lines (\n’s)
    MESG (username) (message) – (15 points)
        Messages user using server as a relay in between
        If user sending message isn’t registered, have server send status saying they’re not registered and to join w/ JOIN instructions
        If receiving end user is not registered, send to client “Unknown recipient”
    BCST (message) – (15 points)
        If client is registered, broadcast this message to all other users (not the sender)
    QUIT – (10 points)
        Client disconnects and server removes them from the database of registered users; unregistered users can do this too but it won’t remove any data
'''
# Hunter Brown, Connor Yep, William Lorence
# Prof. Badruddoja 
# CSC 138-04
# 17 Apr. 2024

from socket import *
import random
import sys
import threading

def handleClientConnection(clientSocket):
    data = clientSocket.recv(1024).decode('utf-8')

    if data:
        print('Received from ' + str(clientAddress) + ': ' + data.decode())
        serverSocket.sendto('PONG!'.encode(), clientAddress)
       
# If the amount of arguments is anything other than 2, 
# it will say in the console an invalid number of args and  kill the process.
if (len(sys.argv) != 2):
    print('Invalid number of arguments.')
    quit()

# Takes in the server port and creates a TCP socket on the server end
serverPort = sys.argv[1]
serverSocket = socket(AF_INET, SOCK_STREAM)
host = '0.0.0.0'
serverSocket.bind((host, int(serverPort)))
serverSocket.listen(5)

# Once the socket is setup, the server prints that it is ready to receive messages
print(f'The server is ready! \nListening on {host}:{serverPort}')

# Loop that continues until terminated manually, continuously listens for any incoming messages from clients. 
while True:
    clientSocket, clientAddress = serverSocket.accept()
    print(f'Connection from {clientAddress}')
    t = threading.Thread(target=handleClientConnection, args=(clientSocket,))
    t.start()
    #t.join()
serverSocket.close()
    
