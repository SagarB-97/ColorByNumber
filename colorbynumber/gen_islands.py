import cv2 as cv
import numpy as np

class GenerateIslands:
    def __init__(self, 
        indices_color_choices,
        gradient_kernel_size = 4,
        ):
        self.indices_color_choices = indices_color_choices
        self.gradient_kernel = np.ones((gradient_kernel_size, gradient_kernel_size), np.uint8)
        
        # List of coordinates for each islands border
        self.island_borders = {}
        for color_index in np.unique(indices_color_choices):
            self.island_borders[color_index] = []
        
        # Images of the islands
        self.island_fills = {}
        for color_index in np.unique(indices_color_choices):
            self.island_fills[color_index] = []
    
    def _get_cleaned_up_contours(self, island_fill, area_threshold_perc):
        contours_image = np.ones_like(island_fill)

        total_area = self.indices_color_choices.shape[0] * self.indices_color_choices.shape[1]

        contours, hierarchy = cv.findContours(
            island_fill, 
            mode = cv.RETR_TREE,
            method = cv.CHAIN_APPROX_NONE
        )

        for cntr_id, contour in enumerate(contours): 
            area_fraction_perc = (cv.contourArea(contour) / total_area) * 100
            if area_fraction_perc >= area_threshold_perc:
                cv.drawContours(contours_image, contours, cntr_id, (0,255,0), 4)

        return contours_image


    def _get_islands_for_one_color(self, color_index, border_padding, area_threshold_perc):
        # Get a binary image with just the selected color
        this_color = (self.indices_color_choices == color_index).astype(np.uint8)
        # Pad the image to enable border detection on image boundaries
        this_color = np.pad(this_color, border_padding, mode='constant', constant_values=0)

        # Find connected components
        num_labels, labels_im = cv.connectedComponents(this_color)

        for component_id in range(1, num_labels):
            this_component = (labels_im == component_id).astype(np.uint8)
            self.island_fills[color_index].append(this_component)
            
            # Get cleaned up contours
            cleaned_up_contours = self._get_cleaned_up_contours(this_component, area_threshold_perc)

            contour_border_coords = np.where(cleaned_up_contours == 0)
            self.island_borders[color_index].append((color_index, contour_border_coords))

    
    def get_islands(self, border_padding=2, area_threshold_perc=0.05):
        for color_index in np.unique(self.indices_color_choices):
            self._get_islands_for_one_color(color_index, border_padding, area_threshold_perc)
        
        # Flatten the list of borders
        island_borders_list = []
        for color_id in self.island_borders:
            if len(self.island_borders[color_id][1]) > 0:
                island_borders_list += self.island_borders[color_id]
        
        return island_borders_list
