default_config = {
    # If True, the image will be denoised after simplification.
    "denoise": True,

    # Higher values will result in more aggressive denoising.
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
    "font_size": 0.3,
    "font_color": (140, 140, 140),
    "font_thickness": 1,
}