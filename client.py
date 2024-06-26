'''
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
import sys
import time
import threading

message = ''

def listenForServer(clientSocket):
    keepListening = True
    while keepListening:
        try:
            serverMessage = clientSocket.recv(1024).decode('utf-8')
            if (serverMessage == 'QUIT'):
                print('\n\nEnter any key to quit the program.')
                keepListening = False
            elif (serverMessage is not None and serverMessage != ""):
                print(f'\b\b{serverMessage}', end='\n> ')
                if (serverMessage == 'Connection timed out, please rejoin. \n(You took too long to send another message!)'):
                    print('\n\nEnter any key to quit the program.')
                    keepListening = False

        except Exception as e:
            pass

    try:
        clientSocket.close()
    except Exception as e:
        pass

    return

# If the number of arguments are not 3, terminate the process
if (len(sys.argv) != 3):
    print('Invalid number of arguments. Correct usage: python client.py <server> <port>')
    quit()

# Takes in the server name and port and creates the client socket
serverName = sys.argv[1]
serverPort = int(sys.argv[2])
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.settimeout(5)
try:
    clientSocket.connect((serverName, serverPort))
    print("Connection established! \n\nEnter JOIN <username> to join the chatroom.\n")
except Exception as e:
    print(f"Could not establish a connection with the host. Error: {e}")
    quit()

t = threading.Thread(target=listenForServer, args=(clientSocket,))
t.start()

while True:
    try:
        message = input('> ')
        clientSocket.send(message.encode('utf-8'))
        clientSocket.settimeout(300)
    except Exception as e:
        break
quit()
    
