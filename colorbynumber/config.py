default_config = {
    # If True, the image will be denoised after simplification.
    "denoise": True,
    
    # Determines the order of denoising.
    # Options: "before_simplify", "after_simplify"
    "denoise_order": "before_simplify",

    # If True, the image will be simplified using kmeans clustering.
    # And then the colors will be matched to closest color in the palette.
    "apply_kmeans": True,

    # Type of denoising to be used.
    # Options: "fastNlMeansDenoisingColored", "gaussianBlur", "blur"
    "denoise_type": "gaussianBlur",
    # Size of the kernel used for gaussian blur.
    "blur_size": 51,
    # h parameter for fastNlMeansDenoisingColored.
    "denoise_h": 200,

    # Padding around the borders of the image.
    "border_padding": 2,

    # Determines the size of the kernel used for open morphological operation.
    # This removes small islands and isthmuses.
    "open_kernel_size": 3,


    # Color islands with area less than this threshold will be ignored.
    # The value is a percentage of the total area of the image.
    "area_perc_threshold": 0.02,

    # If True, all shapes with perimeter to area ratio of less than
    # arc_length_area_ratio_threshold will be ignored.
    "check_shape_validity": True,
    "arc_length_area_ratio_threshold": 1,

    # Color of the border around around color islands.
    "border_color": (181, 181, 181),

    # Font for the numbers shown in color islands.
    "font_size": 1,
    "font_color": (140, 140, 140),
    "font_thickness": 2,
}