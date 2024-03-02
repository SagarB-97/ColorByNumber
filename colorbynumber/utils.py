from matplotlib import pyplot as plt

def show_image(image, cmap = None):
    if cmap:
        plt.imshow(image, cmap = cmap)
    else:
        plt.imshow(image)
    plt.axis('off')
    plt.show()

