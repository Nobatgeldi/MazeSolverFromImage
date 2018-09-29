import sys
import signal
import logging
from ImageClean import ImageCleaner
from FindUGV import Finder
from CalibrateUAV import Calibrate
from SolveMaze import Solver
import time
from SerialPort import Serial


class Timeout:
    class Timeout(Exception):
        pass

    def __init__(self, sec):
        self.sec = sec

    def __enter__(self):
        signal.signal(signal.SIGALRM, self.raise_timeout)
        signal.alarm(self.sec)
    def __exit__(self, *args):
        signal.alarm(0)


ARM = 21
Throttle = 3

# region Logger
logger = logging.getLogger('teknofest')
hdlr = logging.FileHandler('teknofest.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)

logging.basicConfig(level=logging.INFO, format="[%(levelname)s]: %(asctime)-15s %(message)s")
# endregion

try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BOARD)
except:
    logger.info("Error importing RPi.GPIO!  This is probably because you need superuser privileges.")


def _init_serial():
    ser = Serial("/dev/rfcomm0")
    return ser


def send_range(transmitter, x_range, y_range):
    transmitter.write("F")
    transmitter.write(str(y_range))
    transmitter.write(str(x_range))

if __name__ == '__main__':
    GPIO.setup(ARM, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(Throttle, GPIO.OUT, initial=GPIO.LOW)
    time.sleep(3)

    GPIO.output(ARM, GPIO.HIGH)
    GPIO.output(Throttle, GPIO.HIGH)
    time.sleep(30)

    try:
        with Timeout(240):
            cleaner = ImageCleaner("resim/Finder_result.jpg")
            cleaned_image = cleaner.result()

            finder = Finder(cleaned_image)
            ugv_postion = finder.ugv_position()

            cleaner = ImageCleaner("resim/Calibrate_result.jpg")
            cleaned_image = cleaner.result()
            calibrater = Calibrate(cleaned_image, ugv_postion[0])
            state_of_covisart = True

    except Timeout.Timeout:
        logger.info("Zaman bitti, drone inise geciyor")
        state_of_covisart = False

    GPIO.output(Throttle, GPIO.LOW)
    if state_of_covisart:
        cleaned_image_for_solver = "resim/Calibrate_result.jpg"
        solver = Solver(cleaned_image_for_solver)
        solved = solver.solve()
    else:
        time.sleep(60)
    GPIO.output(ARM, GPIO.LOW)
    GPIO.cleanup()

    try:
        transmitter = _init_serial()
        old_x = 0
        old_y = 0
        cm_x = 0
        for nav in solved:
            if old_x != nav.x:
                cm_x = int((nav.x - old_x)*2.7)
                send_range(transmitter, nav.y, cm_x)

            if old_y != nav.y:
                cm_y = int((nav.y - old_y)*2.7)
                send_range(transmitter, nav.y, cm_x)
            logger.info("NAV: x:{0} y: {1}".format(nav.x, nav.y))
    except:
        print("kritik hata")
