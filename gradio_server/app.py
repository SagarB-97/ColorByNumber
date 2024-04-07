import gradio as gr

from colorbynumber.main import ColorByNumber
from colorbynumber.config import default_config
from . import doc

MAX_NUM_COLORS = 50 # Mostly for UI purposes

def get_color_by_number(image_path, number_of_colors, 
                        is_automatic_colors, num_colors,
                        denoise_flag, denoise_order, denoise_type,
                        blur_size, denoise_h,
                        open_kernel_size, area_perc_threshold,
                        check_shape_validity, arc_length_area_ratio_threshold,
                        *color_list):
    # Convert each color to r,g,b tuple
    color_list = color_list[:num_colors]
    def _hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    color_list = [_hex_to_rgb(h) for h in color_list]

    # Update config
    config = default_config.copy()
    config["denoise"] = denoise_flag
    config["denoise_order"] = denoise_order
    config["denoise_type"] = denoise_type
    config["blur_size"] = blur_size
    config["denoise_h"] = denoise_h
    config["open_kernel_size"] = open_kernel_size
    config["area_perc_threshold"] = area_perc_threshold
    config["check_shape_validity"] = check_shape_validity
    config["arc_length_area_ratio_threshold"] = arc_length_area_ratio_threshold

    if is_automatic_colors:
        colorbynumber_obj = ColorByNumber(
            image_path = image_path,
            num_colors = number_of_colors,
            config = config,
        )
    else:
        colorbynumber_obj = ColorByNumber(
            image_path = image_path, 
            color_list = color_list,
            config = config,
        )

    numbered_islands = colorbynumber_obj.create_color_by_number()
    return numbered_islands, \
        colorbynumber_obj.generate_color_legend(), \
        colorbynumber_obj.simplified_image

