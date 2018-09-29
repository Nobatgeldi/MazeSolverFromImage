# -*- coding: utf-8 -*-
import cv2
import sys
from PIL import Image
from resizeimage import resizeimage

""" 
    3264x2448 orginal image
    2448x2448 resized image
    
    69 derece görüş açısı vertical
    86 derece görüş açısı horizintal
    100 derece görüş açısı diagonal
    
    5 metre yükseklik de ortalama 7(687cm) metre görüş (vertical acida)
    5 metre yükseklik de ortalama 10(1000cm) metre görüş( horizintal açıda)
    
    eşit kenar resim de (2448x2448) vertical(69) açıyla 687 cm görüş saglar.
    
    her bir piksel ortalama 0.3 cm (0.2806372549)
"""


class ImageCleaner:
    def __init__(self, output):

        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)
        cv2.imwrite('resim/capture.jpg', frame)
        #cv2.imshow('frame', rgb)
        cap.release()
        #cv2.destroyAllWindows()

        self.image = "resim/capture.jpg"
        self.out = output
        image = Image.open(self.image)
        x, y = image.size
        image = resizeimage.resize_cover(image, [x/2, y/2])

        width, height = image.size
        print(width, height)

        # red green blue
        for i in range(width):
            for j in range(height):
                r, g, b = image.getpixel((i, j))
                if r > 100 and g < 100 and b < 100:
                    image.putpixel((i, j), (255, 0, 0))
                elif r < 100 and g > 100 and b < 100:
                    image.putpixel((i, j), (0, 255, 0))
                elif r < 100 and g < 100 and b > 100:
                    image.putpixel((i, j), (0, 0, 255))

        # Process every pixel
        for i in range(width):
            for j in range(height):
                r, g, b = image.getpixel((i, j))
                if r > 100 and g > 100 and b > 100:
                            image.putpixel((i, j), (255, 255, 255))
                elif r < 100 and g < 100 and b < 100:
                            image.putpixel((i, j), (0, 0, 0))

        self.image = image
        self.image.save(self.out)

    def result(self):
        return self.image

if __name__ == '__main__':
    cleaner = ImageCleaner("resim/Finder_result.jpg")