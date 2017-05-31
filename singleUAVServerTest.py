import socket
import os
import sys
import time
import select
import re
import math

#MAVLINK RELATED IMPORTS

#SERVER
####constants####
JAVAPORT = 6969
SIMPORT = 14550 #environment simulation
min_distance = 0.1 #minimum distance to consider as change in position

####methods####
def decodeSock(msg, port):
    if port == JAVAPORT:
        return msg[:-1] #JAVAPORT]
    if port == SIMPORT:
        return re.split('\)',msg)[-2]+')' #get only the last term
    else: return msg

def encodeSock(msg, port):
    if port == JAVAPORT:
        return msg + '\n' #JAVAPORT
    else: return msg

def createSocket(TCP_PORT):
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #serverSocket.setblocking(0)
    serverSocket.bind(('localhost', TCP_PORT))
    serverSocket.listen(5)

    return serverSocket

def buildPercept():
    percept = 'pos(' + str(pos[0]) + ',' + str(pos[1]) + ',' + str(pos[2]) + ');' + \
                'status(' + status + ')'
    return percept

def sendTo(port, sList, msg): #sendTo(port socket to send, list of sockets, message)
    for s in sList:
        if port in s.getsockname():
            s.sendall(encodeSock(msg,port))

####variable initialization####
localPorts = [SIMPORT, JAVAPORT]
sockList = [] #sockets accepted
lastTime = time.time()

####System state variables####
pos = [0, 0, 0]
status = 'notReady'

####Application####
#Connect to all sub-systems (sockets) before anything
for p in localPorts:
    sock = createSocket(p)
    clientSock, address = sock.accept()
    sockList.append(clientSock)

while True:
    #Check which sockets are readable or writable
    readable, writable, exceptional = select.select(sockList, sockList, sockList, 0.1)

    #percepts update
    if(time.time()-lastTime > 1): #send percepts every second
        lastTime = time.time()
        percept = buildPercept()
        print("SENDING PERCEPTS")
        sendTo(JAVAPORT,writable,encodeSock(percept,JAVAPORT))

    #Interpret received messages
    for s in readable: #for every socket object
        _, receivePort = s.getsockname(); #receivePort = port_number

        data = s.recv(1024)
        if data != '': #if it's not a null message
            decodeData = decodeSock(data, receivePort)

            if receivePort == JAVAPORT: #if it was received from the Agent
                if '!' in decodeData: #if it's and action
                    if 'launch' in decodeData:
                        MODE GUIDED
                        print('launching')

                    if 'land' in decodeData:
                        print('landing')

                    if 'setWaypoint' in decodeData:
                        _, x, y, z, _ = re.split('\(|\)|,', decodeData)
                        print('setting wp to (' + x +', ' + y + ', ' + z + ')')

                    #send command to flight-control-board
                    sendTo(SIMPORT,writable,encodeSock(decodeData,SIMPORT))
                    #send confirmation to the Agent
                    sendTo(JAVAPORT,writable,encodeSock(decodeData,JAVAPORT))

            if receivePort == SIMPORT:#if it was received from the flight-control-board
                if 'pos' in decodeData:
                    _, x, y, z, _ = re.split('\(|\)|,', decodeData)
                    #position percept filter
                    if math.sqrt(math.pow(float(x)-pos[0],2)+
                        math.pow(float(y)-pos[1],2)+
                        math.pow(float(z)-pos[2],2))>min_distance:
                        pos = [float(x),float(y),float(z)] #update position
                if 'status' in decodeData:
                    _, term, _ = re.split('\(|\)', decodeData)
                    status = term #update status

    #else:
        #s.close()
        #if s in sockList:
            #sockList.remove(s)
