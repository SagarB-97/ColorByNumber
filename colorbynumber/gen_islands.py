import cv2 as cv
import numpy as np
from polylabel import polylabel

from .config import default_config


class GenerateIslands:
    def __init__(self, indices_color_choices):
        """
        Args:
            indices_color_choices: 2D numpy array with the same shape as the image.
                Shows the color index chosen for each pixel in the image.
        """
        self.indices_color_choices = indices_color_choices
        
        # List of coordinates for each islands border
        self.island_borders = {}
        for color_index in np.unique(indices_color_choices):
            self.island_borders[color_index] = []
        
        # Images of the islands
        self.island_fills = {}
        for color_index in np.unique(indices_color_choices):
            self.island_fills[color_index] = []
        
        # Coordinate of centroids of islands
        self.island_centroids = {}
        for color_index in np.unique(indices_color_choices):
            self.island_centroids[color_index] = []

    
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
                                 arc_length_area_ratio_threshold, check_shape_validity):
        contours_image = np.ones_like(island_fill)

        total_area = self.indices_color_choices.shape[0] * self.indices_color_choices.shape[1]

        contours, hierarchy = cv.findContours(
            island_fill, 
            mode = cv.RETR_TREE,
            method = cv.CHAIN_APPROX_NONE
        )

        if check_shape_validity:
            is_valid_shape = self._is_valid_shape(
                contours = contours, 
                hierarchy = hierarchy,
                total_area = total_area,
                area_perc_threshold = area_perc_threshold, 
                arc_length_area_ratio_threshold = arc_length_area_ratio_threshold
            )
        else:
            is_valid_shape = True
        
        contours_selected = []
        hierarchy_selected = []

        if is_valid_shape:
            for cntr_id, contour in enumerate(contours): 
                area_fraction_perc = (cv.contourArea(contour) / total_area) * 100
                if area_fraction_perc >= area_perc_threshold:
                    cv.drawContours(
                        image = contours_image, 
                        contours = [contour], 
                        contourIdx = 0, 
                        color = (0,255,0), 
                        thickness = 1)
                    contours_selected.append(contour)
                    hierarchy_selected.append(hierarchy[0][cntr_id])
        
        # If the shape is not valid, return a blank image
        return contours_image, \
            contours_selected, \
            np.array(hierarchy_selected)


    def _get_centroid_for_island(self, contours, hierarchy):
        if len(contours) == 0:
            return np.array([np.nan, np.nan])

        coordinates_for_polylabel = []

        external_contours_ids = np.where(hierarchy[:,-1] == -1)[0]
        for external_contour_id in external_contours_ids:
            epsilon = 0.01 * cv.arcLength(contours[external_contour_id],True)
            approx_contour = cv.approxPolyDP(contours[external_contour_id], epsilon, True)
            coordinates_for_polylabel.append(approx_contour.squeeze())

        holes_contours_ids = np.where(hierarchy[:,-1] != -1)[0]
        for hole_contour_id in holes_contours_ids:
            epsilon = 0.01 * cv.arcLength(contours[hole_contour_id],True)
            approx_contour = cv.approxPolyDP(contours[hole_contour_id], epsilon, True)
            coordinates_for_polylabel.append(approx_contour.squeeze())
        
        centroid_coords =  polylabel(coordinates_for_polylabel)
        return [int(centroid_coords[0]), int(centroid_coords[1])]


    def _get_islands_for_one_color(self, color_index, border_padding, area_perc_threshold, 
                                   arc_length_area_ratio_threshold, check_shape_validity,
                                   open_kernel_size):
        # Get a binary image with just the selected color
        this_color = (self.indices_color_choices == color_index).astype(np.uint8)
        # Pad the image to enable border detection on image boundaries
        this_color = np.pad(this_color, border_padding, mode='constant', constant_values=0)

        # Run the open morphological operation to remove small islands and isthmuses
        kernel = np.ones((open_kernel_size, open_kernel_size),np.uint8)
        this_color = cv.morphologyEx(this_color, cv.MORPH_OPEN, kernel)

        # Find connected components
        num_labels, labels_im = cv.connectedComponents(this_color)

        for component_id in range(1, num_labels):
            this_component = (labels_im == component_id).astype(np.uint8)
            self.island_fills[color_index].append(this_component)
            

            # Get cleaned up contours
            cleaned_up_contours, contours_selected, hierarchies_selected = self._get_cleaned_up_contours(
                island_fill = this_component, 
                area_perc_threshold = area_perc_threshold, 
                arc_length_area_ratio_threshold = arc_length_area_ratio_threshold,
                check_shape_validity = check_shape_validity
            )

            # Get the centroid of the island
            centroid_coords = self._get_centroid_for_island(
                contours_selected,
                hierarchies_selected
            )
            self.island_centroids[color_index].append(centroid_coords)

            contour_border_coords = np.where(cleaned_up_contours == 0)
            self.island_borders[color_index].append((color_index, contour_border_coords))

    
    def get_islands(self, config = default_config):
        border_padding = config["border_padding"]
        area_perc_threshold = config["area_perc_threshold"]
        arc_length_area_ratio_threshold = config["arc_length_area_ratio_threshold"]
        check_shape_validity = config["check_shape_validity"]
        open_kernel_size = config["open_kernel_size"]

        for color_index in np.unique(self.indices_color_choices):
            self._get_islands_for_one_color(
                color_index = color_index, 
                border_padding = border_padding, 
                area_perc_threshold = area_perc_threshold,
                arc_length_area_ratio_threshold = arc_length_area_ratio_threshold,
                check_shape_validity = check_shape_validity,
                open_kernel_size = open_kernel_size,
            )
        
        # Flatten the list of borders
        island_borders_list = []
        centroid_coords_list = []
        for color_id in self.island_borders:
            for idx, border_coords in enumerate(self.island_borders[color_id]):
                if len(border_coords[1][0]) > 0:
                    island_borders_list.append(self.island_borders[color_id][idx])
                    centroid_coords_list.append(self.island_centroids[color_id][idx])
        
        return island_borders_list, centroid_coords_list
