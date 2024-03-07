import cv2 as cv
import numpy as np

from .config import default_config
from .simplify_image import simplify_image
from .gen_islands import GenerateIslands
from .numbered_islands import create_numbered_islands

class ColorByNumber:
    def __init__(self, image_path, 
                 color_list = None, num_colors = None,
                 config = default_config):
        """
        Args:
            image_path: Path to the image file.
            color_list: List of colors in (R, G, B) format.
            config: Dictionary of configuration parameters (optional).
        """
        assert color_list is not None or num_colors is not None, \
            "Either color_list or num_colors must be provided."

        self.image_path = image_path
        self.config = config
        self.color_list = color_list
        self.num_colors = num_colors

        image = cv.imread(self.image_path)
        image = cv.cvtColor(image, cv.COLOR_BGR2RGB)
        self.image = image

    def create_color_by_number(self):

        simplified_image, indices_color_choices, color_list = simplify_image(
            image=self.image, 
            color_list=self.color_list,
            num_colors=self.num_colors,
            config=self.config
            )
        # Assigning the color_list to the one returned by simplify_image
        # because if it was initially None, it would have been assigned a value.
        self.color_list = color_list
        self.simplified_image = simplified_image

        generate_islands_obj = GenerateIslands(indices_color_choices)
        island_borders_list, centroid_coords_list = generate_islands_obj.get_islands(config=self.config)
        self.generate_islands_obj = generate_islands_obj
        self.island_borders_list = island_borders_list
        self.centroid_coords_list = centroid_coords_list

        numbered_islands = create_numbered_islands(
            islands = self.island_borders_list, 
            image_shape = self.image.shape,
            centroid_coords_list = self.centroid_coords_list,
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
            text = str(i + 1)
            text_size, _ = cv.getTextSize(text, font, font_size, 1)
            text_row = (end_row + text_size[1]) + 5
            text_col = start_col + (square_size // 2) - (text_size[0] // 2)
            cv.putText(image, text, (text_col, text_row), font, font_size, (0, 0, 0), 1)

        return image
