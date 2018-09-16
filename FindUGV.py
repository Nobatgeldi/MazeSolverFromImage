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
import logging
from Serial import Serial
from PIL import Image
from resizeimage import resizeimage

# region Logger
logger = logging.getLogger('teknofest')
hdlr = logging.FileHandler('teknofest.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)

logging.basicConfig(level=logging.INFO, format="[%(levelname)s]: %(asctime)-15s %(message)s")
# endregion


class Finder:

    def __init__(self, image):

        # region Colors.
        self.COLOR_MAP = {
            (0,255,0): 'GREEN',
            (255,0,0): 'RED',
            (0,0,255): 'BLUE',
            (255,255,255): 'WHITE',
            (0,0,0): 'BLACK'
        }
        self.COLOR_RED = (255, 0, 0)
        self.COLOR_GREEN = (0, 255, 0)
        self.COLOR_BLUE = (0, 0, 255)
        self.COLOR_WHITE = (255, 255, 255)
        self.COLOR_BLACK = (0, 0, 0)
        self.START_COLOR = self.COLOR_GREEN
        self.END_COLOR = self.COLOR_RED
        self.UGV_COLOR = self.COLOR_BLUE
        self.FRONTIER_COLOR = self.COLOR_GREEN
        self.memoized_color_map = {}

        """ pixel den mm cevirme hesaplamasi
            resim 256x256 olarak işlenir
            69 derece görüş açısıyla alnan resimde 500cm yükseklikde eşit kenar 687cm görüşalanı sağlar
            1px = 2.7 cm  
        """

        self.pixel_cm = 2.7
        # endregion

        # Output parameters.
        self.SNAPSHOT_FREQ = 20000 # Save an image every SNAPSHOT_FREQ steps.

        # Load image.
        self.image = image
        logger.info("Yuklelen resim  ({0} = {1} pixels).".format( self.image.size, self.image.size[0]*self.image.size[1]))

        """Image cleaning for processing"""
        self.image = self._imageWorking()

        self.image = self.image.convert('RGB')
        self.pixels = self.image.load()
        self.image.save("resim/Finder_working.jpg")

        # kara aracını bul
        self.UGV = self._findUGV()
        logger.info("IKA araci x:{0} y: {1} kordinatlarinda".format(self.UGV[0], self.UGV[1]))

        # başlangıç noktasını bul
        self.START = self._findStart()
        logger.info("Baslangic kordinat x:{0} y: {1}".format(self.START[0], self.START[1]))

        # kara aracı ile başlangıç noktası arasındakı mesafe farkı
        self.x_range = int(self._x_range(self.UGV[0], self.START[0]))
        self.y_range = int(self._y_range(self.UGV[1], self.START[1]))

        logger.info("Aradaki mesafe x:{0}cm y: {1}cm".format(self.x_range, self.y_range))
        logger.info("Kara araci baslangic noktasina gonderiliyor...")

        try:
            self.transmitter = self._init_serial()
            self.transmitter_state = True
        except:
            self.transmitter_state = False
            logger.info("Bluethoot baglantisinda hata olustu.")

        if self.transmitter_state:
            logger.info("Bluethoot baglantisi basladi.")
        else:
            logger.info("APC220 baglantisi aktiv ediliyor.")

    def _x_range(self, ugv_x, start_x):
        return (start_x - ugv_x)*self.pixel_cm

    def _y_range(self, ugv_y, start_y):
        return (start_y - ugv_y)*self.pixel_cm

    def _imageWorking(self):
        logger.info("Resim hazirlaniyor...")
        image = resizeimage.resize_cover(self.image, [256, 256])
        width, height = image.size

        # Process every pixel
        for i in range(width):
            for j in range(height):
                r, g, b = image.getpixel((i, j))
                if r > 100:
                    if g > 100:
                        if b > 100:
                            image.putpixel((i, j), (255, 255, 255))

                if r < 100:
                    if g < 100:
                        if b < 100:
                            image.putpixel((i, j), (0, 0, 0))
        logger.info("Hazirlanan resim boyutu: '{0}'".format(image.size))
        return image

    def _findUGV(self):
        logger.info("Kara araci araniyor...")
        ugv = self._findColorCenter(self.UGV_COLOR)
        return ugv

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

    def _init_serial(self):
        ser = Serial("98:D3:32:70:8B:76")
        return ser
    def ugv_position(self):
        return self.UGV

def mean(numbers):
    return int(sum(numbers)) / max(len(numbers), 1)


def distance(c1, c2):
    (r1, g1, b1) = c1
    (r2, g2, b2) = c2
    return math.sqrt((r1 - r2)**2 + (g1 - g2) ** 2 + (b1 - b2) **2)


"""if __name__ == '__main__':
    solver = Finder(sys.argv[1])"""
