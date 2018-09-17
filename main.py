import sys
import logging
from ImageClean import ImageCleaner
from FindUGV import Finder
from CalibrateUAV import Calibrate
from SolveMaze import Solver


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
except:
    logger.info("Error importing RPi.GPIO!  This is probably because you need superuser privileges.")

if __name__ == '__main__':

    cleaner = ImageCleaner(sys.argv[1], "resim/Finder_result.jpg")
    cleaned_image = cleaner.result()

    finder = Finder(cleaned_image)
    ugv_postion = finder.ugv_position()

    cleaner = ImageCleaner(sys.argv[2], "resim/Calibrate_result.jpg")
    cleaned_image = cleaner.result()
    calibrater = Calibrate(cleaned_image, ugv_postion[0])

    cleaned_image_for_solver = "resim/Calibrate_result.jpg"
    solver = Solver(cleaned_image_for_solver)
    solved = solver.solve()
    GPIO.cleanup()
    #for nav in solved:
        #logger.info("NAV: x:{0} y: {1}".format(nav.x, nav.y))