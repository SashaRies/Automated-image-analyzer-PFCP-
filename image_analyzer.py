'''
Sasha Ries
9/27/2022
processe to convert bmp images into readable data'''

import pixel as p
from PIL import Image
import numpy as np
import os

Folder_out = "C:/Users/sries/onedrive/documents/programming/instron_automation/Test_images"

class Image_analyzer():
    '''This class takes images and manipulates them into a 2D array of pixel objects and vice versa'''
    def __init__(self, width = 4632, height = 3488, folder_out = Folder_out):
        self.width = width
        self.height = height
        self.folder_out = folder_out


    def makePixelGrid(self, image):
        '''creates a 2D numpy array of pixel objects'''
        img = Image.open(image)
        self.width = img.width
        self.height = img.height

        pixels = np.array(img) #Convert the image to a 2D numpy array of pixel values

        #shape[0] gives number of lists in numpy array and shape[1] gives length of each list
        grid = np.empty(shape=pixels.shape[:2], dtype=p.Pixel)
        for x in range(pixels.shape[0]):
            for y in range(pixels.shape[1]):
                grid[x][y] = p.Pixel(y, x, x, y, float((int(pixels[x][y][0]) + int(pixels[x][y][1]) + int(pixels[x][y][2]))/3), 
                                    pixels[x][y][0], pixels[x][y][1], pixels[x][y][2])
        #return a numpy array to decrease run time in future methods 
        return grid
        
    def clump(self, pixelGrid, clumpSize):
        '''takes a grid of pixel objects and clumps them into clumpsize*clumpSize sized blocks'''
        newGrid = np.empty(shape=(self.height//clumpSize, self.width//clumpSize), dtype=p.Pixel) #make an empty grid then fill it        
        for i in range(0, self.height, clumpSize):
            for j in range(0, self.width, clumpSize):
                red, green, blue, color = 0, 0, 0, 0
                if i + clumpSize < self.height and j + clumpSize < self.width:
                    for g in range(clumpSize):
                        for h in range(clumpSize):
                            red += pixelGrid[i + g][j + h].getRed()
                            green += pixelGrid[i + g][j + h].getGreen()
                            blue += pixelGrid[i + g][j + h].getBlue()
                            color += pixelGrid[i + g][j + h].getColor()
                    clump = p.Pixel(i//clumpSize, j//clumpSize, j, i, color//(clumpSize**2), red//(clumpSize**2), green//(clumpSize**2), blue//(clumpSize**2))
                    newGrid[i//clumpSize][j//clumpSize] = clump

        #check if there are rows or columns with empty values and remove them if there are
        if np.any(newGrid[-1,:] == None) or np.any(newGrid[:,-1] == None):
            newGrid = np.delete(newGrid,-1,axis = 0)
            newGrid = np.delete(newGrid,-1,axis = 1)

        return newGrid #returns another numpy array but now with averaged values for each clumpSize*clumpSize block of pixels


    def markGrid(self, pixelGrid, coords, size, image_ind = None, image_name = None):#coords is a list of (x,y) touples
        '''creates a red square(size*size) at each supplied coordinate and creates a new marked image in self.folder_out'''
        newGrid = pixelGrid
        height, width = newGrid.shape[:2]
        # create an empty PIL image with mode RGB
        img = Image.new(mode='RGB', size=(width, height))
        
        #coordinates of grid are (y,x) -- grid[y][x]
        for coord in coords:
            if coord[1] + size < self.height and coord[0] + size < self.width:
                for i in range(size):
                    for j in range(size):
                        #this will make only the red value 255 and the green and blue values 0
                        newGrid[coord[1] + i][coord[0]+ j].setRed(255)
                        newGrid[coord[1] + i][coord[0]+ j].setGreen(0)
                        newGrid[coord[1] + i][coord[0]+ j].setBlue(0)

        # set the pixels of the image using the pixel array
        for i in range(height-1):
            for j in range(width-1):
                pixel_value = tuple([newGrid[i][j].getRed(),newGrid[i][j].getGreen(),newGrid[i][j].getBlue()])
                img.putpixel((j, i), pixel_value)

        #now determine how to name the markedimage
        if image_name and image_ind:
            name = str(image_name) + str(image_ind) +  ".bmp"
        elif image_name:
            name = str(image_name) +  ".bmp"
        elif image_ind:
            name = "Checked_image" + str(image_ind) + ".bmp"
        else: name = "Checked_image.bmp"
        img.save(os.path.join(self.folder_out, name))#save the marked image
        

    def cutNewImage(self, pixelGrid, xMin, xMax, yMin, yMax, image_ind = None):
        '''cuts a section of the image from xMin to xMax and yMin to yMax and creates a new image with it'''
        # get the width and height of the cropped section
        width, height = xMax - xMin, yMax - yMin
        img = Image.new(mode='RGB', size=(width, height))

        '''makes a bmp file out of a grid of subPixels'''
        for i in range(xMin,xMax):
            for j in range(yMin,yMax):
                pixel_value = tuple(pixelGrid[i][j].getRed(),pixelGrid[i][j].getGreen(),pixelGrid[i][j].getBlue())
                img.putpixel((j, i), pixel_value)
        if image_ind:
            name = "Crack_Zoomed" + str(image_ind) + ".bmp"
        else: name = "Crack_Zoomed.bmp"
        img.save(os.path.join(self.folder_out, name))



    def set_dx_dy(self, pixel_grid):
        '''method for adding a differential rate of color change in the x and y direction for each pixel object'''
        height, width = len(pixel_grid), len(pixel_grid[0])
        #remove 1 row and 1 column so indexes dont go out of bounds
        for i in range(height-1):
            for j in range(width-1):
                red_x = int(pixel_grid[i][j+1].getRed()) - int(pixel_grid[i][j].getRed())
                red_y = int(pixel_grid[i+1][j].getRed()) - int(pixel_grid[i][j].getRed())
                green_x = int(pixel_grid[i][j+1].getGreen()) - int(pixel_grid[i][j].getGreen())
                green_y = int(pixel_grid[i+1][j].getGreen()) - int(pixel_grid[i][j].getGreen())
                blue_x = int(pixel_grid[i][j+1].getBlue()) - int(pixel_grid[i][j].getBlue())
                blue_y = int(pixel_grid[i+1][j].getBlue()) - int(pixel_grid[i][j].getBlue())
                color_x = int(pixel_grid[i][j+1].getColor()) - int(pixel_grid[i][j].getColor())
                color_y = int(pixel_grid[i+1][j].getColor()) - int(pixel_grid[i][j].getColor())

                pixel_grid[i][j].setDiff_red(red_x, red_y)
                pixel_grid[i][j].setDiff_green(green_x, green_y)
                pixel_grid[i][j].setDiff_blue(blue_x, blue_y)
                pixel_grid[i][j].setDiff_color(color_x, color_y)
            #each pixel will now have a change in rgb value in both x and y direction (used for gradients)
        return pixel_grid