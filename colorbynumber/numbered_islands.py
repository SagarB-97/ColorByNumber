import cv2
import numpy as np

def _get_centroid(coordinates):
    rows, cols = coordinates
    if len(rows) == 0 or len(cols) == 0:
        return np.array([np.nan, np.nan])
    return (int(np.mean(rows)), int(np.mean(cols)))


def _add_text_to_image(image, text, position, font_size=0.5, font_color=(0, 0, 0)):
    """Add text to an image.
    
    Args:
        image (np.array): Numpy image.
        text (str): The text to add.
        position (tuple): The position to add the text.
        font_size (int): The size of the font.
        font_color (tuple): The color of the font.
    Returns:
        np.array: A new image with the text added.
    """
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = font_size
    font_thickness = 2
    return cv2.putText(
        image, 
        text, 
        position, 
        font, 
        font_scale, 
        font_color, 
        font_thickness, 
        cv2.LINE_AA
        )


def create_numbered_islands(islands, image_shape, 
                            centroid_coords_list = None,
                            border_color=[0, 0, 0], 
                            padding=2, show_numbers=True, binary = False):
    """Create a new image with the islands numbered.
    
    Args:
        image (np.array): Numpy image.
        islands (list): A list of tuples. 
            Each tuple contains the color_id and the coordinates of the pixels in an island.
    Returns:
        np.array: A new image with the islands numbered.
    """
    # Create an all white image
    width, height, channels = image_shape
    numbered_islands = np.ones((width + padding*2, height + padding*2, channels), 
                               dtype=np.uint8) * 255

    for idx, (color_id, island_coordinates) in enumerate(islands):
        numbered_islands[island_coordinates] = border_color
        
        # Add the number to the centroid of the island
        if show_numbers:
            if centroid_coords_list:
                centroid = centroid_coords_list[idx]
            else:
                centroid = _get_centroid(island_coordinates)
            if not np.isnan(centroid).any():
                numbered_islands = _add_text_to_image(
                    numbered_islands, 
                    str(color_id), 
                    centroid
                )
    if binary:
        # Convert numbered_islands to binary using openCV
        numbered_islands = cv2.cvtColor(numbered_islands, cv2.COLOR_BGR2GRAY)
        _, numbered_islands = cv2.threshold(numbered_islands, 127, 255, cv2.THRESH_BINARY)
        return numbered_islands

    return numbered_islands

def _test_create_numbered_islands():
    image_shape = (853, 1280, 3)

    max_row, max_col = image_shape[0], image_shape[1]

    diagonal_coordinates = [
        (i,i) for i in range(max_row)
    ]
    left_border = [
        (i, 0) for i in range(max_row)
    ]
    bottom_border_left = [
        (max_row-1, i) for i in range(max_row)
    ]
    region_1 = diagonal_coordinates + left_border + bottom_border_left

    bottom_border_right = [
        (max_row - 1, i) for i in range(max_row, max_col)
    ]
    right_border = [
        (i, max_col - 1) for i in range(max_row)
    ]
    top_border = [
        (0, i) for i in range(max_col)
    ]
    region_2 = bottom_border_right + right_border + top_border


    numbered_islands = create_numbered_islands(
        islands = [
            ('random_color_1', region_1),
            ('random_color_2', region_2)
        ],
        image_shape = image_shape,
    )

    return numbered_islands
