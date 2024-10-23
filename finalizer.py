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

    def refineRows(self, x, y, size, pixelGrid, dark, red, color_range = 50):
        '''creates a an array of rows where the end of each horizontal row is estimated to the edge between polymer and background (each row length varies)'''
        #determine a baseline black or red color value for void (background) pixels
        if len(pixelGrid) != 2*size:
            section = [row[x-size:x+size+1] for row in pixelGrid[y-size:y+size+1]]
        #to save on runtime during/if using recursion
        else: section = pixelGrid
        
        newGrid = []
        for row in section:
            i = 0
            endPixel = 0
            newRow = []
            while endPixel < 5 and i < len(row):
                weighted_color = (row[i].getGreen()*1.5 + row[i].getBlue()*1.5 + row[i].getRed()*0.5)/3
                #if its at the right darkness then check if its red enough
                if weighted_color > dark and weighted_color < dark + color_range:
                #if weighted_color > dark:
                    if row[i].getRed() < red:
                        endPixel += 1
                #otherwise check if its too bright overall
                    else:
                        endPixel = 0
                else:
                    endPixel += 0
                #otherwise its dark enough to be background
                newRow.append(row[i])
                i += 1
            if len(newRow) > 18:
                newGrid.append(newRow)
        #organize into rows that could possibly have the cracktip
        if len(newGrid) > 5:    
            return newGrid
        else: return self.refineRows(x, y, size, pixelGrid, dark, red+1, color_range+1)

    def finalize(self, newGrid, sweepDist = 14):
        #sweep 15 rows above row and 15 rows below. do this for every row
        curRow = 0
        biggestSection = (0,None)
        for row in newGrid:
            voidLength = 0
            #print("this is the length of each row" + str(len(row)))
            if curRow > sweepDist and curRow < len(newGrid) - sweepDist:
                for j in range(sweepDist*2):
                    horizontal = newGrid[(curRow - sweepDist) + j]
                    voidLength += len(horizontal)
                if voidLength > biggestSection[0]:
                    biggestSection = (voidLength, row[-1])
            curRow += 1
        #return the pixel at the estimated cracktip
        return biggestSection[1]

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
            

    