import cv2 as cv
import numpy as np

from .config import default_config

def _choose_closest_colors(image, color_list):
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

    # Adding 1 to indices_color_choices as so the first color is labeled as 1 and not 0.
    indices_color_choices = indices_color_choices + 1

    return simplified_image, indices_color_choices

def _denoise_image(image, h):
    denoised_image = cv.fastNlMeansDenoisingColored(
        src = image.astype(np.uint8),
        dst = None,
        h = h,
        hColor = h,
        templateWindowSize = 7,
        searchWindowSize = 21
    )
    return denoised_image

def simplify_image(image, 
                   color_list, 
                   config = default_config,
                   ):
    """
    Converts all colors in an image to the closest color in the color list.
    Denoises if required.
    
    Args:
      image: Image in the RGB color space as a 3D array.
      color_list: A list of tuples representing RGB values of allowed colors.
    
    Returns:
      A copy of the image with all colors replaced with the closest color in the list.
    """
    denoise = config["denoise"]
    denoise_h = config["denoise_h"]
    
    simplified_image, indices_color_choices = _choose_closest_colors(image, color_list)
    if denoise:
        # Denoising after simplifying image as denoising original image need not reduce the 
        # number of colors islands and also removed some key features from the original image.
        simplified_image = _denoise_image(simplified_image, denoise_h)
    
        # Simplying image again as denoising may have introduced new colors.
        simplified_image, indices_color_choices = _choose_closest_colors(simplified_image, color_list)

    return simplified_image, indices_color_choices