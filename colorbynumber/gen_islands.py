import cv2 as cv
import numpy as np

class GenerateIslands:
    def __init__(self, 
        indices_color_choices,
        gradient_kernel_size = 4,
        ):
        self.indices_color_choices = indices_color_choices
        self.gradient_kernel = np.ones((gradient_kernel_size, gradient_kernel_size), np.uint8)
        self.color_index_island_list = []
    
    def _get_islands_for_one_color(self, color_index):
        # Get a binary image with just the selected color
        this_color = (self.indices_color_choices == color_index).astype(np.uint8)

        # Find connected components
        num_labels, labels_im = cv.connectedComponents(this_color)

        this_color_index_island_list = []

        for component_id in range(1, num_labels):
            this_component = (labels_im == component_id).astype(np.uint8)
            
            # Border detection
            gradient = cv.morphologyEx(this_component, cv.MORPH_GRADIENT, self.gradient_kernel)

            this_color_index_island_list.append((color_index, np.where(gradient == 1)))
        
        return this_color_index_island_list
    
    def get_islands(self):
        for color_index in np.unique(self.indices_color_choices):
            this_color_index_island_list = self._get_islands_for_one_color(color_index)
            self.color_index_island_list.extend(this_color_index_island_list)
        
        return self.color_index_island_list
