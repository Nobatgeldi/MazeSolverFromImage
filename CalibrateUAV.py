#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

"""
    Maze Solver

    Usage:
        python solve.py <maze-image-in>

    Output:
        An image of the original maze with the solution path drawn in.

    Note:
        This program relies on colors.
        For example, assumes explorable space is WHITE and the maze is BLACK.
"""

import os
import sys
import math
import time
import logging
from Serial import Serial
from ImageClean import ImageCleaner
from PIL import Image

# region Logger
logger = logging.getLogger('teknofest')
hdlr = logging.FileHandler('teknofest.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)

logging.basicConfig(level=logging.INFO, format="[%(levelname)s]: %(asctime)-15s %(message)s")
# endregion

ROLL_UP = 11
ROLL_DOWN = 19

PITCH_UP = 7
PITCH_DOWN = 15

YAW_UP = 5
YAW_DOWN = 13

chan_list = (ROLL_UP, ROLL_DOWN, PITCH_UP, PITCH_DOWN, YAW_UP, YAW_DOWN)

try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BOARD)
    gpio_state = True
except:
    gpio_state = False
    logger.info("Error importing RPi.GPIO!  This is probably because you need superuser privileges.")


class Calibrate:

    def __init__(self, img, ugv_x):

        # region Colors.
        self.COLOR_MAP = {
            (0, 255, 0): 'GREEN',
            (255, 0, 0): 'RED',
            (0, 0, 255): 'BLUE',
            (255, 255, 255): 'WHITE',
            (0, 0, 0): 'BLACK'
        }
        self.COLOR_RED = (255, 0, 0)
        self.COLOR_GREEN = (0, 255, 0)
        self.COLOR_BLUE = (0, 0, 255)
        self.COLOR_WHITE = (255, 255, 255)
        self.COLOR_BLACK = (0, 0, 0)
        self.START_COLOR = self.COLOR_GREEN
        self.END_COLOR = self.COLOR_RED
        self.FRONTIER_COLOR = self.COLOR_GREEN
        self.memoized_color_map = {}

        """ pixel den mm cevirme hesaplamasi
            resim 256x256 olarak işlenir
            69 derece görüş açısıyla alnan resimde 500cm yükseklikde eşit kenar 687cm görüşalanı sağlar
            1px = 2.7 cm  
        """

        self.pixel_cm = 2.7
        # endregion

        self.ugv = ugv_x

        # Output parameters.
        self.SNAPSHOT_FREQ = 20000 # Save an image every SNAPSHOT_FREQ steps.

        # Load image.
        self.image = img
        logger.info("Yuklelen resim ({0} = {1} pixels).".format(self.image.size, self.image.size[0]*self.image.size[1]))

        self.image = self.image.convert('RGB')
        self.pixels = self.image.load()

        if gpio_state:
            self._gpio_setup()
            self.result = self._recursive()

    def _recursive(self):

        #region kordinates

        cleaner = ImageCleaner("resim/Calibrate_result.jpg")
        cleaned_image = cleaner.result()
        self.image = cleaned_image.convert('RGB')
        self.pixels = self.image.load()

        #başlangıç noktasını bul
        try:
            self.START = self._findStart()
            start_not_found = False
            logger.info("Baslangic kordinat x:{0} y: {1}".format(self.START[0], self.START[1]))
        except:
            start_not_found = True
            logger.info("Baslangic kordinat bulunamadi")

        # bitiş noktasını bul
        try:
            self.END = self._findEnd()
            end_not_found = False
            logger.info("Cikis kordinat x:{0} y: {1}".format(self.END[0], self.END[1]))
        except:
            end_not_found = True
            logger.info("Cikis kordinat bulunamadi")
        #endregion

        if end_not_found:
            if self.START[0] > self.ugv:
                self._go_right()
                time.sleep(1)
                self._stand()

            elif self.START[0] < self.ugv:
                self._go_left()
                time.sleep(1)
                self._stand()
            self._recursive()
        else:
            return True

    def _x_range(self, ugv_x, start_x):
        return (start_x - ugv_x)*self.pixel_cm

    def _y_range(self, ugv_y, start_y):
        return (start_y - ugv_y)*self.pixel_cm

    def _findClosestColor(self, color, memoize=False):
        colors = list(self.COLOR_MAP.keys())
        if color in self.memoized_color_map and memoize == True:
            return color
        closest_color = sorted(colors, key=lambda c: distance(c, color))[0]
        if memoize == True: self.memoized_color_map[color] = closest_color
        return closest_color

    def _findColorCenter(self, color):
        x_min, x_max, y_min, y_max = float('inf'), float('-inf'), float('inf'), float('-inf')
        x,y = self.image.size
        for i in range(x):
            for j in range(y):
                code = self._findClosestColor(self.pixels[i,j])
                if  code == color:
                    x_min, y_min = min(x_min, i), min(y_min, j)
                    x_max, y_max = max(x_max, i), max(y_max, j)
        return (mean([x_min, x_max]), mean([y_min, y_max]))

    def _findStart(self):
        logger.info("Finding START point...")
        start = self._findColorCenter(self.START_COLOR)
        return start

    def _findEnd(self):
        logging.info("Finding END point...")
        end = self._findColorCenter(self.END_COLOR)
        return end

    def _init_serial(self):
        ser = Serial("98:D3:32:70:8B:76")
        return ser

    #region GPIO control section
    def _gpio_setup(self):
        GPIO.setup(ROLL_UP, GPIO.OUT)
        GPIO.setup(ROLL_DOWN, GPIO.OUT)

        GPIO.setup(PITCH_UP, GPIO.OUT)
        GPIO.setup(PITCH_DOWN, GPIO.OUT)

        GPIO.setup(YAW_UP, GPIO.OUT)
        GPIO.setup(YAW_DOWN, GPIO.OUT)

        GPIO.output(chan_list, GPIO.LOW)

    def _go_right(self):
        GPIO.output(PITCH_UP, 0)
        GPIO.output(PITCH_DOWN, 1)

    def _go_left(self):
        GPIO.output(PITCH_UP, 1)
        GPIO.output(PITCH_DOWN, 0)

    def _stand(self):
        GPIO.output(PITCH_UP, 0)
        GPIO.output(PITCH_DOWN, 0)
    #endregion

def mean(numbers):
    return int(sum(numbers)) / max(len(numbers), 1)


def distance(c1, c2):
    (r1,g1,b1) = c1
    (r2,g2,b2) = c2
    return math.sqrt((r1 - r2)**2 + (g1 - g2) ** 2 + (b1 - b2) **2)


if __name__ == '__main__':
    solver = Calibrate(sys.argv[1], sys.argv[2])
