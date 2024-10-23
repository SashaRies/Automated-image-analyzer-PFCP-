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



    def findCornerRed(self, clumps, aditBright, redRatio, extraneb, darkException):
        '''Checks clumps for the initial top left corner to use as a reference point.'''
        cornerList = [[], []]
        brightRated = self.bright * self.neighborDistance
        darkRated = self.dark * self.neighborDistance
        clump_rows = len(clumps)
        
        for i in range(clump_rows):
            row = clumps[i]
            row_length = len(row)
            
            for j in range(row_length):
                # Boundary checks
                if (j >= self.neighborDistance) and (j + self.neighborDistance < row_length) and (i >= self.neighborDistance) and (i + self.neighborDistance < clump_rows):
                    color_left = sum(clumps[i][j-z-1].getColor() for z in range(self.neighborDistance))
                    
                    if color_left <= darkRated:  # Check for dark left side
                        color_right = sum(clumps[i][j+z+1].getColor() for z in range(self.neighborDistance))
                        
                        if color_right >= brightRated:  # Check for bright right side
                            for a in range(2):  # Check top and bottom corners
                                color_top = sum(clumps[i-z-1][j].getColor() for z in range(self.neighborDistance))
                                condition_top = (color_top >= brightRated + aditBright * self.neighborDistance and a == 0) or \
                                                (color_top <= darkRated and a == 1)

                                if condition_top:
                                    color_bottom = sum(clumps[i+z+1][j].getColor() for z in range(self.neighborDistance))

                                    condition_bottom = (color_bottom <= darkRated and a == 0) or \
                                                    (color_bottom >= brightRated + aditBright * self.neighborDistance and a == 1)

                                    if condition_bottom:
                                        colorLeft, redLeft = 0, 0
                                        colorRight, redRight = 0, 0
                                        
                                        for z in range(self.neighborDistance + extraneb):
                                            if a == 0:  # Top-left
                                                colorLeft += clumps[i-z-1][j-z-1].getColor()
                                                redLeft += clumps[i-z-1][j-z-1].getRed()
                                                colorRight += clumps[i-z-1][j+z+1].getColor()
                                                redRight += clumps[i-z-1][j+z+1].getRed()
                                            else:  # Bottom-left
                                                colorLeft += clumps[i+z+1][j-z-1].getColor()
                                                redLeft += clumps[i+z+1][j-z-1].getRed()
                                                colorRight += clumps[i+z+1][j+z+1].getColor()
                                                redRight += clumps[i+z+1][j+z+1].getRed()
                                        
                                        # Final check for corner condition
                                        if (redLeft/colorLeft)/(redRight/colorRight) >= redRatio * 0.8 and colorLeft/(self.neighborDistance + extraneb) <= self.dark + darkException:
                                            cornerList[a].append(clumps[i][j])  # Add the clump found
        # Check if corners were found
        if len(cornerList[0]) < 1 and len(cornerList[1]) < 1:
            print("Not enough corners were found in FindCornerRed")
    
        return cornerList

    def determineCorner(self, cornerList):
        '''Determine which of the corner candidates will become the corner reference point based on specific parameters.'''
        newList = [p.Pixel(400, 400, 400, 400, 0), p.Pixel(400, 400, 400, 400, 0)]

        for i, orientation in enumerate(cornerList):
            if not orientation:  # Return default if empty orientation
                return newList

            # Calculate average coordinates
            avgX = sum(c.getX() for c in orientation) / len(orientation)
            avgY = sum(c.getY() for c in orientation) / len(orientation)

            if i == 0:
                # For the first orientation (top-left corner)
                candidates = [c for c in orientation if abs(c.getY() - avgY) < self.Ydisplacement and c.getX() >= avgX - self.Xdisplacement]
                if candidates:
                    newList[0] = max(candidates, key=lambda c: c.getY())
            else:
                # For the second orientation (bottom-left corner)
                candidates = [c for c in orientation if abs(c.getY() - avgY) < self.Ydisplacement and c.getX() >= avgX - self.Xdisplacement]
                if candidates:
                    newList[1] = min(candidates, key=lambda c: c.getY())

        print(f"Top-left corner X,Y: {newList[0].getX()}, {newList[0].getY()}")
        print(f"Bottom-left corner X,Y: {newList[1].getX()}, {newList[1].getY()}")
        return newList