import os

import cv2 as cv
from matplotlib import pyplot as plt
import numpy as np

def show_image(image, cmap = None):
    if cmap:
        plt.imshow(image, cmap = cmap)
    else:
        plt.imshow(image)
    plt.axis('off')
    plt.show()

def draw_contours(contour, image_width, image_height):
    contours_image = np.ones((image_width, image_height), dtype = np.uint8)
    if type(contour) == tuple:
        # If the contour is a tuple, it is a tuple of multiple contours
        cv.drawContours(contours_image, contour, -1, (0,255,0), 4)
    else:
        # Else, it is a single contour
        cv.drawContours(contours_image, [contour], 0, (0,255,0), 4)
    show_image(contours_image, cmap = 'gray')

def save_image(image, filename, convert_to_bgr = True):
    if convert_to_bgr:
        image = cv.cvtColor(image.astype(np.uint8), cv.COLOR_RGB2BGR)
    
    directory = os.path.dirname(filename)
    if not os.path.exists(directory):
        os.makedirs(directory)
    cv.imwrite(filename, image)
