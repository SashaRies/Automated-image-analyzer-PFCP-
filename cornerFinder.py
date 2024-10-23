'''
Sasha Ries
9/22/2022
processo to analyze crack length automatically'''

import pixel as p

# constants that can be changed anytime
Folder_dir = "C:/Users/sries/onedrive/documents/programming/instron_automation"

class CornerFinder():
    def __init__(self, width=4632, height=3488, dark=80, bright=140, neighborDistance=28, Ydisplacement=450, Xdisplacement=450):
        self.width = width
        self.height = height
        self.dark = dark
        self.bright = bright
        self.neighborDistance = neighborDistance
        self.Ydisplacement = Ydisplacement
        self.Xdisplacement = Xdisplacement



    def findCornerRed(self,clumps, aditBright, redRatio, extraneb, darkException):
        '''checks clumps for the initial top left corner to use as a reference point'''
        i = 0
        cornerList = [[],[]]
        brightRated = self.bright * self.neighborDistance
        darkRated = self.dark * self.neighborDistance
        
        for row in clumps:
            #I roganized my if statements to reduce runtime and only check neighborhing clumps if previous tests have been passed
            j = 0
            for clump in row:
                if (j-self.neighborDistance) >= 0 and (j+self.neighborDistance) <= len(row) and (i-self.neighborDistance) >= 0 and (i+self.neighborDistance) <= len(clumps):
                    color = 0
                    '''top section is for both corners'''
                    for z in range(self.neighborDistance): #check the 30 left clumps
                        color += clumps[i][j-z-1].getColor()
                    if color <= darkRated: #check if average of 30 left clumps is very dark
                        color = 0
                        for z in range(self.neighborDistance): #check the 30 right clumps
                            color += clumps[i][j+z+1].getColor()
                        if color >= brightRated: #check if average of 30 right clumps is very bright
                            for a in range(2):
                                color = 0
                                '''this section splits up top and bottom corner'''
                                for z in range(self.neighborDistance): #check the top 30 clumps
                                    color += clumps[i-z-1][j].getColor()
                                if (color >= brightRated + aditBright*self.neighborDistance and a == 0) or (color <= darkRated and a == 1):
                                    #check if average of 30 top clumps is very bright or very dark
                                    color = 0
                                    for z in range(self.neighborDistance):#check the 30 bottom clumps
                                        color += clumps[i+z+1][j].getColor()
                                    if (color <= darkRated and a == 0) or (color >= brightRated + aditBright*self.neighborDistance and a == 1):
                                        #check if average of 30 bottom clumps is very dark or very bright
                                        colorLeft = 0
                                        redLeft = 0
                                        colorRight = 0
                                        redRight = 0
                                        if a == 0:
                                            for z in range(self.neighborDistance + extraneb):#finally check the 30 topleft clumps (diagonally)
                                                colorLeft += clumps[i-z-1][j-z-1].getColor()
                                                redLeft += clumps[i-z-1][j-z-1].getRed()
                                                colorRight += clumps[i-z-1][j+z+1].getColor()
                                                redRight += clumps[i-z-1][j+z+1].getRed()
                                        else:
                                            for z in range(self.neighborDistance + extraneb):#finally check the 30 bottomleft clumps (diagonally)
                                                colorLeft += clumps[i+z+1][j-z-1].getColor()
                                                redLeft += clumps[i+z+1][j-z-1].getRed()
                                                colorRight += clumps[i+z+1][j+z+1].getColor()
                                                redRight += clumps[i+z+1][j+z+1].getRed()
                                        if (redLeft/colorLeft)/(redRight/colorRight) >= redRatio*0.8 and colorLeft/(self.neighborDistance + extraneb) <= self.dark + darkException: 
                                            #check if average of 30 somethingleft clumps is very dark
                                            cornerList[a].append(clump)
                j += 1
            i += 1
        #check if corners were found
        if len(cornerList[0]) < 1 and len(cornerList[1]) < 1:
            print("not enough corners were found in FindCornerRed")
        return cornerList

    def determineCorner(self,cornerList):
        #print("number of corner candidates: " + str(len(cornerList[0])))
        '''based on specific parameters this will determine which of the corner candidates will become the corner reference point'''
        newList = [p.Pixel(400,400,400,400,0), p.Pixel(400,400,400,400,0)]
        i = 0
        for orientation in cornerList:
            if len(orientation) < 1: #make sure to return a value even if no corners were provided
                return newList
            averageX = 0
            averageY = 0
            i += 1
            for cornerCandidate in orientation: #find average x and y coordinate values to weed out pixels that deviate too much
                averageX += cornerCandidate.getX()
                averageY += cornerCandidate.getY()
            averageX /= len(orientation)
            averageY /= len(orientation)

            if i == 1:
                Y = 0 #start with a small number y to gaurantee one is bigger
                for cornerCandidate in orientation:
                    if abs(cornerCandidate.getY() - averageY) < self.Ydisplacement and cornerCandidate.getY() > Y:
                        if abs(cornerCandidate.getX() - averageX) < self.Xdisplacement:
                            Y = cornerCandidate.getY()
                            newList[0] = cornerCandidate
            else:
                Y = self.height #start with a big number y to gaurantee one is smaller
                for cornerCandidate in orientation:
                    if abs(cornerCandidate.getY() - averageY) < self.Ydisplacement and cornerCandidate.getY() < Y:
                        if abs(cornerCandidate.getX() - averageX) < self.Xdisplacement:
                            Y = cornerCandidate.getY()
                            newList[1] = cornerCandidate
        print("topleft corner X,Y: " + str(newList[0].getX()) + ", " + str(newList[0].getY()))
        print("bottomleft corner X,Y: " + str(newList[1].getX()) + ", " + str(newList[1].getY()))
        return newList
    




    #code that i didnt want to delete but could be useful in the future

    '''def findCorners_differential(self, pixelGrid, dRed, dColor):
    #A corner is a clump where (d/dx)(Red) is either around 0 or a little bigger than 0
    #A corner is a clump where (d/dx)(Color) is much bigger than 0
    #If its an upp corner than the above applies with d/dx and -d/dy
    #If its a lower corner than the above applies with d/dx and d/dy
    upperCornerList, lowerCornerList = [], []
    for row in pixelGrid:
        for pixel in row:
            #set up if statements for lower corner since (d/dx)(Red) and (d/dy)(Red) is inbetween 0 and dRed
            if pixel.getDiff_red()[0] < dRed and pixel.getDiff_red()[1] < dRed and pixel.getDiff_red()[0] > 0 and pixel.getDiff_red()[1] > 0:
                if pixel.getDiff_color()[0] > dColor and pixel.getDiff_color()[1] > dColor:
                    lowerCornerList.append(pixel)
            #set up if statements for upper corner since (d/dx)(Red) is inbetween 0 and dRed and (d/dy)(Red) is inbetween -dRed and 0
            elif pixel.getDiff_red()[0] < dRed and pixel.getDiff_red()[1] > -1*dRed and pixel.getDiff_red()[0] > 0 and pixel.getDiff_red()[1] < 0:
                if pixel.getDiff_color()[0] > dColor and pixel.getDiff_color()[1] < -1*dColor:
                    upperCornerList.append(pixel)
    if len(upperCornerList) > 0 and len(lowerCornerList) > 0:
        return (upperCornerList, lowerCornerList)
    else: 
        return self.findCorners_differential(pixelGrid, dRed*1.1, dColor*0.9)
    
    def find_corners_new(self, edgeList, pixelGrid, redRatio):
        cornerList = [[],[]]
        brightRated = self.bright * self.neighborDistance
        darkRated = self.dark * self.neighborDistance
        for edge in edgeList:
            i = edge[1]
            j = edge[0]
            if i < len(pixelGrid) - self.neighborDistance and i > self.neighborDistance and j < len(pixelGrid[0]) - self.neighborDistance and j > self.neighborDistance:
                    color = 0
                    #top section is for both corners
                    for z in range(self.neighborDistance): #check the 30 left clumps
                        color += pixelGrid[i][j-z-1].getColor()
                    if color <= darkRated: #check if average of 30 left clumps is very dark
                        color = 0
                        for z in range(self.neighborDistance): #check the 30 right clumps
                            color += pixelGrid[i][j+z+1].getColor()
                        if color >= brightRated: #check if average of 30 right clumps is very bright
                            for a in range(2):
                                color = 0
                                #this section splits up top and bottom corner
                                for z in range(self.neighborDistance): #check the top 30 clumps
                                    color += pixelGrid[i-z-1][j].getColor()
                                if (color >= brightRated and a == 0) or (color <= darkRated and a == 1):
                                    #check if average of 30 top clumps is very bright or very dark
                                    color = 0
                                    for z in range(self.neighborDistance):#check the 30 bottom clumps
                                        color += pixelGrid[i+z+1][j].getColor()
                                    if (color <= darkRated and a == 0) or (color >= brightRated and a == 1):
                                        #check if average of 30 bottom clumps is very dark or very bright
                                        colorLeft = 0
                                        redLeft = 0
                                        colorRight = 0
                                        redRight = 0
                                        if a == 0:
                                            for z in range(self.neighborDistance):#finally check the 30 topleft clumps (diagonally)
                                                colorLeft += pixelGrid[i-z-1][j-z-1].getColor()
                                                redLeft += pixelGrid[i-z-1][j-z-1].getRed()
                                                colorRight += pixelGrid[i-z-1][j+z+1].getColor()
                                                redRight += pixelGrid[i-z-1][j+z+1].getRed()
                                        else:
                                            for z in range(self.neighborDistance):#finally check the 30 bottomleft clumps (diagonally)
                                                colorLeft += pixelGrid[i+z+1][j-z-1].getColor()
                                                redLeft += pixelGrid[i+z+1][j-z-1].getRed()
                                                colorRight += pixelGrid[i+z+1][j+z+1].getColor()
                                                redRight += pixelGrid[i+z+1][j+z+1].getRed()
                                        if (redLeft/colorLeft)/(redRight/colorRight) >= redRatio*0.8 and colorLeft/(self.neighborDistance) <= self.dark: 
                                            #check if average of 30 somethingleft clumps is very dark
                                            cornerList[a].append(pixelGrid[i][j])
        #check if corners were found
        if len(cornerList[0]) > 0 and len(cornerList[1]) > 0:
            return cornerList
        else: print("not enough corners were found in Find_corners_new")
        return cornerList
    


    def findCorners_differential(self, pixelGrid, bright, red, dark, dRed, dColor, iterLength = 20):
        #change this to make it find dx and dy over two clumps instead of one
        upperCornerList, lowerCornerList = [], []
        brightRated = bright*iterLength
        darkRated = dark*iterLength
        redRated = red*iterLength
        iterDiff = int(iterLength/2 - 1)
        diffRedRated = dRed*iterDiff*2
        diffColorRated = dColor*iterDiff*2

        for i in range(iterLength, len(pixelGrid)-iterLength):
            for j in range(iterLength, len(pixelGrid[0])-iterLength):
                corner_identity = 0
                leftRed = sum([pixelGrid[i][j-x].getRed() for x in range(iterLength)])
                leftColor = sum([pixelGrid[i][j-x].getColor() for x in range(iterLength)])
                rightColor = sum([pixelGrid[i][j+x].getColor() for x in range(iterLength)])
                
                if leftColor > darkRated or leftRed < redRated or rightColor < brightRated: #check if average of 30 left clumps is very dark and red
                    continue
                    
                upRed = sum([pixelGrid[i-x][j].getRed() for x in range(iterLength)])
                upColor = sum([pixelGrid[i-x][j].getColor() for x in range(iterLength)])
                downRed = sum([pixelGrid[i+x][j].getRed() for x in range(iterLength)])
                downColor = sum([pixelGrid[i+x][j].getColor() for x in range(iterLength)])

                if upColor <= darkRated and upRed >= redRated: #check if average of 30 upper clumps is very dark and red
                    #search for bottom corner
                    diff_red_horizontal = sum([pixelGrid[i][j+x-iterDiff].getDiff_red()[0] for x in range(iterDiff*2)])
                    diff_color_horizontal = sum([pixelGrid[i][j+x-iterDiff].getDiff_red()[0] for x in range(iterDiff*2)])
                
                elif downColor <= darkRated and downRed >= redRated:
                    #search for upper corner
                    diff_red_horizontal = sum([pixelGrid[i][j+x-iterDiff].getDiff_red()[0] for x in range(iterDiff*2)])
                    diff_color_horizontal = sum([pixelGrid[i][j+x-iterDiff].getDiff_red()[0] for x in range(iterDiff*2)])
                
                else: continue

                if diff_red_horizontal < diffRedRated and diff_red_horizontal > 0 and diff_color_horizontal > diffColorRated:
                    diff_red_vertical = sum([pixelGrid[i+x-iterDiff][j].getDiff_red()[1] for x in range(iterDiff*2)])
                    diff_color_vertical = sum([pixelGrid[i+x-iterDiff][j].getDiff_color()[1] for x in range(iterDiff*2)])
                    
                    if diff_red_vertical < diffRedRated and diff_red_vertical > 0 and diff_color_vertical > diffColorRated:
                        lowerCornerList.append(pixelGrid[i][j])
                    elif diff_red_vertical > -1*diffRedRated and diff_red_vertical < 0 and diff_color_vertical < -1*diffColorRated:
                        upperCornerList.append(pixelGrid[i][j])

        return (upperCornerList,lowerCornerList)



    def findCornerBlue(self, edgeList, aditBright):
        #checks clumps for the initial top left corner to use as a reference point
        cornerList = [[],[]]
        for edge in edgeList:
            #I reorganized my if statements to reduce runtime and only check neighborhing clumps if previous tests have been passed
            if (edge.getX() - self.neighborDistance) > 0 and (edge.getX() + self.neighborDistance) < self.width and (edge.getY() - 
            self.neighborDistance) > 0 and (edge.getY() + self.neighborDistance) < self.height:
                color = 0
                #top section is for both corners
                for z in range(self.neighborDistance): #check the 30 left clumps
                    color += edgeList[edge.getRow()][edge.getCol() - z - 1].getColor()
                if color/self.neighborDistance <= self.dark: #check if average of 30 left clumps is very dark
                    color = 0
                    for z in range(self.neighborDistance): #check the 30 right clumps
                        color += edgeList[edge.getRow()][edge.getCol() + z + 1].getColor()
                    if color/self.neighborDistance >= self.bright: #check if average of 30 right clumps is very bright
                        for a in range(2):
                            color = 0
                            #this section splits up top and bottom corner
                            for z in range(self.neighborDistance + 8): #check the top 30 clumps
                                color += edgeList[edge.getRow() - z - 1][edge.getCol()].getColor()
                            if (color/(self.neighborDistance+8) >= self.bright + aditBright and a == 0) or (color/(self.neighborDistance+8) <= self.dark-10 and a == 1):
                                #check if average of 30 top clumps is very bright or very dark
                                color = 0
                                for z in range(self.neighborDistance + 8):#check the 30 bottom clumps
                                    color += edgeList[edge.getRow() + z + 1][edge.getCol()].getColor()
                                if (color/(self.neighborDistance+8) <= self.dark-10 and a == 0) or (color/(self.neighborDistance+8) >= self.bright + aditBright and a == 1):
                                    #check if average of 30 bottom clumps is very dark or very bright
                                    color = 0
                                    if a == 0:
                                        for z in range(self.neighborDistance+5):#finally check the 30 topleft clumps (diagonally)
                                            color += edgeList[edge.getRow() - int(z/2) - 1][edge.getCol() - z - 1].getColor()
                                    else:
                                        for z in range(self.neighborDistance+5):#finally check the 30 bottomleft clumps (diagonally)
                                            color += edgeList[edge.getRow() + int(z/2) + 1][edge.getCol() - z - 1].getColor()
                                    if color/(self.neighborDistance+5) <= self.dark: #check if average of 30 somethingleft clumps is very dark
                                        cornerList[a].append(edge)
        #check if corners were found
        if len(cornerList[0]) > 1 and len(cornerList[1]) > 1:
            return cornerList
        else: print("not enough corners were found in FindCornerBlue")
        return cornerList


    def findCornerDark(self,clumps, aditBright, extraneb, darkException):
        i = 0
        cornerList = [[],[]]
        for row in clumps:
            #I roganized my if statements to reduce runtime and only check neighborhing clumps if previous tests have been passed
            j = 0
            for clump in row:
                if (j-self.neighborDistance) >= 0 and (j+self.neighborDistance) <= len(row) and (i-self.neighborDistance) >= 0 and (i+self.neighborDistance) <= len(clumps):
                    color = 0
                    #top section is for both corners
                    for z in range(self.neighborDistance): #check the 30 left clumps
                        color += clumps[i][j-z-1].getColor()
                    if color/self.neighborDistance <= self.dark: #check if average of 30 left clumps is very dark
                        color = 0
                        for z in range(self.neighborDistance): #check the 30 right clumps
                            color += clumps[i][j+z+1].getColor()
                        if color/self.neighborDistance >= self.bright: #check if average of 30 right clumps is very bright
                            for a in range(2):
                                color = 0
                                #this section splits up top and bottom corner
                                for z in range(self.neighborDistance): #check the top 30 clumps
                                    color += clumps[i-z-1][j].getColor()
                                if (color/self.neighborDistance >= self.bright + aditBright and a == 0) or (color/self.neighborDistance <= self.dark and a == 1):
                                    #check if average of 30 top clumps is very bright or very dark
                                    color = 0
                                    for z in range(self.neighborDistance):#check the 30 bottom clumps
                                        color += clumps[i+z+1][j].getColor()
                                    if (color/self.neighborDistance <= self.dark and a == 0) or (color/self.neighborDistance >= self.bright + aditBright and a == 1):
                                        #check if average of 30 bottom clumps is very dark or very bright
                                        color = 0
                                        if a == 0:
                                            for z in range(self.neighborDistance + extraneb):#finally check the 30 topleft clumps (diagonally)
                                                color += clumps[i-z-1][j-z-1].getColor()
                                        else:
                                            for z in range(self.neighborDistance + extraneb):#finally check the 30 bottomleft clumps (diagonally)
                                                color += clumps[i+z+1][j-z-1].getColor()
                                        if color/(self.neighborDistance + extraneb) <= self.dark + darkException: #check if average of 30 somethingleft clumps is very dark
                                            cornerList[a].append(clump)
                j += 1
            i += 1
        #check if corners were found
        if len(cornerList[0]) > 1 and len(cornerList[1]) > 1:
            return cornerList
        else: print("not enough corners were found in FindCornerDark")
        return cornerList'''

