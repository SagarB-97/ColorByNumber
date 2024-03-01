import numpy as np

def _closest_color(pixel, color_list):
    """
    Finds the closest color in the list to the given pixel (RGB values)
    
    Args:
      pixel: A tuple representing the RGB values of a pixel (R, G, B).
      color_list: A list of tuples representing RGB values of allowed colors.
    
    Returns:
      A tuple representing the RGB values of the closest color in the list.
    """
    distances = np.array([np.linalg.norm(np.array(pixel) - np.array(color)) for color in color_list])
    return color_list[np.argmin(distances)]

def simplify_image(image, color_list):
    """
    Converts all colors in an image to the closest color in the color list.
    
    Args:
      image: Image in the RGB color space as a 3D array.
      color_list: A list of tuples representing RGB values of allowed colors.
    
    Returns:
      A copy of the image with all colors replaced with the closest color in the list.
    """
    
    # Replace each pixel with closest color from the list
    converted_image = image.copy()  # Operate on a copy
    height, width, channels = image.shape
    for y in range(height):
        for x in range(width):
            pixel = image[y, x]
            closest = _closest_color(pixel, color_list)
            converted_image[y, x] = closest
    return converted_image
