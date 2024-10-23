'''Sasha Ries
   Class for Pixel objects'''

folder_dir = "C:/Users/sries/onedrive/documents/programming/instron_automation"

class Pixel:
    '''This class gives all the attributes associated with a pixel but in a convenient to access form'''
    def __init__(self, row, col, x, y, color, redVal = 0, greenVal = 0, blueVal = 0, dxColor = 0, dyColor = 0, dxRed = 0, dyRed = 0, dxGreen = 0, dyGreen = 0, dxBlue = 0, dyBlue = 0):
        self.x = x
        self.y = y
        self.row = row
        self.col = col
        self.color = color
        self.red = redVal
        self.blue = blueVal
        self.green = greenVal
        self.dxColor = dxColor
        self.dyColor = dyColor
        self.dxRed = dxRed
        self.dyRed = dyRed
        self.dxGreen = dxGreen
        self.dyGreen = dyGreen
        self.dxBlue = dxBlue
        self.dyBlue = dyBlue

    def getX(self):
        return self.x
    
    def getY(self):
        return self.y
    
    def getRow(self):
        return self.row
    
    def getCol(self):
        return self.col
    
    def getColor(self):
        return self.color

    def getRed(self):
        return self.red

    def getBlue(self):
        return self.blue
    
    def getGreen(self):
        return self.green

    def getDiff_color(self):
        return self.dxColor, self.dyColor
    
    def getDiff_red(self):
        return self.dxRed, self.dyRed

    def getDiff_green(self):
        return self.dxGreen, self.dyGreen

    def getDiff_blue(self):
        return self.dxBlue, self.dyBlue
    
    def __eq__(self, other):
        '''check if there are two identical pixels'''
        if isinstance(other, Pixel):
            return self.x == other.x and self.y == other.y
        return False
    

    def isInBetween(self, upperCorner, lowerCorner, centerX):
        '''check if self is within the provided coordinates'''
        if self.y > upperCorner.getY() and self.y < lowerCorner.getY() and abs(self.x - centerX) < 600:
            return True
        return False

    def compareRed(self,clumpList, leftnum, rightnum, ratio):
        '''compares the ratio of average (redness/overall color) of the left (leftnum) pixels to the average (redness/overall color) of the right (rightnum) pixels'''
        totalRedLeft = 0
        totalRedRight = 0
        totalRight = 0
        totalLeft = 0
        for i in range(leftnum):
            totalRedLeft += clumpList[self.row][self.col-i].getRed()
            totalLeft += clumpList[self.row][self.col-i].getColor()
        for j in range(rightnum):
            totalRight += clumpList[self.row][self.col+j].getColor()
            totalRedRight += clumpList[self.row][self.col+j].getRed()
        if (totalRedLeft/(totalLeft)) / (totalRedRight/(totalRight)) >= ratio: #returns true if the ratio is high enough
            return True
        return False

    def compareDark(self, clumpList, leftnum, rightnum, diff, dark):
        '''compares the difference between average darkness of the left (leftnum) pixels to the right (rightnum) pixels'''
        totalRight = 0
        totalLeft = 0
        for z in range(leftnum):
            totalLeft += clumpList[self.row][self.col-z].getColor()
        for x in range(rightnum):
            totalRight += clumpList[self.row][self.col+x].getColor()
        
        #now determine comparisons
        if totalRight/rightnum - totalLeft/leftnum > diff and totalLeft/leftnum <= dark: 
            #returns true if difference is big enough and average of (leftnum) pixels is dark enough
            return True
        return False



    def checkColor(self, colorIntensity, whiteIntensity, colorChoice):
        '''checks if self reaches a certain color criteria while being under a total brightness criteria'''
        if colorChoice == "red":
            rgb = self.red
        elif colorChoice == "blue":
            rgb = self.blue
        else:
            rgb = self.green
        
        if rgb > colorIntensity and self.color < whiteIntensity:
            return True
        return False
    
    def setX(self, newX):
        self.x = newX
    
    def setY(self, newY):
        self.y = newY
    
    def setRow(self, newRow):
        self.row = newRow

    def setCol(self, newCol):
        self.col = newCol
    
    def setRed(self, newRed):
        self.red = newRed 

    def setGreen(self, newGreen):
        self.green = newGreen 

    def setBlue(self, newBlue):
        self.blue = newBlue 

    def setDiff_red(self, newDxRed, newDyRed):
        self.dxRed = newDxRed
        self.dyRed = newDyRed
    
    def setDiff_green(self, newDxGreen, newDyGreen):
        self.dxRed = newDxGreen
        self.dyRed = newDyGreen

    def setDiff_blue(self, newDxBlue, newDyBlue):
        self.dxRed = newDxBlue
        self.dyRed = newDyBlue
    
    def setDiff_color(self, newDxColor, newDyColor):
        self.dxColor = newDxColor
        self.dyColor = newDyColor