'''Sasha Ries
   4/11/23
   File for user to interact with marked images post automated analysis and move red squares which would in live time update the X-pixel distance in the excel file'''

import cv2
import tkinter as tk
import os
import data_organizer as do
import pandas as pd
import openpyxl


# global variables
x_scale, y_scale = 1, 1
click = False
clickUp = False
clickDown = False
clickCrack = False
run = True
square_pos = None
button_xRange, button_yRange = (0,0), (0,0)
upCorner, lowCorner, crack = (0,0), (0,0), (0,0)
update = False



def mouse_event(event, x, y, flags, param):
    '''whenver the mouse is clicked or moved it will call this method and update global variables accordingly'''
    global clickUp, clickDown, clickCrack, square_pos, update

    if event == cv2.EVENT_LBUTTONDOWN: #button down means the mouse has been clicked
        #check coordinates of click
        if x >= upCorner[0] and x <= upCorner[0]+8*x_scale and y >= upCorner[1] and y <= upCorner[1]+6*y_scale: #upcorner click
            if not clickUp:
                clickUp = True
            else: 
                clickUp = False
        elif x >= lowCorner[0] and x <= lowCorner[0]+8*x_scale and y >= lowCorner[1] and y <= lowCorner[1]+6*y_scale: #lowcorner clicked
            if not clickDown:
                clickDown = True
            else: 
                clickDown = False
        elif x >= crack[0] and x <= crack[0]+8*x_scale and y >= crack[1] and y <= crack[1]+6*y_scale: #crack cliked
            if not clickCrack:
                clickCrack = True
            else: 
                clickCrack = False
        elif x >= button_xRange[0] and x<= button_xRange[1] and y >= button_yRange[0] and y <= button_yRange[1]: #update button clicked
            update = True

        square_pos = (x, y)

    elif event == cv2.EVENT_MOUSEMOVE:
        square_pos = (x, y)




def interact(img):
    '''loop through and display markers in assigned location
    when one is clicked on have it follow the mouse untill user clicks again, then it is placed there'''
    global click, upCorner, lowCorner, crack, update, run
    
    img_copy = img.copy()

    while True: #iterate and continuously redraw the markers, while updating their coordinates
        img = img_copy.copy()


        xOffset = int(8*x_scale)
        yOfsset = int(6*y_scale)

        if clickUp: #upper corner clicked
            upCorner = (int(square_pos[0]),int(square_pos[1]))
        
        elif clickDown: #lower corner clicked
            lowCorner = (int(square_pos[0]),int(square_pos[1]))

        elif clickCrack: #crack tip clicked
            crack = (int(square_pos[0]),int(square_pos[1]))

        
        cv2.rectangle(img, upCorner, (upCorner[0]+xOffset, upCorner[1]+yOfsset), (0,255,0), -1)#upper corner marker
        cv2.rectangle(img, lowCorner, (lowCorner[0]+xOffset, lowCorner[1]+yOfsset), (0,255,255), -1)#lower corner marker
        cv2.rectangle(img, crack, (crack[0]+xOffset, crack[1]+yOfsset), (0,0,255), -1)#crack tip marker

        cv2.imshow("image_checker", img)

        #32 corresponds to the space bar being pressed
        if cv2.waitKey(1) & 0xFF == 32 or update: #will go to next image and update data either if space is pressed of the update button is clicked
            update = False 

            #rescale the values
            upCorner = (int(upCorner[0]*x_scale), int(upCorner[1]*y_scale))
            lowCorner = (int(lowCorner[0]*x_scale), int(lowCorner[1]*y_scale))
            crack = (int(crack[0]*x_scale), int(crack[1]*y_scale))
            return img
        elif cv2.waitKey(1) & 0xFF == 115: #the s key was pressed to close the program
            run = False
            print("program closed successfully")
            return None
            