with gr.Blocks(title = "Color by number") as demo:
    with gr.Row():
        # Inputs
        with gr.Column():
            image_path = gr.Image(type="filepath")
            image_examples = gr.Examples(
                examples=[
                    ["ExampleImages/Macaw.jpeg"],
                    ["ExampleImages/Grids.png"],
                ],
                inputs=[image_path]
            )

            # Color selection
            gr.Markdown(doc.color_selection_block())
            is_automatic_colors = gr.Checkbox(label = "Automatic colors", value = True)
            number_of_colors = gr.Number(precision=0, label = "Number of colors", value=10)
            
            # Color pickers
            color_pickers = []
            with gr.Row(visible=False) as color_picker_row:
                for i in range(MAX_NUM_COLORS):
                    color_pickers.append(gr.ColorPicker(label = str(i + 1)))

            # Toggle visibility of color pickers
            def _change_number_of_colors(number_of_colors):
                return [gr.update(visible=True)]*number_of_colors + \
                    [gr.update(visible=False)]*(MAX_NUM_COLORS - number_of_colors)
            def _get_color_selection_ui(is_automatic_colors_checked, number_of_colors):
                if is_automatic_colors_checked:
                    return [gr.update(visible=False)] + _change_number_of_colors(0)
                else:
                    return [gr.update(visible=True)] + _change_number_of_colors(number_of_colors)

            is_automatic_colors.change(
                _get_color_selection_ui,
                inputs = [is_automatic_colors, number_of_colors],
                outputs=[color_picker_row] + color_pickers,
            )     
            number_of_colors.change(
                fn=_change_number_of_colors,
                inputs=[number_of_colors],
                outputs=color_pickers,
            )

            # Config UI
            gr.Markdown(doc.parameters_block_header())
            with gr.Accordion(label="Configuration") as config_accordion:
                with gr.Tab(label="Denoise") as denoise_tab:
                    # Denoise parameters
                    gr.Markdown(doc.denoise_block_header())
                    denoise_flag = gr.Checkbox(
                            label = "Denoise", 
                            value = default_config["denoise"]
                            )
                    with gr.Group() as denoise_params:
                        with gr.Row():
                            denoise_order = gr.Dropdown(
                                label = "Denoise order", 
                                choices = ["before_simplify", "after_simplify"], 
                                value = default_config["denoise_order"],
                                )
                            denoise_type = gr.Dropdown(
                                label = "Denoise type", 
                                choices = ["fastNlMeansDenoisingColored", "gaussianBlur", "blur"], 
                                value = default_config["denoise_type"],
                                info="Algorithm to be used for denoising"
                                )
                        show_denoise_h = False
                        if default_config["denoise_type"] == "fastNlMeansDenoisingColored":
                            show_denoise_h = True

                        with gr.Row():
                            blur_size = gr.Slider(
                                label = "Blur size",
                                minimum = 3,
                                maximum = 101,
                                step=2, 
                                value = default_config["blur_size"],
                                info="Larger values will denoise more",
                                visible=(not show_denoise_h)
                                )
                            denoise_h = gr.Slider(
                                label = "h", 
                                value = default_config["denoise_h"],
                                info="Larger values will denoise more",
                                visible=show_denoise_h
                                )
                    
                    def _toggle_h_blur_size_visibility(event: gr.SelectData):
                        if event.value == "fastNlMeansDenoisingColored":
                            # Show denoise_h, hide blur_size
                            return [gr.update(visible=False), gr.update(visible=True)]
                        else:
                            # Show blur_size, hide denoise_h
                            return [gr.update(visible=True), gr.update(visible=False)]
                    denoise_type.select(
                        fn = _toggle_h_blur_size_visibility,
                        inputs = None,
                        outputs = [blur_size, denoise_h]
                        )
                        
                    denoise_flag.change(
                        fn = lambda x: gr.update(visible=x),
                        inputs = [denoise_flag],
                        outputs = denoise_params
                    )

                with gr.Tab(label = "Simplify") as simplify_tab:    
                
                    # Simplification parameters
                    gr.Markdown(doc.simplify_islands_parameters())
                    open_kernel_size = gr.Slider(
                        label = "Open kernel size",
                        minimum = 3,
                        maximum = 51,
                        step=2, 
                        value = default_config["open_kernel_size"],
                        info="Larger the value, cleaner the image. But too large values can remove important details."
                    )
                    area_perc_threshold = gr.Slider(
                        label = "Area Percentage threshold",
                        minimum = 0,
                        maximum = 10,
                        step=0.01, 
                        value = default_config["area_perc_threshold"],
                        info="Islands which cover a percentage area less than this threshold will be removed."
                    )

                    check_shape_validity = gr.Checkbox(
                        label = "Remove thin islands", 
                        value = default_config["check_shape_validity"],
                    )
                    arc_length_area_ratio_threshold = gr.Slider(
                        label = "Arc length to Area ratio",
                        minimum = 0,
                        maximum = 10,
                        step=0.01, 
                        value = default_config["arc_length_area_ratio_threshold"],
                        info="Smaller value removes more islands.",
                        visible=default_config["check_shape_validity"]
                    )
                    check_shape_validity.change(
                        fn = lambda x: gr.update(visible=x),
                        inputs = [check_shape_validity],
                        outputs = [arc_length_area_ratio_threshold]
                    )

            # Submit button
            submit_button = gr.Button("Submit")

        # Outputs
        with gr.Column():
            color_by_number_image = gr.Image(label = "Color by number")
            legend_image = gr.Image(label = "Legend")
            simplified_image = gr.Image(label = "Simplified image")

        # Submit button callback
        submit_button.click(
            fn = get_color_by_number,
            inputs = [
                image_path, 
                number_of_colors,
                is_automatic_colors,
                number_of_colors,
                denoise_flag,
                denoise_order,
                denoise_type,
                blur_size,
                denoise_h,
                open_kernel_size,
                area_perc_threshold,
                check_shape_validity,
                arc_length_area_ratio_threshold,
                *color_pickers
                ],
            outputs = [color_by_number_image, legend_image, simplified_image]
        )

demo.launch()
