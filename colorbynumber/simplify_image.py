import numpy as np


def simplify_image(image, color_list):
    """
    Converts all colors in an image to the closest color in the color list.
    
    Args:
      image: Image in the RGB color space as a 3D array.
      color_list: A list of tuples representing RGB values of allowed colors.
    
    Returns:
      A copy of the image with all colors replaced with the closest color in the list.
    """
    
    width, height, channels = image.shape
    image_copy = image.reshape((width, height, 1, channels)).copy()

    color_list = np.array(color_list)
    num_colors = color_list.shape[0]
    color_list_broadcastable = color_list.reshape((1, 1, num_colors, 3))

    norm_diff = ((image_copy - color_list_broadcastable)**2).sum(axis = -1)
    indices_color_choices = norm_diff.argmin(axis = -1)
    simplified_image = color_list[indices_color_choices.flatten(), :].reshape(image.shape)

    return simplified_image
