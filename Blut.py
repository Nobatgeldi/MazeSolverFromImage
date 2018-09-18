import bluetooth
import time

bd_addr = "98:D3:32:70:8B:76"
port = 1
sock = bluetooth.BluetoothSocket (bluetooth.RFCOMM)
sock.connect((bd_addr,port))

while 1:
    tosend = raw_input()
    if tosend != 'q':
        sock.send(tosend)
    else:
        break
    time.sleep(1)
    buffer = sock.recv(4096)
    print (buffer)

sock.close()