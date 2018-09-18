import time
try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error importing RPi.GPIO!  This is probably because you need superuser privileges.  You can achieve this by using 'sudo' to run your script")
GPIO.setmode(GPIO.BOARD)

ARM = 21
Throttle = 3

GPIO.setup(ARM, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(Throttle, GPIO.OUT, initial=GPIO.LOW)
time.sleep(3)

GPIO.output(ARM, GPIO.HIGH)
GPIO.output(Throttle, GPIO.HIGH)
time.sleep(60)

GPIO.output(Throttle, GPIO.LOW)
time.sleep(10)

GPIO.output(ARM, GPIO.LOW)