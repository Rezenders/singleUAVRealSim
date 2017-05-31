import socket
import sys
import time
import select
import math
import re
from matplotlib import pyplot

timeout = 0.1 #communication timeout
period = 0.3 #simulate every period
min_distance = 0.1 #minimum distance to trigger UAV movement towards wp
SIMPORT = 6970 #environment simulation

#dist(a,b) measures the euclidian distance between points a and b
def distance(a, b):
    d = 0
    for i in range(len(a)):
        d += math.pow(b[i]-a[i],2)
    return math.sqrt(d)


#Create TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#Connect the socket to SIMPORT
server_address = ('localhost', SIMPORT)
print >>sys.stderr, 'connecting to %s port %s' % server_address
sock.connect(server_address)
sock.setblocking(0)

speed = 0.2 #speed in m/s
position = [0,0,0] #initial position
std_altitute = 5 #standard altitude
status = 'ready' #initial status
waypoint = [0,0,0] #initial waypoint

#show plot
pyplot.axis([-1, 7, -1, 7])
pyplot.ion()
pyplot.show(block=False)
pyplot.scatter(position[0], position[1], s=(position[2]+1)*100)
pyplot.pause(0.001)
pyplot.draw()

sock.sendall('status(ready)')
lastTime = time.time()

while True:
    ready_receive, _, _ = select.select([sock],[],[], timeout)
    if ready_receive:
        data = sock.recv(1024)

        if 'launch' in data:
            status = 'flying'
            waypoint[2] = std_altitute #go to standard altitude on same X,Y
        if 'land' in data:
            status = 'landed'
            waypoint[2] = 0 #land on same X,Y position
        if 'setWaypoint' in data:
            _, x, y, z, _ = re.split('\(|\)|,', data)
            waypoint = [float(x), float(y), float(z)]

    deltaT = time.time()-lastTime
    if(deltaT > period): #run simulation every period
            lastTime = time.time()
            d = distance(position,waypoint)
            print('dT: ' + str(deltaT))
            #print('distance: ' + str(d))
            if d>min_distance:
                base = [(x2-x1)/d for x1,x2 in zip(position,waypoint)] #base vector
                position = [round(x1+x2*speed*deltaT,3) for x1,x2 in zip(position,base)]
                pyplot.scatter(position[0], position[1], s=(position[2]+1)*100)
                pyplot.pause(0.001)
                pyplot.draw()
            print('position: ' + str(position))
            print('waypoint: ' + str(waypoint))
            print('status: ' + status)

            _, ready_send, _ = select.select([],[sock],[], timeout)
            if ready_send[0]:
                print('sending percepts')
                sock.sendall('pos(' + str(position[0]) + ',' + str(position[1]) + ',' + str(position[2]) + ')')
                sock.sendall('status(' + status + ')')
