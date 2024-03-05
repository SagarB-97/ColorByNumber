import cv2 as cv
import numpy as np

from .config import default_config
from .simplify_image import simplify_image
from .gen_islands import GenerateIslands
from .numbered_islands import create_numbered_islands

class ColorByNumber:
    def __init__(self, image_path, color_list, config = default_config):
        self.image_path = image_path
        self.color_list = color_list
        self.config = config

    def create_color_by_number(self):
        image = cv.imread(self.image_path)
        image = cv.cvtColor(image, cv.COLOR_BGR2RGB)
        self.image = image

        simplified_image, indices_color_choices = simplify_image(
            image=self.image, 
            color_list=self.color_list,
            config=self.config
            )
        self.simplified_image = simplified_image

        generate_islands_obj = GenerateIslands(indices_color_choices)
        island_borders_list, centroid_coords_list = generate_islands_obj.get_islands(config=self.config)
        self.generate_islands_obj = generate_islands_obj
        self.island_borders_list = island_borders_list

        numbered_islands = create_numbered_islands(
            islands = self.island_borders_list, 
            image_shape = self.image.shape,
            centroid_coords_list = centroid_coords_list,
            config = self.config
            )
        self.numbered_islands = numbered_islands

        return self.numbered_islands
    
    def generate_color_legend(self,
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
            colors: List of colors in (R, G, B) format.
            rows: Number of rows in the grid (optional).
            cols: Number of columns in the grid (optional).

        Returns:
            A NumPy array representing the color grid image.
        """

        # Calculate grid dimensions if not provided
        if rows is None and cols is None:
            num_colors = len(self.color_list)
            rows = cols = int(np.sqrt(num_colors)) + 1

        elif rows is None:
            cols = min(cols, len(self.color_list))
            rows = int(np.ceil(len(self.color_list) / cols))

        # Calculate total width and height based on margins, gaps, and squares
        total_width = 2 * margin + (cols + 1) * square_size + (cols - 1) * gap_horizontal
        total_height = 2 * margin + (rows + 1) * square_size + (rows - 1) * gap_vertical

        # Create a white image
        image = np.ones((total_height, total_width, 3), dtype=np.uint8) * 255

        # Fill squares with colors
        for i, color in enumerate(self.color_list):
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
            text_size, _ = cv.getTextSize(str(i), font, font_size, 1)
            text_row = (end_row + text_size[1]) + 5
            text_col = start_col + (square_size // 2) - (text_size[0] // 2)
            cv.putText(image, str(i), (text_col, text_row), font, font_size, (0, 0, 0), 1)

        return image
