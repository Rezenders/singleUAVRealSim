import socket
import os
import sys
import time
import select
import re
import math
from ESP import ESP

ESPPORT = '/dev/ttyUSB1'

####methods####
def decodeSock(msg, port):
    if port == JAVAPORT:
        return msg[:-1]
    else: return msg

def encodeSock(msg, port):
    if port == JAVAPORT:
        return msg + '\n'
    else: return msg

####variable initialization####
sockList = [] #sockets accepted
lastTime = time.time()
newConnection = ''

####Application####
#setup ESP
esp = ESP(ESPPORT)

while True:
    #serial messages
    mail = esp.read()
    print('Received: ' + mail)

    time.sleep(0.02)
