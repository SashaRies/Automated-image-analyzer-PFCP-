'''
Sasha Ries
12/11/2022
processe to finalize location of cracktip from estimate of cracktip (go from within 30 pixels to within 10)'''

import image_analyzer as img
import os

Folder_out = "C:/Users/sries/onedrive/documents/programming/instron_automation/Test_images"
folder_in = "C:/Users/sries/onedrive/documents/programming/instron_automation/image holder"
#folder_in = "C:/Users/sries/onedrive/documents/programming/instron_automation/CM25CCB_ISTAtest1_original_files_only"

class Finalizer():

    def refineRows(self, x, y, size, pixelGrid, dark, red, color_range=50):
        '''Creates an array of rows where the end of each horizontal row is estimated to the edge between polymer and background (each row length varies).'''
        
        # Determine a section to process based on the pixel grid size
        section = pixelGrid if len(pixelGrid) == 2 * size else [row[x - size:x + size + 1] for row in pixelGrid[y - size:y + size + 1]]
        newGrid = []

        for row in section:
            endPixel = 0
            newRow = []
            for pixel in row:
                weighted_color = (pixel.getGreen() * 1.5 + pixel.getBlue() * 1.5 + pixel.getRed() * 0.5) / 3
                
                # Check if the color falls within the acceptable range
                if dark < weighted_color < dark + color_range:
                    if pixel.getRed() < red:
                        endPixel += 1
                    else:
                        endPixel = 0  # Reset end pixel count if the red value is sufficient
                else:
                    endPixel += 0  # This line is unnecessary; could be omitted
        
                newRow.append(pixel)
                if endPixel >= 5:  # Stop processing if we've observed enough non-red pixels
                    break

            if len(newRow) > 18:
                newGrid.append(newRow)
        
        # Recursion if there are not enough rows
        if len(newGrid) > 5:    
            return newGrid
        else:
            return self.refineRows(x, y, size, pixelGrid, dark, red + 1, color_range + 1)


    def finalize(self, newGrid, sweepDist=14):
        '''Sweeps rows above and below to find the longest sequence of rows.'''
        biggestSection = (0, None)

        for curRow in range(len(newGrid)):
            if sweepDist < curRow < len(newGrid) - sweepDist:
                voidLength = sum(len(newGrid[curRow - sweepDist + j]) for j in range(sweepDist * 2))

                if voidLength > biggestSection[0]:
                    biggestSection = (voidLength, newGrid[curRow][-1])  # Store the last pixel of the current row

        return biggestSection[1]  # Return the pixel at the estimated crack tip


    def complete(self, pixelGrid, x, y, size, dark, green, sweepDist):
        newGrid = self.refineRows(x, y, size, pixelGrid, dark, green)
        return self.finalize(newGrid, sweepDist)
    


if __name__ == "__main__":
    imager = img.Image_analyzer(folder_out = Folder_out)
    finaler = Finalizer()
    a = 0
    for images in os.listdir(folder_in):
        if (images.endswith(".bmp") and "test_image" not in images): #check if the image ends with bpm
            a += 1
            pixelGrid = imager.makePixelGrid(folder_in + '/' + images)
            #pixelGrid = imager.clump(pixelGrid, 4)
            finalPoint = finaler.complete(pixelGrid, int(imager.width/2), int(imager.height/2), int(imager.width/2), 100, 70, 15)
            #print(finalPoint.getRed(), finalPoint.getGreen(), finalPoint.getBlue())
            print(finalPoint.getX())
            imager.markGrid(pixelGrid, [(finalPoint.getX(),finalPoint.getY())], 25, a)
            

    