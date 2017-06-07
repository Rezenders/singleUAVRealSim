import socket
import os
import sys
import time
import select
import re
import math
#MAVLINK RELATED IMPORTS
from dronekit import *

#SERVER
####constants####
JAVAPORT = 6969
SIMPORT = '127.0.0.1:14550' #environment simulation
min_distance = 0.1 #minimum distance to consider as change in position
default_altitude = 50

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
localPorts = [JAVAPORT]
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

#setup VANT
copter = connect(SIMPORT, wait_ready=True)
while not copter.is_armable:
    print(" Waiting for copter to initialise...")
    time.sleep(1)
copter.mode = VehicleMode("GUIDED")
copter.armed= True
while not copter.armed:
    print(" Waiting for arming...")
    time.sleep(1)

#initial position
pos = [float(copter.location.global_frame.lon), float(copter.location.global_frame.lat), float(copter.location.global_frame.alt)]

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
                        print('launching')
                        copter.simple_takeoff(default_altitude)
                    if 'land' in decodeData:
                        print('landing')
                    if 'setWaypoint' in decodeData:
                        _, x, y, z, _ = re.split('\(|\)|,', decodeData)
                        print('setting wp to (' + x +', ' + y + ', ' + z + ')')

                    #send confirmation to the Agent
                    sendTo(JAVAPORT,writable,encodeSock(decodeData,JAVAPORT))

    x, y, z = float(copter.location.global_frame.lon), float(copter.location.global_frame.lat), float(copter.location.global_frame.alt)
    if (math.sqrt(math.pow(x-pos[0],2) + math.pow(y-pos[1],2) + math.pow(z-pos[2],2)))>min_distance :
        pos = [x,y,z] #update position

    if copter.armed:
        status = 'ready' #update status

    #else:
        #s.close()
        #if s in sockList:
            #sockList.remove(s)
copter.close()
