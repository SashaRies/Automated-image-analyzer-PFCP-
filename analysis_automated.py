'''
Sasha Ries
9/22/2022
processo to analyze crack length automatically'''

import image_analyzer
import pixel as p
import cornerFinder as cf
import data_organizer as dat
import os
import pandas as pd

def findCrack(clumpList, upperCorner, lowerCorner, leftnum, rightnum, diff, ratio, dark, width):
    '''returns the cracktip as a clump object'''
    crack = p.Pixel(800,800,800,800,0)
    biggestX = 0
    if upperCorner == lowerCorner: #checks if corners were found otherwise return an empty pixel to prevent program crashing
        print("no corners so crack was placed in upper left corner")
        return crack
    
    for row in clumpList:
        for clump in row:
            if clump.isInBetween(upperCorner, lowerCorner, width/2): #check if the clump meets crack tip criteria
                if clump.compareDark(clumpList, leftnum, rightnum, diff, dark) and clump.compareRed(clumpList,leftnum,rightnum,ratio) and clump.getX() > biggestX:
                    biggestX = clump.getX()
                    crack = clump
    return crack
            


'''now define lumped methods based on the type of background'''
def carbonSample(cornerFinder, clumps, leftnum, rightnum, diff, ratio, dark, aditBright, extraneb, darkException, width):
    '''returns the upper and lower corner and cracktip as clump objects'''
    corners = cornerFinder.determineCorner(cornerFinder.findCornerRed(clumps, aditBright, ratio, extraneb, darkException))
    crack_object = findCrack(clumps, corners[0], corners[1], leftnum, rightnum, diff, ratio, dark, width)

    #determine coordinates of locations
    upCorner = (corners[0].getX(), corners[0].getY())
    lowCorner = (corners[1].getX(), corners[1].getY())
    crack = (crack_object.getX(), crack_object.getY())

    if corners[0] == corners[1] or corners[0] == crack_object: #assign an arbitrary location to manually place the squares for post analysis
        upCorner, lowCorner, crack = (400, 400), (400, 1200), (800, 800)
    return [upCorner, lowCorner, crack] #return (x,y) coordinates for each pixel object




'''finally here is the main method with its parameters'''
def mainMethod(image_folder_name, test_image_folder_name, excel_name, nebnum = 33, ydis = 450, xdis = 450, cornerDark=90, cornerBright=150, 
darkness=100, leftn = 39, rightn = 39, redRatio = 1.5, diffStrength = 30, adBright = 5, extraneb = 5, darkException = 10, mark = False):
    
    current_directory = os.getcwd() #find directory
    image_folder = current_directory + '/' + image_folder_name
    excel = current_directory + '/' + excel_name
    test_image_folder = current_directory + '/' + test_image_folder_name

    data_organizer = dat.Data_organizer() #instantiate data organizer and image analyzer
    imager = image_analyzer.Image_analyzer(test_image_folder)
    a = 0 #for indexing images

    for images in os.listdir(image_folder):
        if (images.endswith(".bmp") and "test_image" not in images): #check if the image ends with bpm
            a += 1
            print("Starting image " + str(a))

            img_path_in = image_folder + '/' + images #find the image file

            #clump pixels and create rows
            pixelGrid = imager.makePixelGrid(img_path_in)
            clumps = imager.clump(pixelGrid, 4)
            cornerFinder = cf.CornerFinder(imager.width, imager.height, cornerDark, cornerBright, nebnum, ydis, xdis)

            #now work on finding points in image
            pointList = carbonSample(cornerFinder,clumps,leftn,rightn,diffStrength,redRatio,darkness*0.9,adBright, extraneb, darkException, imager.width)
            #pointList = [upperCorner, lowerCorner, crack]
            

            crack_coords, upCorner_coords, lowCorner_coords = pointList[2], pointList[0], pointList[1]

            
            #now print out data for user to see
            cracktip = "(" + str(crack_coords[0]) + "," + str(crack_coords[1]) + ")"
            print(cracktip + " is the (X,Y) coordinate for cracktip of image: " + images)
            
            markedList = [upCorner_coords,lowCorner_coords, crack_coords]
            
            if mark:#mark the image for checking where reference points were found (saved in folder called "Test_images")
                imager.markGrid(pixelGrid, markedList, 25, image_ind = a)
                        
            data_organizer.update_data(images, crack_coords, upCorner_coords, lowCorner_coords) #update data to excel

    #add all data to the excel after all images analyzed
    data = pd.DataFrame(data_organizer.getData_table())
    data.to_excel (excel, sheet_name = "Sheet1", index = False, header = True)






#main code
if __name__ == "__main__":
    #for using the main method: 
    current_file_path = os.path.abspath(__file__)
    current_directory = os.path.dirname(current_file_path)
    os.chdir(current_directory) #move to new directory regardless of location

    '''image related characteristics: '''
    #type the name of the folders and excel file here
    image_folder = "Images_in" # -folder_in: is the name of the folder the images are in
    test_image_folder = "Test_images" # -test_folder: is where the test images are saved to when drawn
    excel = "Crack propogation.xlsx" # -Excel: is the excel file name + location that the data will be written to
    mark = True # -mark determines whether the points are redrawn for visual reference or not, True means yes. (this increases run time alot)


    '''Corner related characteristics: '''
    nebnum = 33 # -nebnum: is the number of neighborhing clumps being checked in every direction for finding corners (we want between 23 and 35)

    # -ydis: is the pixel distance corners can deviate from the average y value of the cornerCandidates, same for xdis but with x value
    ydis = 500
    xdis = 500
    # -cornerDark and cornerBright: are the color values we define for dark pixels and bright pixels
    cornerDark = 90
    cornerBright = 150  

    # -adbright: if the amount brighter we want the parts above upper and below lower corner to be (to be added to cornerBright value)
    adBright = 5
    extraneb = 5 # -extraneb: is the amount of extra neighbors being checked in the upper and lower diagonal directions for finding corner


    '''Cracktip related characteristics: '''
    darkness = 100 # -darkness: is the pixel value that the neighborhing clumps to the left of the cracktip need to be

    # -leftn and rightn: are the number of neighbors to the left and right being checked and averaged to find the cracktip (higher # means method will check farther to left and right)
    leftn = 45
    rightn = 45
    redRatio = 1.4 # -redRatio: is the ratio of redness on the left side of cracktip to right side (pick ratio depending on how red background is)
    diffStrength = 28 # -diffstrength: is a scaled value for the difference between darkness of left and right neighbors (leftn and rightn) of cracktip (we want between 20 and 60)    
    darkException = 5 # -darkException is the amount brighter the standard for dark can be for the the lower and upper left diagonal neighbors for determining corners


    '''This is the actual method being called to run the whole program'''
    mainMethod(image_folder, test_image_folder, excel, nebnum, ydis, xdis, cornerDark, cornerBright,
            darkness, leftn, rightn, redRatio, diffStrength, adBright, extraneb, darkException, mark)