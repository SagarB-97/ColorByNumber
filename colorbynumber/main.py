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
