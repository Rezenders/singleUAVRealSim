import socket
import os
import sys
import time
import select
import re
import math
from ESP import ESP
#MAVLINK RELATED IMPORTS
from dronekit import *

#SERVER
####constants####
JAVAPORT = 6969
DRONEPORT = '127.0.0.1:14550' #environment simulation
#POSSIBLE DRONEPORTS:
## '127.0.0.1:14550' #environment simulation PC-PC
## '192.168.7.2:14550' #environment simulation Beagle-PC
## '/dev/ttyACM0' #real application via USB Beagle-PixHawk
## '/dev/ttyO4' #real application via serial Beagle-PixHawk.
### Requires baud-rate 57600
ESPPORT = '/dev/ttyUSB0'

MIN_DISTANCE = 0.5 #minimum distance to consider as change in position
MIN_ALT = 5
R = 6371; # Radius of the earth

####methods####
def decodeSock(msg, port):
    if port == JAVAPORT:
        return msg[:-1]
    if port == DRONEPORT:
        return re.split('\)',msg)[-2]+')' #get only the last term
    else: return msg

def encodeSock(msg, port):
    if port == JAVAPORT:
        return msg + '\n'
    else: return msg

def createSocket(TCP_PORT):
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #serverSocket.setblocking(0)
    serverSocket.bind(('localhost', TCP_PORT))
    serverSocket.listen(5)

    return serverSocket

def buildPercept():
    percept = 'pos('+str(pos[0])+ ',' +str(pos[1])+ ',' +str(pos[2])+');' + \
                'status('+status+');'
    return percept

def sendTo(port, sList, msg): #sendTo(port socket to send, list of sockets, message)
    for s in sList:
        if port in s.getsockname():
            s.sendall(encodeSock(msg,port))

####variable initialization####
localPorts = [JAVAPORT]
sockList = [] #sockets accepted
lastTime = time.time()
ag_name = ''
newConnection = ''
espConnections = {}

####System state variables####
pos = [0, 0, 0]
status = 'Ready'

####Application####
#setup ESP
#esp = ESP(ESPPORT)

#Connect to all sub-systems (sockets) before anything
for p in localPorts:
    sock = createSocket(p)
    clientSock, address = sock.accept()
    sockList.append(clientSock)

#setup VANT
# copter = connect(DRONEPORT, wait_ready=True) #if ttyO4, set baud=57600
# copter.mode = VehicleMode("GUIDED")
# while not copter.armed:
#     copter.armed= True
#     print(" Waiting for arming...")
#     time.sleep(5)

#initial position
#initial_pos = [float(copter.location.global_relative_frame.lon), float(copter.location.global_relative_frame.lat), float(copter.location.global_relative_frame.alt)]

while True:
    #Check which sockets are readable or writable
    readable, writable, exceptional = select.select(sockList, sockList, sockList, 0.1)

    #percepts update
    if(time.time()-lastTime > 1): #send percepts every second
        lastTime = time.time()
        percept = buildPercept()
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
                        #copter.simple_takeoff(MIN_ALT)

                    if 'land' in decodeData:
                        print('landing')
                        #copter.mode  = VehicleMode("RTL")

                    if 'setWaypoint' in decodeData:
                        print('setting wp')
                        #_, latwp, lonwp, altwp, _ = re.split('\(|\)|,', decodeData)
                        #wp = LocationGlobalRelative(-30,150,20)
                        #wp = LocationGlobalRelative(float(latwp), float(lonwp), float(altwp))
                        #print(wp)
                        #print(pos)
                        #copter.simple_goto(wp)
                if '*' in decodeData:
                    print('sending msg')
                    print(decodeData)
                    #destination = re.split('\[|\]|,', decodeData)[1]
                    #message = decodeData(len('send(['+destination+'], '))[:-1]
                    #esp.send(destination+';'+message)

                    #if 'register_name' in decodeData:
                    #    _, name, _, = re.split('\(|\)|,', decodeData)
                    #    ag_name = name
                    #    print('this agent\'s name is: ' + ag_name)

                    #send confirmation to the Agent
                    #sendTo(JAVAPORT,writable,encodeSock(decodeData,JAVAPORT))

    #latitude and longitude are global. Altitude is relative to the ground
    # lat, lon, alt =  float(copter.location.global_relative_frame.lat), float(copter.location.global_relative_frame.lon), float(copter.location.global_relative_frame.alt)
    # latDistance = math.radians(lat-pos[0])
    # lonDistance = math.radians(lon-pos[1])
    # height = alt - pos[2]
    #
    # a = math.sin(latDistance / 2) * math.sin(latDistance / 2) + math.cos(math.radians(lat)) * math.cos(math.radians(pos[0])) * math.sin(lonDistance / 2) * math.sin(lonDistance / 2)
    #
    # distance = R * 1000 * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    #
    # distance = math.sqrt(math.pow(distance, 2) + math.pow(height, 2));
    #
    # if distance>MIN_DISTANCE :
    #     pos = [lat,lon,alt] #update position
    #
    # if copter.armed:
    #     if float(copter.location.global_relative_frame.alt) > MIN_ALT*0.95 :
    #         status = 'flying'
    #     else:
    #         status = 'ready' #update status
    # else:
    #     status = 'notReady'

    #serial messages
    #mail = esp.read()

    #if 'connected:' in mail:
    #     connectionID, _, connectionName = re.split(':|;',mail)
    #     espConnections.update({connectionID : connectionName})
    #
    # else:
    #     newConnection = ''
    #     mail = mail[mail.find(';')+1 :]
    #     sendTo(JAVAPORT,writable,encodeSock(mail))

    #else:
        #s.close()
        #if s in sockList:
            #sockList.remove(s)

    time.sleep(0.02)
#copter.close()
