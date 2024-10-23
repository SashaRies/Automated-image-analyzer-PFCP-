'''
Sasha Ries
9/22/2022
processo to organize crack length, cycle number, min and max load'''

import pandas as pd

class Data_organizer():
    def __init__(self):
        self.dataList = []
        self.d = {"name" : [], "load" : [], "cycle" : [], "x" : [], "y" : [], "corner" : [], "Corner up" : [], "Corner down" : []}
        
        self.data_dict = {"Image name" : [], "Total Cycles" : [], "Load min" : [], "LowCorner front X" : [], "LowCorner front Y" : [], "LowCorner back X" : [],
                       "LowCorner back Y" : [], "UpCorner front X" : [], "UpCorner front Y" : [], "UpCorner back X" : [], "UpCorner back Y" : [],
                        "Crack front X" : [], "Crack front Y" : [], "Crack back X" : [], "Crack back Y" : [], 
                        "Y dist front" : [], "Y dist back" : [], "X dist front" : [], "X dist back" : []}
        self.df = None
        

    def getData_table(self):
        return self.data_dict

    def update_data(self, name, location, upCorner, lowCorner):
        '''Adds or changes data based on the name of the image.'''
        split_name = name.rstrip(".bmp").split('_')
        load_val = float(split_name[2])

        # Check if the image already exists in the dictionary
        if name not in self.d["name"]:
            self.d["name"].append(name)
            self.d["load"].append(load_val)
            self.d["x"].append(location[0])
            self.d["y"].append(location[1])

            # Average corner coordinates
            corner = ((upCorner[0] + lowCorner[0])/2, (upCorner[1] + lowCorner[1])/2)
            self.d["corner"].append(corner)
            self.d["Corner up"].append(upCorner)
            self.d["Corner down"].append(lowCorner)

            add_cycle = int(split_name[5]) if len(split_name) > 5 and split_name[5] != "back" else 0
            self.d["cycle"].append(add_cycle)
            
        else:
            index = self.d["name"].index(name)  # Find index to update
            self.d["load"][index] = load_val
            self.d["x"][index] = location[0]
            self.d["y"][index] = location[1]

            # Average corner coordinates
            corner = ((upCorner[0] + lowCorner[0])/2, (upCorner[1] + lowCorner[1])/2)
            self.d["corner"][index] = corner
            self.d["Corner up"][index] = upCorner
            self.d["Corner down"][index] = lowCorner

            add_cycle = int(split_name[5]) if len(split_name) > 5 and split_name[5] != "back" else 0
            self.d["cycle"][index] = add_cycle

        # Update and organize data
        self.dataList = [
            (self.d["load"][i], self.d["cycle"][i], self.d["name"][i],
            self.d["x"][i], self.d["y"][i], self.d["corner"][i],
            self.d["Corner up"][i], self.d["Corner down"][i]) 
            for i in range(len(self.d["name"]))
        ]

        # Sort based on the first element in each tuple
        self.dataList.sort(key=lambda x: x[0])

        # Clear each array in data_dict
        for key in self.data_dict:
            self.data_dict[key].clear()

        # Calculate elapsed cycles for each image
        prevLoad, startCycle = 0, 0

        for touple in self.dataList:
            if touple[0] != prevLoad:
                startCycle += 10000
                prevLoad = touple[0]

            curCycle = touple[1] + startCycle

            # Add data for front and back values
            if touple[2].endswith("back.bmp"):
                self._update_back_distances(touple)
            else:
                self._update_front_distances(touple, curCycle)

    def _update_back_distances(self, touple):
        '''Update back distances in data_dict.'''
        self.data_dict["X dist back"].append(touple[3] - touple[5][0])
        self.data_dict["Y dist back"].append(touple[4] - touple[5][1])
        self.data_dict["Crack back X"].append(touple[3])
        self.data_dict["Crack back Y"].append(touple[4])
        self.data_dict["LowCorner back X"].append(touple[7][0])
        self.data_dict["LowCorner back Y"].append(touple[7][1])
        self.data_dict["UpCorner back X"].append(touple[6][0])
        self.data_dict["UpCorner back Y"].append(touple[6][1])

    def _update_front_distances(self, touple, curCycle):
        '''Update front distances in data_dict.'''
        self.data_dict["Image name"].append(touple[2])
        self.data_dict["Total Cycles"].append(curCycle)
        self.data_dict["Load min"].append(touple[0])
        self.data_dict["X dist front"].append(touple[3] - touple[5][0])
        self.data_dict["Y dist front"].append(touple[4] - touple[5][1])
        self.data_dict["Crack front X"].append(touple[3])
        self.data_dict["Crack front Y"].append(touple[4])
        self.data_dict["LowCorner front X"].append(touple[7][0])
        self.data_dict["LowCorner front Y"].append(touple[7][1])
        self.data_dict["UpCorner front X"].append(touple[6][0])
        self.data_dict["UpCorner front Y"].append(touple[6][1])



    def read_data(self, excel):
        df = pd.read_excel(excel, sheet_name = 'Sheet1')
        # create a dictionary where each key is a column header and the values are arrays of column values
        self.df = {column: df[column].tolist() for column in df.columns}
        return df

    def get_Data(self, name):
        upCorner_coords, lowCorner_coords, crack_coords = (400, 400), (400, 1200), (800, 800)
        
        if "Image name" in self.df and name.replace("_back", "") in self.df["Image name"]:
            if name.endswith("back.bmp"):
                index = self.df["Image name"].index(name.replace("_back", ""))

                upCorner_coords = (self.df["UpCorner back X"][index], self.df["UpCorner back Y"][index])
                lowCorner_coords = (self.df["LowCorner back X"][index], self.df["LowCorner back Y"][index])
                crack_coords = (self.df["Crack back X"][index], self.df["Crack back Y"][index])
            else:
                index = self.df["Image name"].index(name)

                upCorner_coords = (self.df["UpCorner front X"][index], self.df["UpCorner front Y"][index])
                lowCorner_coords = (self.df["LowCorner front X"][index], self.df["LowCorner front Y"][index])
                crack_coords = (self.df["Crack front X"][index], self.df["Crack front Y"][index])
        
        return upCorner_coords, lowCorner_coords, crack_coords


    def findIndex_ofColumn(self, array, column, value):
        for i in range(len(array)):
            if array[i][column] == value:
                return i
        print("couldnt find value in array")
        return False  # If the search value is not found in the array