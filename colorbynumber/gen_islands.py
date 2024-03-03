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
    
    def _is_valid_shape(self, contours, hierarchy, total_area, area_perc_threshold,
                        arc_length_area_ratio_threshold):
        holes_contours_ids = np.where(hierarchy[0,:,-1] != -1)[0]
        hole_areas_sum = 0
        for hole_contour_id in holes_contours_ids:
            hole_area = cv.contourArea(contours[hole_contour_id])
            hole_areas_sum += hole_area

        external_contours_ids = np.where(hierarchy[0,:,-1] == -1)[0]
        external_areas_sum = 0
        external_arc_length = 0
        for external_contour_id in external_contours_ids:
            external_areas_sum += cv.contourArea(contours[external_contour_id])
            external_arc_length += cv.arcLength(contours[external_contour_id],True)

        total_island_area = external_areas_sum - hole_areas_sum

        if total_island_area == 0:
            return False
        
        area_percentage = (total_island_area / total_area) * 100
        arc_length_area_ratio = (external_arc_length / total_island_area)

        if (area_percentage >= area_perc_threshold) \
            and (arc_length_area_ratio <= arc_length_area_ratio_threshold):
            return True
        else:
            return False


    def _get_cleaned_up_contours(self, island_fill, area_perc_threshold, 
                                 arc_length_area_ratio_threshold):
        contours_image = np.ones_like(island_fill)

        total_area = self.indices_color_choices.shape[0] * self.indices_color_choices.shape[1]

        contours, hierarchy = cv.findContours(
            island_fill, 
            mode = cv.RETR_TREE,
            method = cv.CHAIN_APPROX_NONE
        )

        is_valid_shape = self._is_valid_shape(
            contours = contours, 
            hierarchy = hierarchy,
            total_area = total_area,
            area_perc_threshold = area_perc_threshold, 
            arc_length_area_ratio_threshold = arc_length_area_ratio_threshold
        )
        if is_valid_shape:
            for cntr_id, contour in enumerate(contours): 
                area_fraction_perc = (cv.contourArea(contour) / total_area) * 100
                if area_fraction_perc >= area_perc_threshold:
                    cv.drawContours(contours_image, contours, cntr_id, (0,255,0), 4)
        
        # If the shape is not valid, return a blank image
        return contours_image


    def _get_islands_for_one_color(self, color_index, border_padding, area_perc_threshold, 
                                   arc_length_area_ratio_threshold):
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
            cleaned_up_contours = self._get_cleaned_up_contours(
                island_fill = this_component, 
                area_perc_threshold = area_perc_threshold, 
                arc_length_area_ratio_threshold = arc_length_area_ratio_threshold
            )

            contour_border_coords = np.where(cleaned_up_contours == 0)
            self.island_borders[color_index].append((color_index, contour_border_coords))

    
    def get_islands(self, border_padding=2, area_perc_threshold=0.05, 
                    arc_length_area_ratio_threshold=0.1):
        for color_index in np.unique(self.indices_color_choices):
            print(color_index)
            self._get_islands_for_one_color(
                color_index = color_index, 
                border_padding = border_padding, 
                area_perc_threshold = area_perc_threshold,
                arc_length_area_ratio_threshold = arc_length_area_ratio_threshold,
            )
        
        # Flatten the list of borders
        island_borders_list = []
        for color_id in self.island_borders:
            if len(self.island_borders[color_id][1]) > 0:
                island_borders_list += self.island_borders[color_id]
        
        return island_borders_list
