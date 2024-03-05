default_config = {
    # If True, the image will be denoised after simplification.
    "denoise": True,

    # Higher values will result in more aggressive denoising.
    "denoise_h": 100,

    # Padding around the borders of the image.
    "border_padding": 2,

    # Color islands with area less than this threshold will be ignored.
    # The value is a percentage of the total area of the image.
    "area_perc_threshold": 0.05,

    # If True, all shapes with perimeter to area ratio of less than
    # arc_length_area_ratio_threshold will be ignored.
    "check_shape_validity": True,
    "arc_length_area_ratio_threshold": 1,

    # Color of the border around around color islands.
    "border_color": (0, 0, 0),

    # Font for the numbers shown in color islands.
    "font_size": 0.5,
    "font_color": (0, 0, 0),
    "font_thickness": 2,
}