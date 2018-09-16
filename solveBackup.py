#!/usr/bin/env python2.7

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
import cv2
import sys
import math
import colorsys
import logging
#from Serial import Serial
from PIL import Image
from resizeimage import resizeimage

logging.basicConfig(level=logging.INFO, format="[%(levelname)s]: %(asctime)-15s %(message)s")


class Point(object):

    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


class Solver:
    """
    file_in = Input maze image filename.
    image   = Maze image object.
    pixels  = Maze image pixel array.
    """
    def __init__(self, img):
        # Colors.
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
        self.FRONTIER_COLOR = self.COLOR_GREEN
        self.memoized_color_map = {}
        self.pixel_mm = 25

        # Output parameters.
        self.SNAPSHOT_FREQ = 20000  # Save an image every SNAPSHOT_FREQ steps.

        # Load image.
        self.image = img
        logging.info("Loaded image ({0} = {1} pixels).".format(self.image.size, self.image.size[0]*self.image.size[1]))

        """Image cleaning for processing"""
        self.image = self._imageWorking()

        self.image = self.image.convert('RGB')
        self.pixels = self.image.load()

        self.image.save("resim/SolveMaze_worked.jpg")

        # başlangıç noktasını bul
        self.START = self._findStart()
        logging.info("Başlangıç kordinat x:{0} y: {1}".format(self.START[0], self.START[1]))

        # bitiş noktasını bul
        self.END = self._findEnd()
        logging.info("Çıkış kordinat x:{0} y: {1}".format(self.END[0], self.END[1]))

        self.image = self._cropImage(self.START[0]+5, 0, self.END[0]-5, 256)
        self.pixels = self.image.load()

        # yeni başlangıç noktasını bul
        self.START = 5, self.START[1]
        logging.info("Yeni başlangıç kordinat x:{0} y: {1}".format(self.START[0], self.START[1]))

        # yeni bitiş noktasını bul
        self.END = self.END[0]-35, self.END[1]
        logging.info("Yeni cıkış kordinat x:{0} y: {1}".format(self.END[0], self.END[1]))
        self._cleanImage()

        int_start_x = int(self.START[0])
        int_start_y = int(self.START[1])
        int_end_x = int(self.END[0])
        int_end_y = int(self.END[1])
        print("type of int_start_x:")
        print(type(int_start_x))

        #opencv solve
        self.rw = 2
        self.p = 0

        self.start = Point(int_start_x, int_start_y)
        self.end = Point(int_end_x, int_end_y)

        print(self.start.x)
        print(self.start.y)
        print(self.end.x)
        print(self.end.y)

        self.dir4 = [Point(0, -1), Point(0, 1), Point(1, 0), Point(-1, 0)]
        self.img = cv2.imread("resim/SolveMaze_cleaned.jpg", cv2.IMREAD_GRAYSCALE)
        _, self.img = cv2.threshold(self.img, 120, 255, cv2.THRESH_BINARY)
        self.img = cv2.cvtColor(self.img, cv2.COLOR_GRAY2BGR)
        self.h, self.w = self.img.shape[:2]

        self.result = self.BFS(self.start, self.end)
        for nav in self.result:
            logging.info("x:{0} y: {1}".format(nav.x, nav.y))

        cv2.imshow("Image", self.img)
        cv2.waitKey(0)

    def _x_Range(self, ugv_x, start_x):
        return (start_x - ugv_x)*self.pixel_mm

    def _y_Range(self, ugv_y, start_y):
        return (start_y - ugv_y)*self.pixel_mm

    def _cropImage(self, x, y, w, h):
        image_cr = self.image
        # crop image
        width, height = image_cr.size
        cropped = image_cr.crop((x, y, w, h))
        cropped.save("resim/SolveMaze_cropped.jpg")
        return cropped

    def _imageWorking(self):
        logging.info("Image restoring...")
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
        return image
    """
    Purify pixels to either pure black or white, except for the start/end pixels.
    """
    def _cleanImage(self):
        logging.info("Cleaning image...")
        x, y = self.image.size
        for i in range(x):
            for j in range(y):
                if (i,j) == self.START:
                    self.pixels[i, j] == self.START_COLOR
                    continue
                if (i,j) == self.END:
                    self.pixels[i,j] == self.END_COLOR
                    continue
                closest_color = self._findClosestColor(self.pixels[i,j])
                for color in [self.COLOR_WHITE, self.COLOR_BLACK]:
                    if closest_color == color: self.pixels[i,j] = color
                for color in [self.START_COLOR, self.END_COLOR]:
                    if closest_color == color: self.pixels[i,j] = self.COLOR_WHITE
        self.image.save("resim/SolveMaze_cleaned.jpg")

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
        logging.info("Finding START point...")
        start = self._findColorCenter(self.START_COLOR)
        self._drawSquare(start, self.START_COLOR)
        return start

    def _findEnd(self):
        logging.info("Finding END point...")
        end = self._findColorCenter(self.END_COLOR)
        self._drawSquare(end, self.END_COLOR)
        return end

    def solve(self):
        return self.result

    def BFS(self, s, e):
        const = 10000
        found = False
        q = []
        v = [[0 for j in range(self.w)] for i in range(self.h)]
        parent = [[Point() for j in range(self.w)] for i in range(self.h)]

        q.append(s)
        v[s.y][s.x] = 1
        while len(q) > 0:
            p = q.pop(0)
            for d in self.dir4:
                cell = p + d
                if (cell.x >= 0 and cell.x < self.w and cell.y >= 0 and cell.y < self.h and v[cell.y][cell.x] == 0 and
                        (self.img[cell.y][cell.x][0] != 0 or self.img[cell.y][cell.x][1] != 0 or self.img[cell.y][cell.x][2] != 0)):
                    q.append(cell)
                    v[cell.y][cell.x] = v[p.y][p.x] + 1  # Later

                    self.img[cell.y][cell.x] = list(reversed(
                        [i * 255 for i in colorsys.hsv_to_rgb(v[cell.y][cell.x] / const, 1, 1)])
                    )
                    parent[cell.y][cell.x] = p
                    if cell == e:
                        found = True
                        del q[:]
                        break
        path = []
        if found:
            p = e
            while p != s:
                path.append(p)
                p = parent[p.y][p.x]
            path.append(p)
            path.reverse()

            for p in path:
                self.img[p.y][p.x] = [255, 255, 255]
            print("Path Found")
        else:
            print("Path Not Found")
        return path

    def _drawX(self, pos, color=(0,0,255)):
        x, y = pos
        d = 5
        for i in range(-d, d):
            self.pixels[x+i, y] = color
        for j in range(-d, d):
            self.pixels[x, y+j] = color

    def _drawSquare(self, pos, color=(0,0,255)):
        x,y = pos
        d = 1
        for i in range(-d,d):
            for j in range(-d,d):
                self.pixels[x+i,y+j] = color

    def _inBounds(self, dim, x, y):
        mx, my = dim
        if x < 0 or y < 0 or x >= mx or y >= my:
            return False
        return True

    def _isWhite(self, pixels, pos):
        i,j = pos
        r,g,b = pixels[i,j]
        th = 240
        if pixels[i,j] == self.COLOR_WHITE or pixels[i,j] == 0 or (r>th and g>th and b>th) \
                or pixels[i,j] == self.END_COLOR:
            return True

def mean(numbers):
    return int(sum(numbers)) / max(len(numbers), 1)

def distance(c1, c2):
    (r1,g1,b1) = c1
    (r2,g2,b2) = c2
    return math.sqrt((r1 - r2)**2 + (g1 - g2) ** 2 + (b1 - b2) **2)


if __name__ == '__main__':
    solver = Solver(sys.argv[1])
    solver.solve()
