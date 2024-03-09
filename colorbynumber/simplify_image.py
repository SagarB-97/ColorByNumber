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

def _kmeans_simplify_image(image, num_colors):
    Z = image.reshape((-1,3))
 
    # convert to np.float32
    Z = np.float32(Z)
    
    # define criteria, number of clusters(K) and apply kmeans()
    criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    K = num_colors
    ret,label,center=cv.kmeans(Z,K,None,criteria,10,cv.KMEANS_RANDOM_CENTERS)
    
    # Now convert back into uint8, and make original image
    center = np.uint8(center)
    res = center[label.flatten()]
    res = res.reshape((image.shape))

    simplified_image = res
    indices_color_choices = label.reshape((image.shape[:2])) + 1
    color_list = center

    return simplified_image, indices_color_choices, color_list

def _denoise_image(image, h, denoise_type, blur_size = None):
    if denoise_type == "fastNlMeansDenoisingColored":
        denoised_image = cv.fastNlMeansDenoisingColored(
            src = image.astype(np.uint8),
            dst = None,
            h = h,
            hColor = h,
            templateWindowSize = 7,
            searchWindowSize = 21
        )
    elif denoise_type == "gaussianBlur":
        kernel = (blur_size, blur_size)
        denoised_image = cv.GaussianBlur(image, kernel, 0)
    
    elif denoise_type == "blur":
        kernel = (blur_size, blur_size)
        denoised_image = cv.blur(image, kernel)

    return denoised_image

def simplify_image(image, 
                   color_list = None,
                   num_colors = None, 
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
    if config["denoise"] and (config["denoise_order"] == "before_simplify"):
        image = _denoise_image(
            image=image, 
            h = config["denoise_h"], 
            denoise_type = config["denoise_type"], 
            blur_size = config["blur_size"],
            )

    if color_list is None:
        # Use kmeans to simplify the image to the specified number of colors.
        simplified_image, indices_color_choices, color_list = _kmeans_simplify_image(image, num_colors)

    else:
        if config["apply_kmeans"]:
            image, indices_color_choices, color_list_kmeans = _kmeans_simplify_image(image, len(color_list))
        simplified_image, indices_color_choices = _choose_closest_colors(image, color_list)
    

    if config["denoise"] and (config["denoise_order"] == "after_simplify"):
        # Denoising after simplifying image as denoising original image need not reduce the 
        # number of colors islands and also removed some key features from the original image.
        simplified_image = _denoise_image(
            simplified_image, 
            h = config["denoise_h"], 
            denoise_type = config["denoise_type"], 
            blur_size = config["blur_size"],
            )
    
        # Simplying image again as denoising may have introduced new colors.
        simplified_image, indices_color_choices = _choose_closest_colors(
            simplified_image, 
            color_list
            )

    return simplified_image, indices_color_choices, color_list