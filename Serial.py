try:
    import bluetooth
except:
    print("Error on bluetooth")
import time

class Serial(object):

    def __init__(self, addr):
        self.bd_addr = addr
        self.port = 1
        self.sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.sock.connect((self.bd_addr, self.port))

    def write(self, data):
        self.sock.send(data)

    def read(self, length):
        return self.sock.recv(length)

    def close(self):
        self.sock.close()

    def write_all(self, data):
        self.sock.sendall(data)

if __name__ == '__main__':
    ser = Serial("98:D3:32:70:8B:76")
    ser.write('2')
    buffer = ser.read(1024)
    buffer = int(buffer)
    print(buffer == 2)
    if buffer == 2:
        print("if inner")
        ser.write('F')
        buffer = ser.read(4096)
        print(buffer)
        ser.write("50")
        buffer = ser.read(4096)
        print(buffer)
        ser.write("50")
        buffer = ser.read(4096)
        print(buffer)
        time.sleep(1)
