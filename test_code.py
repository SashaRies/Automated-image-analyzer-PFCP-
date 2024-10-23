'''Sasha Ries
an area I put code I want to experiment with without changing code in other files'''

import numpy as np
import cv2
import os
from skimage import io
import finalizer
from skimage.filters import threshold_otsu, gaussian
from skimage.feature import canny
from skimage.color import rgb2gray
import cornerFinder as corner
import image_analyzer as img

image_in = "C:/Users/sries/onedrive/documents/programming/instron_automation/CM25CCB_ISTAtest1_original_files_only/CM25CCB_istatest1_10_100_50N.bmp"
folder_in = "C:/Users/sries/onedrive/documents/programming/instron_automation/CM25CCB_ISTAtest1_original_files_only"
test_folder = "C:/Users/sries/onedrive/documents/programming/instron_automation/Test_images"


def find_contours(pixels):
    # Convert the 2D array of pixel class objects to a numpy array
    image = np.array([[(pixels[i][j].getRed(),pixels[i][j].getGreen(),pixels[i][j].getBlue()) for j in range(len(pixels[0]))] for i in range(len(pixels))])
    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    # Canny edge detection
    edges = cv2.Canny(blurred, 50, 150)
    # Find contours
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    #The cv2.findContours method in Python's OpenCV library returns a list of contours, 
    #where each contour is a numpy array of (x, y) coordinates of boundary points of an object.
    return contours

def eigenCorner(image_file, out_dir):
    # Load the input image
    img = cv2.imread(image_file, cv2.IMREAD_COLOR)

    if img is None:
        print('Error: could not read image')
        return

    # Compute the minimum eigenvalue of the structure tensor at each pixel
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    eigenvalues = cv2.cornerMinEigenVal(gray, blockSize=30, ksize=3)

    # Normalize the eigenvalues to the range [0, 255]
    eigenvalues_norm = cv2.normalize(eigenvalues, None, 0, 255, cv2.NORM_MINMAX)

    # Apply a threshold to the normalized eigenvalues to detect corners
    threshold = 120
    corners = np.zeros_like(gray)
    corners[eigenvalues_norm > threshold] = 255

    # Dilate the corners to make them appear as bigger clumps of white pixels
    kernel = np.ones((6, 6), np.uint8)
    corners = cv2.dilate(corners, kernel, iterations=6)

    # Overlay the detected corners on the original image
    img_corners = np.copy(img)
    img_corners[corners > 0] = (0, 255, 0)
    # Construct the output file path
    out_file = os.path.join(out_dir, os.path.basename(image_file))

    # Save the output image as a .bmp file
    cv2.imwrite(out_file, img_corners)

    if np.count_nonzero(corners) == 0:
        print('No corners detected')
        return



def eigenCorner_red(image_file, out_dir):
        # Load the input image
    img = cv2.imread(image_file, cv2.IMREAD_COLOR)

    # Apply a color threshold to filter out all pixels that are not in the red color range
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower_red = np.array([0, 50, 50])
    upper_red = np.array([10, 255, 255])
    mask = cv2.inRange(hsv, lower_red, upper_red)

    # Combine the red color mask with the grayscale image of the input
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray_masked = cv2.bitwise_and(gray, gray, mask=mask)

    # Compute the minimum eigenvalue of the structure tensor at each pixel
    eigenvalues = cv2.cornerMinEigenVal(gray_masked, blockSize=25, ksize=3)

    # Normalize the eigenvalues to the range [0, 255]
    eigenvalues_norm = cv2.normalize(eigenvalues, None, 0, 255, cv2.NORM_MINMAX)

    # Apply a threshold to the normalized eigenvalues to detect corners
    threshold = 180
    corners = np.zeros_like(gray)
    corners[eigenvalues_norm > threshold] = 255

    # Dilate the corners to make them appear as bigger clumps of white pixels
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (6, 6))
    iterations = 2
    corners = cv2.dilate(corners, kernel, iterations=iterations)

    # Overlay the detected corners on the original image
    img_corners = np.copy(img)
    img_corners[corners > 0] = (0, 255, 0)
    
    # Construct the output file path
    out_file = os.path.join(out_dir, os.path.basename(image_file))

    # Save the output image as a .bmp file
    cv2.imwrite(out_file, img_corners)

def edge_finder(image_file, out_dir):
    # Load the image
    image = cv2.imread(image_file)

    # Convert the image to the HSV color space
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Define the red and white color ranges
    red_lower = np.array([0, 50, 50])
    red_upper = np.array([10, 255, 255])
    white_lower = np.array([0, 0, 220])
    white_upper = np.array([255, 30, 255])

    # Threshold the image to get the red and white regions
    red_mask = cv2.inRange(hsv, red_lower, red_upper)
    white_mask = cv2.inRange(hsv, white_lower, white_upper)

    # Combine the red and white masks to get the final mask
    mask = cv2.bitwise_or(red_mask, white_mask)

    # Detect the edges of the object
    edges = cv2.Canny(mask, 100, 200)

    # Apply a dilation operation to make the edges thicker
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    dilated_edges = cv2.dilate(edges, kernel)

    # Create a mask from the edges
    mask = cv2.merge([dilated_edges, dilated_edges, dilated_edges])

    # Overlay the mask on the original image with green color
    overlay = cv2.addWeighted(image, 0.5, mask, 0.5, 0)
    out_file = os.path.join(out_dir, os.path.basename(image_file))
    cv2.imwrite(out_file, overlay)

