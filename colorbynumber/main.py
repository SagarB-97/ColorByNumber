import cv2 as cv

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
