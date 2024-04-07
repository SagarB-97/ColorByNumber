import cv2
import numpy as np

from .config import default_config

def _get_centroid(coordinates):
    rows, cols = coordinates
    if len(rows) == 0 or len(cols) == 0:
        return np.array([np.nan, np.nan])
    return (int(np.mean(rows)), int(np.mean(cols)))


def _add_text_to_image(image, text, position, font_size, font_color, font_thickness):
    """Add text to an image.
    
    Args:
        image (np.array): Numpy image.
        text (str): The text to add.
        position (tuple): The position to add the text.
        font_size (int): The size of the font.
        font_color (tuple): The color of the font.
        font_thickness (int): The thickness of the font.
    Returns:
        np.array: A new image with the text added.
    """
    font = cv2.FONT_HERSHEY_SIMPLEX
    text_size, _ = cv2.getTextSize(text, font, font_size, 1)
    position = (position[0] - text_size[0]//2, position[1] + text_size[1]//2)
    return cv2.putText(
        image, 
        text, 
        position, 
        font, 
        font_size, 
        font_color, 
        font_thickness, 
        cv2.LINE_AA
        )


def add_numbers_to_image(image, 
                         centroid_coords_list, color_id_list, 
                         font_size, font_color, font_thickness):
    """Add numbers to the image.
    
    Args:
        image (np.array): Numpy image.
        centroid_coords_list (list): A list of centroid coordinates for the islands.
        color_id_list (list): A list of color ids.
    Returns:
        np.array: A new image with the numbers added.
    """
    numbered_islands = image.copy()
    for idx in range(len(centroid_coords_list)):
        centroid = centroid_coords_list[idx]
        color_id = color_id_list[idx]
        if not np.isnan(centroid).any():
            numbered_islands = _add_text_to_image(
                image=numbered_islands, 
                text=str(color_id), 
                position=centroid,
                font_size=font_size,
                font_color=font_color,
                font_thickness=font_thickness
            )
    return numbered_islands


def create_islands(islands, image_shape,
                   padding, border_color, binary = False):
    """Create a new image with the islands numbered.
    
    Args:
        islands (list): A list of tuples. 
            Each tuple contains the color id and the coordinates of the island border.
        image_shape (tuple): The shape of the original image.
        padding (int): The padding to add to the image.
        border_color (tuple): The color of the border.
        binary (bool): If True, the output will be a binary image.
    """
    # Create an all white image
    width, height, channels = image_shape
    numbered_islands = np.ones((width + padding*2, height + padding*2, channels), 
                               dtype=np.uint8) * 255

    for color_id, island_coordinates in islands:
        numbered_islands[island_coordinates] = border_color

    if binary:
        # Convert numbered_islands to binary using openCV
        numbered_islands = cv2.cvtColor(numbered_islands, cv2.COLOR_BGR2GRAY)
        _, numbered_islands = cv2.threshold(numbered_islands, 127, 255, cv2.THRESH_BINARY)
        return numbered_islands

    return numbered_islands


def create_numbered_islands(islands, image_shape, 
                            centroid_coords_list = None,
                            config = default_config, 
                            show_numbers=True, binary = False):
    """Create a new image with the islands numbered.
    
    Args:
        islands (list): A list of tuples. 
            Each tuple contains the color id and the coordinates of the island border.
        image_shape (tuple): The shape of the original image.
        centroid_coords_list (list): A list of centroid coordinates for the islands.
        config (dict): Configuration dictionary.
        show_numbers (bool): If True, the numbers will be shown in the islands.
        binary (bool): If True, the output will be a binary image.
    """

    padding = config["border_padding"]
    border_color = config["border_color"]
    font_size = config["font_size"]
    font_color = config["font_color"]
    font_thickness = config["font_thickness"]

    islands_image = create_islands(
        islands, 
        image_shape, 
        padding, 
        border_color, 
        binary
        )
    
    if not show_numbers:
        return islands_image
    
    if not centroid_coords_list:
        centroid_coords_list = [
            _get_centroid(island_coordinates) for _, island_coordinates in islands
            ]
    numbered_islands = add_numbers_to_image(
        islands_image, 
        centroid_coords_list, 
        [color_id for color_id, _ in islands], 
        font_size, 
        font_color, 
        font_thickness
        )
    return numbered_islands
