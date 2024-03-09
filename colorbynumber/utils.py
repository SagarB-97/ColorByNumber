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

def generate_color_legend(color_list,
                        cols=7,
                        rows=None, 
                        square_size=100, 
                        margin=10, 
                        gap_horizontal=5, gap_vertical=30, 
                        font=cv.FONT_HERSHEY_SIMPLEX, 
                        font_size=1, 
                        border_color=(0, 0, 0)
                            ):
        """
        Generates a grid of colored squares with labels below them.

        Args:
            cols: Number of columns in the grid.
            rows: Number of rows in the grid.
            square_size: Size of each square in the grid.
            margin: Margin around the grid.
            gap_horizontal: Horizontal gap between squares.
            gap_vertical: Vertical gap between squares.
            font: Font for the labels.
            font_size: Font size for the labels.
            border_color: Color of the border around each square.
        """

        # Calculate grid dimensions if not provided
        if rows is None and cols is None:
            num_colors = len(color_list)
            rows = cols = int(np.sqrt(num_colors)) + 1

        elif rows is None:
            cols = min(cols, len(color_list))
            rows = int(np.ceil(len(color_list) / cols))

        # Calculate total width and height based on margins, gaps, and squares
        total_width = 2 * margin + (cols + 1) * square_size + (cols - 1) * gap_horizontal
        total_height = 2 * margin + (rows + 1) * square_size + (rows - 1) * gap_vertical

        # Create a white image
        image = np.ones((total_height, total_width, 3), dtype=np.uint8) * 255

        # Fill squares with colors
        for i, color in enumerate(color_list):
            row = i // cols
            col = i % cols

            start_col = margin + col * (square_size + gap_horizontal)
            end_col = start_col + square_size

            start_row = margin + row * (square_size + gap_vertical)
            end_row = start_row + square_size

            # Fill square with color
            image[start_row:end_row, start_col:end_col] = color

            # Draw border around that color
            image[start_row, start_col:end_col] = border_color # Top Border
            image[end_row, start_col:end_col] = border_color # Bottom Border
            image[start_row:end_row, start_col] = border_color # Left Border
            image[start_row:end_row, end_col] = border_color # Right Border

            # Draw text label below the square
            text = str(i + 1)
            text_size, _ = cv.getTextSize(text, font, font_size, 1)
            text_row = (end_row + text_size[1]) + 5
            text_col = start_col + (square_size // 2) - (text_size[0] // 2)
            cv.putText(image, text, (text_col, text_row), font, font_size, (0, 0, 0), 1)

        return image
