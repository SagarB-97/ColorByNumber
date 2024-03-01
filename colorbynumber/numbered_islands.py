import cv2
import numpy as np

def _get_centroid(coordinates):
    """Get the centroid of a set of coordinates.
    
    Args:
        coordinates (list): A list of tuples.
            Each tuple contains the row and column of a pixel.
    Returns:
        tuple: The row and column of the centroid.
    """
    row_sum = 0
    col_sum = 0
    for row, col in coordinates:
        row_sum += row
        col_sum += col
    return (row_sum // len(coordinates), col_sum // len(coordinates))


def _add_text_to_image(image, text, position, font_size=1, font_color=(0, 0, 0)):
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
    position = (position[1], position[0])
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


def create_numbered_islands(islands, image_shape, border_color=[0, 0, 0]):
    """Create a new image with the islands numbered.
    
    Args:
        image (np.array): Numpy image.
        islands (list): A list of tuples. 
            Each tuple contains the color and the coordinates of the pixels in an island.
    Returns:
        np.array: A new image with the islands numbered.
    """
    # Create an all white image
    numbered_islands = np.ones(image_shape, dtype=np.uint8) * 255

    color_to_number = {}
    for i, (color, _) in enumerate(islands):
        color_to_number[color] = i + 1

    for color, island_coordinates in islands:
        for row, col in island_coordinates:
            numbered_islands[row, col] = border_color
        centroid = _get_centroid(island_coordinates)
        
        # Add the number to the centroid of the island
        numbered_islands = _add_text_to_image(
            numbered_islands, 
            str(color_to_number[color]), 
            centroid
        )
    
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