def create_button(img, location, text, box_color, text_color, font_scale, font_thickness):
    '''draws the update button'''
    global button_xRange, button_yRange
    # Set font properties
    font = cv2.FONT_HERSHEY_SIMPLEX

    # Get text size and position it in the center of the image
    text_size, _ = cv2.getTextSize(text, font, font_scale, font_thickness)
    button_xRange = (location[0], location[0]+text_size[0])
    button_yRange = (location[1]-text_size[1]-5*font_scale, location[1]+text_size[1]-10*font_scale)

    # Draw the box
    cv2.rectangle(img, (location[0], location[1]-text_size[1]-5*font_scale), 
                (location[0]+text_size[0], location[1]+text_size[1]-10*font_scale), box_color, -1)

    # Draw the text
    cv2.putText(img, text, location, font, font_scale, text_color, font_thickness, cv2.LINE_AA)



def data_to_excel(data, excel, sheet_name):
    '''write data to a specified sheet in excel without changing the others'''
    workbook = openpyxl.load_workbook(excel)

    sheet = workbook[sheet_name] #Select the sheet you want to write to

    # Iterate through the rows and columns of the DataFrame and write each cell value to the corresponding cell in the Excel sheet
    for row in range(1, len(data) + 1):
        for col in range(1, len(data.columns) + 1):
            cell = sheet.cell(row=row, column=col)
            cell.value = data.iloc[row - 1, col - 1]

    workbook.save(excel) #Save the changes to the workbook




def make_interface(image_folder_name, excel_name, test_image_folder_name):
    '''creates the user interface for image markers to be moved and data updated accordingly'''
    global upCorner, lowCorner, crack, x_scale, y_scale
    
    current_directory = os.getcwd() #find directory
    image_folder = current_directory + '/' + image_folder_name
    excel = current_directory + '/' + excel_name
    test_image_folder = current_directory + '/' + test_image_folder_name

    dat = do.Data_organizer()
    dat.read_data(excel) #read in data from excel file
    a = 0 #index for checked images

    cv2.namedWindow("image_checker")
    cv2.setMouseCallback("image_checker", mouse_event)

    for images in os.listdir(image_folder): #loop through all the images in the folder
        if (images.endswith(".bmp") and "test_image" not in images): #check if the image ends with bpm
            a += 1

            img_path_in = image_folder + '/' + images# find the image file
            img_path_out = test_image_folder + "/Checked_image" + str(a) + ".bmp"

            # create a dummy window to get screen size
            root = tk.Tk()
            width = root.winfo_screenwidth()
            height = root.winfo_screenheight()
            root.destroy()

            #let x-y coordinates be scaled back to the original image dimensions
            img = cv2.imread(img_path_in)
            orig_height, orig_width, channels = img.shape
            x_scale = orig_width/width
            y_scale = orig_height/height

            img = cv2.resize(img, (width, height)) #resize image

            button_x = int(500*x_scale)
            button_y = int(150*y_scale)
            create_button(img, (button_x, button_y),"Update", (180,100,50),(0,0,255), 2, 3)#create a button to click for updating data and going to next image

            upCorner, lowCorner, crack = dat.get_Data(images)#get data and place in squares

            #scale it down so it fits in the screen
            upCorner = (int(upCorner[0]/x_scale),int(upCorner[1]/y_scale))
            lowCorner = (int(lowCorner[0]/x_scale),int(lowCorner[1]/y_scale))
            crack = (int(crack[0]/x_scale),int(crack[1]/y_scale))

            img = interact(img)#this sets up the while loop for a user to drag and drop red squares

            if run == False: #check if s was pressed in which case the program is closed
                return

            #now save marked image and update points in excel sheet
            dat.update_data(images, crack, upCorner, lowCorner)
            cv2.imwrite(img_path_out, img) #save the updted image for reference

    #now update everything on sheet1 of the excel file without affecting sheet 2
    data = pd.DataFrame(dat.getData_table())
    data_to_excel(data, excel, "Sheet1")

    cv2.destroyAllWindows()#close the window





#main code
if __name__ == "__main__":
    # Get the directory of the current Python file
    current_file_path = os.path.abspath(__file__)
    current_directory = os.path.dirname(current_file_path)
    os.chdir(current_directory) #move to new directory regardless of location

    #type the name of the folders and excel file here
    image_folder = "Images_in"
    test_image_folder = "Test_images"
    excel = "Crack propogation.xlsx"
    make_interface(image_folder, excel, test_image_folder)
