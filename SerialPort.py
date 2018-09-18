import time
import serial

# configure the serial connections (the parameters differs on the device you are connecting to)
class Serial(object):

    def __init__(self, addr):
        self.ser = serial.Serial(
            port=addr,  #'/dev/rfcomm0'
            baudrate=9600,
            parity=serial.PARITY_ODD,
            stopbits=serial.STOPBITS_TWO,
            bytesize=serial.SEVENBITS,
            timeout=5,
            write_timeout=5
        )
        self.ser.isOpen()
        time.sleep(2)

    def write(self, data):
        self.ser.write(data)
        time.sleep(1)

    def close(self):
        self.ser.close()

    def available(self):
        return self.ser.in_waiting

    def clean_buffer(self):
        self.ser.reset_input_buffer()

    def read(self, size):
        return self.read(size)


if __name__ == '__main__':
    com = Serial("/dev/rfcomm0")
    print("Serial init")
    time.sleep(2)
    print("Serial clean_buffer")
    com.clean_buffer()
    print("write F")
    com.write("F")

    time.sleep(2)
    print("write 5")
    com.write("5")
    time.sleep(2)
    print("write 5")
    com.write("5")

