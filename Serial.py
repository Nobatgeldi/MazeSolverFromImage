try:
    import bluetooth
except:
    print("Error on bluetooth")

class Serial(object):

    def __init__(self, addr):
        self.bd_addr = addr
        self.port = 1
        self.sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.sock.connect((self.bd_addr, self.port))

    def write(self, data):
        self.sock.send(data)

    def close(self):
        self.sock.close()

    def write_all(self, data):
        self.sock.sendall(data)

