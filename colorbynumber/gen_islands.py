
def _is_same_color(color1, color2):
    """Check if two colors are the same.
    
    Args:
        color1 (list): A tuple representing the RGB values of a color (R, G, B).
        color2 (list): A tuple representing the RGB values of a color (R, G, B).
    Returns:
        bool: True if the colors are the same, False otherwise.
    """
    all_same = True
    for i in range(3):
        all_same = all_same and color1[i] == color2[i]
    return all_same


def _get_neighbors(pixel, image_shape):
    """Get the neighbors of a pixel.
    
    Args:
        pixel (tuple): A tuple representing the row and column of a pixel.
        image_shape (tuple): A tuple representing the number of rows and columns in the image.
    Returns:
        set: A set of tuples representing the row and column of the neighbors.
    """
    row, col = pixel
    neighbors = set()
    if row > 0:
        neighbors.add((row - 1, col))
    if row < image_shape[0] - 1:
        neighbors.add((row + 1, col))
    if col > 0:
        neighbors.add((row, col - 1))
    if col < image_shape[1] - 1:
        neighbors.add((row, col + 1))
    return neighbors

def get_islands(simplified_image, color_list):
    """Get the numbered islands from an image.
    
    Args:
        image (np.array): Numpy image.
        color_list (list): A list of string re allowed colors.
    Returns:
        islands (list): A list of islands where each island is a tuple consisting of
         1. the color name
         2. a list of tuples representing the row and column of the pixels in the island.
    """
    islands = []
    visited_pixels = set()
    current_color = simplified_image[0, 0]
    stack_to_visit = set()
    # Go to all the neighbors of the current pixel.
    # If the neighbor has the same color, add it to the island and visit its neighbors.
    # If the neighbor has a different color, add it to the stack to visit later.
    stack_to_visit.add((0, 0))
    while stack_to_visit:
        pixel = stack_to_visit.pop()
        print(pixel)
        if pixel in visited_pixels:
            continue
        current_color = simplified_image[pixel]
        visited_pixels.add(pixel)
        island = [pixel]
        neighbor_stack = _get_neighbors(pixel, simplified_image.shape)
        while len(neighbor_stack)>0:
            neighbor = neighbor_stack.pop()
            (neighbor_row, neighbor_col) = neighbor
            if neighbor in visited_pixels:
                continue
            if _is_same_color(simplified_image[neighbor_row][neighbor_col], current_color):
                island.append(neighbor)
                visited_pixels.add(neighbor)
                neighbor_stack = neighbor_stack.union(_get_neighbors(neighbor, simplified_image.shape))
            else:
                stack_to_visit.add(neighbor)
            # Remove any visited pixels from the stack
            neighbor_stack = neighbor_stack - visited_pixels
            print(len(neighbor_stack))
            print("visited pixels")
            print(len(visited_pixels))
        islands.append((color_list[current_color], island))
        # Debug: size of visited pixels
        stack_to_visit = stack_to_visit - visited_pixels
        print("visited islands")
        print(len(islands))
    return islands