def find_edge_skimage(image_in, out_dir):
    # Load the image
    image = io.imread(image_in)

    # Convert the image to grayscale
    #default weight is Y = 0.2125 R + 0.7154 G + 0.0721 B
    custom_weights = [0.25, 1, 1]
    gray_image = np.dot(image[...,:3], custom_weights)

    # Normalize the resulting grayscale image
    gray_image /= np.max(gray_image)
    #gray_image = rgb2gray(image, weights=custom_weights)

    # Apply a Gaussian blur to smooth the image
    blurred_image = gaussian(gray_image, sigma=35)

    # Threshold the image using Otsu's method
    # The threshold_otsu method determines a therhsold value based on image backround and object color intensity
    threshold = 0.72*threshold_otsu(blurred_image)
    binary_image = blurred_image > threshold

    # Apply the Canny edge detector to the binary image
    # canny method return a numpy array of 0 and 1 with the same dimensions of the image. 1 go where the detected edges are
    edge_image = canny(binary_image, sigma=2)

    # Create a new image with the edges marked in green
    color_image = image.copy()
    color_image[edge_image == 1, 1] = 255

    # Save the image in the new folder
    '''os.makedirs(out_dir, exist_ok=True)
    filename = os.path.basename(image_in)
    out_path = os.path.join(out_dir, filename)
    io.imsave(out_path, color_image)'''
    return edge_image

    # Display the edge image
    #io.imshow(color_image)
    #io.show()

def binary_array_to_tuples(binary_array, clumpSize):
    indices = np.argwhere(binary_array == 1)
    tuples = [(int(i[0]/clumpSize), int(i[1]/clumpSize)) for i in indices]
    # Iterate over each tuple in the array
    return tuples

def find_corners(image_in, out_dir, index):
    clumpSize = 4
    imager = img.Image_analyzer(out_dir)
    pixelGrid = imager.makePixelGrid(image_in)
    pixelGrid = imager.clump(pixelGrid, clumpSize)
    edge_grid = find_edge_skimage(image_in, out_dir)
    edge_list = binary_array_to_tuples(edge_grid, clumpSize)
    c = corner.CornerFinder(dark=105, bright=100, neighborDistance=28)
    cornerList = c.find_corners_new(edge_list, pixelGrid, redRatio = 1.2)
    corners = c.determineCorner(cornerList)
    imager.markGrid([(corners[0].getX(),corners[0].getY()),(corners[1].getX(),corners[1].getY())], 25, "newest_test_image" + str(index))


'''The GaussianBlur method is a function in the OpenCV (Open Source Computer Vision Library) library in Python that performs Gaussian smoothing on an image. Gaussian smoothing is a commonly used technique to reduce noise in an image by replacing each pixel value with the average of the surrounding pixels.

The Gaussian blur works by convolving an image with a Gaussian kernel, which is a two-dimensional kernel with a Gaussian function as its values. The Gaussian function has a bell-shaped curve that gives more weight to the pixels that are closer to the center and less weight to the pixels that are farther away.

The GaussianBlur method takes in three parameters:

The image to be blurred (in this case, the grayscale image)
The size of the kernel to be used for the Gaussian smoothing, specified as a tuple (height, width)
The standard deviation of the Gaussian function, specified as a scalar value
The method returns a smoothed version of the input image. The larger the kernel size and the standard deviation, the stronger the smoothing effect will be.'''

'''OpenCV: OpenCV (Open Source Computer Vision) is a popular library for computer vision and image processing. 
It provides various methods for corner detection, such as Harris corner detection, Shi-Tomasi corner detection, and FAST corner detection. 
You can use the cv2.cornerHarris(), cv2.goodFeaturesToTrack(), or cv2.FAST() functions to detect corners in an image.
Scikit-image: Scikit-image is a library for image processing and computer vision. It provides various functions for corner detection, such as Harris corner detection, 
Shi-Tomasi corner detection, and corner peak finding. You can use the skimage.feature.corner_harris(), skimage.feature.corner_shi_tomasi(), 
or skimage.feature.corner_peaks() functions to detect corners in an image. Mahotas: Mahotas is a library for computer vision and image processing. 
It provides various methods for corner detection, such as Harris corner detection, Shi-Tomasi corner detection, and Minimum Eigenvalue corner detection. 
You can use the mahotas.features.corner_harris(), mahotas.features.corner_min_eigenvalue(), or mahotas.features.corner_peaks() functions to detect corners in an image.
CornerNet-Lite: CornerNet-Lite is a lightweight library for corner detection in images. It provides a fast and accurate method for detecting corners in an image. 
You can use the cornernet_lite.detect_corners() function to detect corners in an image.'''

def test_main():
    '''im = img.Image_analyzer(test_folder)
    pixelImage = im.makePixelGrid(image_in)
    contours = find_contours(pixelImage)
    list_of_edgeXY = np.concatenate(contours).tolist()
    list_of_edgeXY = [i[0] for i in list_of_edgeXY]
    im.markGrid(pixelImage, list_of_edgeXY, 20)'''

    '''a = 0
    for images in os.listdir(folder_in):
        if (images.endswith(".bmp") and "test_image" not in images): #check if the image ends with bpm
            a += 1
            #find_edge_skimage(folder_in + '/' + images, test_folder)
            find_corners(folder_in + '/' + images, test_folder, a)'''
test_main()