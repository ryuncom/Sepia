from PIL import Image

#reference: https://www.codementor.io/isaib.cicourel/image-manipulation-in-python-du1089j1u

# Open an Image:
def open_image(path):
    newImage = Image.open(path)
    return newImage


# Save an Image:
def save_image(image, path):
    image.save(path, 'png')


# Create a new image with the given size:
def create_image(i, j):
    image = Image.new("RGB", (i, j), "white")
    return image


# Get the pixel from the given image:
def get_pixel(image, i, j):
    # check if the positions are inside image bounds:
    width, height = image.size
    if i > width or j > height:
        return None
    
    # Get Pixel
    pixel = image.getpixel((i, j))
    return pixel


def apply_filter(image, filter):
    """" applies desired filter and returns a new image """
    filteredImage = create_image(image)
    # Apply Filter:
    # FIXME!
    
    return filteredImage

# Main
if __name__ == "__main__":
    
    #takes user input(image directory, filter type)
    #FIXME!
    imgDir = ""
    filterType = ""
    
    # Load Image:
    original = open_image('/Users/annielee/Desktop/Sepia/PythonOnXCode/'+ imgDir + '.png')
    
    # Apply the Desired Filter:
    newim = apply_filter(original, filterType)
    
    # Show Image:
    newim.show()

