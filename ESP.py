import serial

class ESP:
    def __init__(self, port, name, baud_rate=115200, timeout=0.1):
        self._port = port
        self._name = name
        self._ID = ''
        self.interface = serial.Serial(port, baud_rate, timeout = timeout)

        self.send('ID_REQ')
        while self._ID == '':
            self._ID = self.read()
        self.send(name)
        ok = ''
        while ok != 'NAME_OK':
            print(ok)
            ok = self.read()


    def _encode(self, msg):
        return msg + '\n'

    def send(self, msg):
        self.interface.write(self._encode(msg))

    def read(self):
        return self.interface.readline()[:-1]

    def getID(self):
        return self._ID
