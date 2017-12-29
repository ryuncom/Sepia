import sys
import numpy as np
from scipy import stats
from PIL import Image

def ambient(im):
    width, height = im.size
    arr = np.asarray(im)
    row, col, vals = arr.shape

    # arrays to store RGB values
    red_arr = [[0 for x in range(col)] for y in range(row)]
    green_arr = [[0 for x in range(col)] for y in range(row)]
    blue_arr = [[0 for x in range(col)] for y in range(row)]
    i = 0
    for r in range(0, row):
        for c in range(0, col):
            red_arr[r][c] = arr[r][c][0]
            green_arr[r][c] = arr[r][c][1]
            blue_arr[r][c] = arr[r][c][2]
    
    buffer = 10
    max_vals_R = findMode(buffer, red_arr)
    max_vals_G = findMode(buffer, green_arr)
    max_vals_B = findMode(buffer, blue_arr)

    new_red = convertVals(np.array(red_arr), max_vals_R)
    new_green = convertVals(np.array(green_arr), max_vals_G)
    new_blue = convertVals(np.array(blue_arr), max_vals_B)
    
    new_arr = [[[0 for v in range(3)] for c in range(col)] for r in range(row)]
    for r in range(0, row):
        for c in range(0, col):
            new_arr[r][c][0] = new_red[r][c]
            new_arr[r][c][1] = new_green[r][c]
            new_arr[r][c][2] = new_blue[r][c]

    return Image.fromarray(np.array(new_arr))


# calculate the most buffer-many frequent values
def findMode(buffer, arr):
    max_vals = [0 for x in range(buffer)]
    
    values,counts = np.unique(arr,return_counts=True)
    counts_sort = np.sort(-counts, kind='quicksort', order=None)
    counts_sort = -counts_sort
    
    for i in range(0, buffer):
        max_vals[i] = values[((np.where(counts == counts_sort[i]))[0][0])]
    
    return max_vals

def convertVals(arr, max_val):
    for i in range(arr.shape[0]):
        for j in range(arr.shape[1]):
            if arr[i][j] in max_val:
                arr[i][j] = (arr[i][j] + 128) % 2
    return arr

# Main
if __name__ == "__main__":
    im = Image.open('/Users/annielee/Desktop/Sepia/Sepia_local/PythonOnXCode/4.png')
    newim = ambient(im)
    newim.show()
