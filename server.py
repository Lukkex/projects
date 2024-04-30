'''
server.py (port number):
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
import errno
import threading

# Fixed size of 10; if all slots are filled, do not allow new clients to register
userRegistry = []

def setRegistry(newReg):
    userRegistry = newReg

# Returns 1 if username in use
# returns 2 if username is available
# returns 0 if registry full
def join(clientSocket, clientAddress, username):
    try:
        if (len(userRegistry) < 10):
            i = 0
            # Checks if username is already in use
            for users in userRegistry:
                if (userRegistry[i][1][1] == username):
                    return 1
                i += 1
            userRegistry.append((clientSocket, (clientAddress, username)))
            return 2
        return 0
    except Exception as e:
        print("Error: " + str(e))

# Will return true if member is within the registry
# Will return false if member is not in the registry
def checkIfMember(clientAddress):
    try:
        if (len(userRegistry) > 0):
            # Separates tuple into list of all addresses and usernames
            regSockets, userTuples = zip(*userRegistry)
            regAddresses, regUsernames = zip(*userTuples)

            for i in regAddresses:
                if (i == clientAddress):
                    return True
            return False
        else:
            return False
    except Exception as e:
        print("Error: " + str(e)) 

# Handles how to dispatch types of messages
# returns 0 if broadcasting to everyone except sender
# returns 1 if broadcasting to everyone including sender
# returns 2 if broadcasting to a single member
def serverMessageHandler(targSocket, message, type):
    try:
        if (len(userRegistry) > 0):
            # Separates tuple into list of all addresses and usernames
            regSockets, userTuples = zip(*userRegistry)
            # for broadcasts - sender
            if(type == 0):
                for socket in regSockets:
                    if (socket != targSocket):
                        socket.send(message.encode())
            # for broadcasts (everyone)
            if(type == 1):
                for socket in regSockets:
                    socket.send(message.encode())
            # for direct messages
            if(type == 2):
                for socket in regSockets:
                    if (socket == targSocket):
                        socket.send(message.encode())
            return True
        else:
            return False


    except Exception as e:
        print("Error: " + str(e))

# returns name of user in (clientSocket)
def getUsername(clientSocket):
    try:
        if (len(userRegistry) > 0):
            
            regSockets, userTuples = zip(*userRegistry)
            regAddresses, regUsernames = zip(*userTuples)
            i = 0
            for socket in regSockets:
                if (socket == clientSocket):
                    return regUsernames[i]
                i += 1

    except Exception as e:
        print("Error: " + str(e))
    
    return None

# Removes user assiciated with (clientSocket) from registry
def removeUser(clientSocket):
    try:
        if (len(userRegistry) > 0):
            # Separates tuple into list of all addresses and usernames
            regSockets, userTuples = zip(*userRegistry)
            i = 0
            for socket in regSockets:
                if (socket == clientSocket):
                    clientTuple = userRegistry[i]
                i += 1

    except Exception as e:
        print("Error: " + str(e))
    
    userRegistry.remove(clientTuple)
    # setRegistry(newReg)
    print('Removed user from list!')
    return True

# Bulk handling of client interaction
# contains implementation of client commands, timeout due to disconnect, and data management
def handleClientConnection(clientSocket, clientAddress):
    hasJoined = False
    while True:
        try:
            clientSocket.settimeout(300)
            data = clientSocket.recv(1024).decode('utf-8')

            if data:
                print('Received from ' + str(clientAddress) + ': ' + data)

                # Splits data/command by spaces
                data_tokens = data.split()

                # JOIN COMMAND
                if (data_tokens[0] == 'JOIN'):
                    if (len(data_tokens) == 2):
                        # Makes sure client isn't already a member
                        if (checkIfMember(clientAddress)):
                            clientSocket.send('You\'re already a member!\n'.encode())
                        # Assumes username is alphanumeric
                        # Checks if there is room for user to join
                        else:
                            joinResult = join(clientSocket, clientAddress, data_tokens[1])
                            if (joinResult == 2):
                                clientSocket.send('Successfully joined! Enjoy!\n'.encode())
                                print(str(data_tokens[1] + " joined!"))
                                serverMessageHandler(clientSocket, str(data_tokens[1]) + ' joined!', 0)
                                hasJoined = True
                            elif (joinResult == 1):
                                clientSocket.send('That username is already in use!\n'.encode())
                            else:
                                clientSocket.send('Too many users in registry, try again later!\n'.encode())
                        
                    else:
                        clientSocket.send('Invalid number of arguments for JOIN. Try: \'JOIN <username>\'\n'.encode())
            
                # LIST COMMAND
                elif (data_tokens[0] == 'LIST'):
                    if (hasJoined):
                        #userList = str(regToString(userRegistry))
                        listStr = 'Connected users: '
                        i = 0
                        for users in userRegistry:
                            listStr = listStr + str(userRegistry[i][1][1]) + ', '
                            i += 1
                        listStr = listStr[:-2] + "\n"
                    
                        clientSocket.send(listStr.encode())
                        #print('Sent list!')    
                    else:
                        clientSocket.send('You\'re not registered yet!\n'.encode()) 
                
                # BCST COMMAND
                elif(data_tokens[0] == 'BCST'):
                    # checks if user is joined and if their usage is correct with error checking
                    if (hasJoined):
                        if (len(data_tokens) > 1):
                            # removes fluff at beginning of message
                            data_tokens.remove(data_tokens[0])
                            broadcastmsg = ' '.join(data_tokens)
                            # Noitifies user they are sending a broadcast and calls serverMessageHandler to broadcast
                            try:
                                userName = getUsername(clientSocket)
                                clientSocket.send((str(userName) + ' is sending a broadcast!\n').encode())
                                serverMessageHandler(clientSocket, str(userName) + ': ' + str(broadcastmsg), 1)
                            except Exception as e:
                                print("Error: " + str(e))
                        else:
                            clientSocket.send('Message cannot be empty!\n'.encode())
                    else:
                        clientSocket.send('You\'re not registered yet!\n'.encode())
                
                # MESG COMMAND
                # checks if user is joined and if their usage is correct with error checking
                elif(data_tokens[0] == 'MESG'):
                    if (hasJoined):
                        if (len(data_tokens) <= 1):
                            clientSocket.send('Invalid syntax.\n\nMESG <username> <message>\n'.encode())                       
                        else:
                            # removes fluff at beginning of message while storing target
                            target = str(data_tokens[1])

                            userExists = False
                            j = 0
                            for users in userRegistry:
                                if (userRegistry[j][1][1] == target):
                                    userExists = True
                                j += 1

                            if (userExists):
                                data_tokens.remove(data_tokens[1])
                                data_tokens.remove(data_tokens[0])
                                message = ' '.join(data_tokens)
                                # gets username of current socket, and then sends message to target socket
                                try:
                                    if (len(userRegistry) > 0):
                                        i = 0
                                        j = 0
                                        for users in userRegistry:
                                            if (userRegistry[i][0] == clientSocket):
                                                userName = userRegistry[i][1][1]
                                            i += 1
                                        for users in userRegistry:
                                            if (userRegistry[j][1][1] == target):
                                                targetSocket = userRegistry[j][0]
                                                if(targetSocket == clientSocket):
                                                    clientSocket.send('You cannot send a message to yourself!\n'.encode())
                                                else:
                                                    serverMessageHandler(targetSocket, str(userName) + ' (private): ' + str(message), 2)
                                            j += 1
                                except Exception as e:
                                    print("Error: " + str(e))
                            else:
                                clientSocket.send('Unknown user!\n'.encode())    
                    else:
                        clientSocket.send('You\'re not registered yet!\n'.encode()) 

                # QUIT COMMAND
                # checks if user is joined and if their usage is correct with error checking
                # calls removeUser to remove user from the userRegistry, and gracefully closes socket connection
                elif (data_tokens[0] == 'QUIT'):
                    if (hasJoined):
                        username = getUsername(clientSocket) 
                        serverMessageHandler(clientSocket, username + ' left.', 0)
                        serverMessageHandler(clientSocket, username + ' is quitting the chat server.', 2)
                        print(username + ' has left the server.')
                        removeUser(clientSocket)
                    clientSocket.send('QUIT'.encode())
                    clientSocket.close()
                    return

                # HELP COMMAND
                # Prints usage
                elif (data_tokens[0] == 'HELP'):
                    if (hasJoined):
                        clientSocket.send('Please use one of the following:\nJOIN <username>\nLIST\nMESG <recipient> <message>\nBCST <message>\nHELP\nQUIT\n'.encode())
                    else:
                        clientSocket.send('Please use one of the following:\nJOIN <username>\nHELP\nQUIT\n'.encode())
                
                # Otherwise
                # Prints usage in case of incorrect usage
                else:
                    if (hasJoined):
                        clientSocket.send('Invalid command. Please use one of the following:\nJOIN <username>\nLIST\nMESG <recipient> <message>\nBCST <message>\nHELP\nQUIT\n'.encode())
                    else:
                        clientSocket.send('Invalid command. Please use one of the following:\nJOIN <username>\nHELP\nQUIT\n'.encode())
                #clientSocket.send('PONG!'.encode())
        
        except timeout:
            print("Connection with " + str(clientAddress) + " timed out.")
            break

        except Exception as e:
            pass

        '''
        except IOError as e:
            if e.errno == errno.EPIPE:
                print("Pipe Error: " + str(e))
        '''
    
    try:
        clientSocket.send('Connection timed out, please rejoin. \n(You took too long to send another message!)'.encode())
        clientSocket.close()
    except Exception as e:
        pass
    removeUser(clientSocket)
       
# If the amount of arguments is anything other than 2, 
# it will say in the console an invalid number of args and  kill the process.
if (len(sys.argv) != 2):
    print('Invalid number of arguments. Correct usage: python server.py <port>')
    quit()

# Takes in the server port and creates a TCP socket on the server end
serverPort = sys.argv[1]
serverSocket = socket(AF_INET, SOCK_STREAM)
host = '0.0.0.0'
try:
    serverSocket.bind((host, int(serverPort)))
    serverSocket.listen(5)
except Exception as e:
    print('Error establishing server socket, please make sure the port # is valid and open!')
    quit()

# Once the socket is setup, the server prints that it is ready to receive messages
print(f'The server is ready! \nListening on {host}:{serverPort}')

# Loop that continues until terminated manually, continuously listens for any incoming connection requests from clients. 
while True:
    try:
        clientSocket, clientAddress = serverSocket.accept()
        print(f'Connection from {clientAddress}')
        t = threading.Thread(target=handleClientConnection, args=(clientSocket, clientAddress,))
        t.start()
    except Exception as e:
        print("Error: " + str(e))
serverSocket.close()