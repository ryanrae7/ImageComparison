from PIL import Image, ImageChops, ImageTk, ImageEnhance, ImageFilter
import numpy as np
import tkinter as tk
from tkinter import filedialog
import decimal
import pandas as pd
import math
import os
import cv2
import pathlib
import matplotlib.pyplot as plt

#first create a dictionary table
zones = {
    'Time': [900, 1024, 0, 50], #input col1, col2, row1, row2
    'Version': [785, 900, 0, 50],
    'Language': [0, 200, 0, 50],
    'Entire Image': [0, 1024, 0, 768]
}



#function for calculating number of differences percentage wise in a given zone.
def extractROICalculations(image_1, image_2, zones):
    #ensure that the images are equal size, otherwise give the following message
    assert image_1.size == image_2.size, ("Images are not the same size.")

    data_array1 = np.asarray(image_1)
    data_array2 = np.asarray(image_2)

    #initialize dictionary to store values
    ROI_dic = {}

    #iterate through the zones and ensure that coordinates match
    for zone_name, zone_coords in zones.items():
        #initialize the zone for each item
        col1, col2, row1, row2 = zone_coords

        #crop the given area and find the difference
        roi_1 = data_array1[row1:row2, col1:col2]
        roi_2 = data_array2[row1:row2, col1:col2]
        
        #calculate the difference for each channel
        roi_difference = np.abs(roi_2 - roi_1)
        
        #sum the differences across all channels of RGB
        #allows for us to take on RGB values rather than use .convert('L') to bypass the steps that we want
        channel_difference_sum = np.sum(roi_difference, axis=-1)
        
        #calculate non-zero differences
        non_zero = np.count_nonzero(channel_difference_sum)

        #calculate the area of the zone and find the percentage
        area = (col2 - col1)*(row2 - row1)
        area_zone = (non_zero / area)*100

        #format the result
        formatted_area_zone = round(area_zone, 2)
        
        #input into the dictionary
        ROI_dic[zone_name] = formatted_area_zone

    return ROI_dic


        

#create output visual of the zone
def zoneVisual(image, zones):
    #color converter taking in image and assign color convertor code
    image_cv = cv2.cvtColor(np.array(image),cv2.COLOR_RGBA2RGB) #RGBA to RGB deleting alpha channels when drawing rectangles

    #iterate through all the zones listed above and get each item()
    for zone_index, zone in zones.items():
        col1, col2, row1, row2 = zone #taken from above
    
        #draw a rectangle with coordinates in the dictionary above with color RED
        image_cv = cv2.rectangle(image_cv, (col1, row1), (col2, row2), (255,0,0), lineType=1)

        #OPTIONAL put text next to rectangle
        image_cv = cv2.putText(image_cv, zone_index, (col1, row1-30), cv2.FONT_HERSHEY_SIMPLEX, fontScale=1,color=(255,255,255), thickness=1, lineType=cv2.LINE_AA)  

    return Image.fromarray(cv2.cvtColor(image_cv, cv2.COLOR_BGR2RGB))




#create function that takes a folder, passes all paths to a list (for one folder with images, can call this within getImagesFolderInFolder)
def getImagesFolder(folder_path):
    #initialize images array
    images = []

    #given a folder path loop through all the contents ending with .png/.PNG ... and append that path to the array
    for file_name in os.listdir(folder_path):

        if file_name.endswith(('.png', '.jpg', '.jpeg')):
            images.append(os.path.join(folder_path, file_name))
        
        #case for capital
        elif file_name.endswith(('.PNG', '.JPG', '.JPEG')):
            images.append(os.path.join(folder_path, file_name))

    #test if it does create array and return
    print (images)
    return images




#for the use case for when iterating through not only files but subdirectories
def getImagesFolderInFolder(directory):
    images = []
    namesFile = []
    #utilize walk from root to dir to files
    for root, dirs, files in os.walk(directory):

        #for each files that ends with .png .jpg and .jpeg, append to the initialized array above
        for file_name in files:
            if file_name.endswith(('.png', '.jpg', '.jpeg')):
                images.append(os.path.join(root, file_name))
                namesFile.append(file_name)
            elif file_name.endswith(('.PNG', '.JPG', '.JPEG')):
                images.append(os.path.join(root, file_name))
                namesFile.append(file_name)

    print(images)
    return images




def highlightDifference(image_1, image_2, opacity) -> Image:
    #format images to take in Alpha channel 
    image_1 = image_1.convert('RGBA')
    image_2 = image_2.convert('RGBA')

    #here, find the difference between the pixels and turn into array
    diff_temp = ImageChops.difference(image_1, image_2)
    diff_temp = np.array(diff_temp)

    #Ensure that the format is correct for the comparisons
    #self-note: [:, :, :3] where the first two : are x and y or width and height respectively and :3 is the RGB
        #where not equal to black for any axis=-1 (refers to the third dimension i.e. last dimension)
    mask = (diff_temp[:, :, :3] != [0, 0, 0]).any(axis=-1)

    #Turn those differences of mask into red with alpha = 255
    diff_temp[mask] = [255, 0, 0, 255]

    #Turn the numpy array back into an Image 
    diff_final = Image.fromarray(diff_temp, 'RGBA')

    #Adjust the opacity of image_2 takes in parameter 'Opacity'
    image_2.putalpha(int(opacity * 255))
    image_2 = ImageEnhance.Contrast(image_2).enhance(0.6)
    image_2 = ImageEnhance.Brightness(image_2).enhance(1.2)

    #Combine the images together at the end here utilizing image_2 (image compared against base)
    final = Image.alpha_composite(image_2, diff_final)

    return final
    


#save file method
def saveFile(image, base_name, counter):
    #with any keyword of user name e.g. rgae and the downloads file, make the path there
    path_file = os.path.join(os.getenv('USERPROFILE'), 'Downloads', 'Picture Difference')

    #If the file is not in that path, create new directory
    if not os.path.isdir(path_file):
        os.makedirs(path_file)

    #make file path name joining paramters and save it out
    file_path = os.path.join(path_file, f'{base_name}_{counter}.png')
    image.save(file_path)

    #return the file name
    return f'{base_name}_{counter}.png'


#possibly create a show image class to display the two initial pictures and the difference photo?
def main():
    #get images from folder
    images1 = getImagesFolderInFolder("C:/Users/rgae/Downloads/D58850_4.02.05 - Copy")
    images2 = getImagesFolderInFolder("C:/Users/rgae/Downloads/D58850_4.02.05")


    #initialize array to store percentages of difference
    #percentageArray = []

    #initialize list to store dictionary results for zone differences
    dictionaryZoneList = []

    #initialize filename
    fileName_1 = []
    fileName_2 = []

    #initialize name for the output of photo
    outputPhoto = []

    #loop the length of the smallest array (to ensure that the lists are comparable)
    for i in range(min(len(images1), len(images2))):
        # convert into RGBA for alpha
        img1 = Image.open(images1[i]).convert('RGBA')
        img2 = Image.open(images2[i]).convert('RGBA')

        #call displayPhotos function
        difference_test = highlightDifference(img1, img2, 1)

        #save the file in the downloads directory with changing names i + 1 and append the output image name to array
        saveFile(difference_test, 'difference_name', i + 1)
        outputPhoto.append(saveFile(difference_test, 'difference_name', i + 1))

        #calculate the difference in the zones and append new dictionary to the list
        difference_zone = extractROICalculations(img1, img2, zones)
        dictionaryZoneList.append(difference_zone)

        #Append the fileName into the two arrays listed above
        fileName_1.append(os.path.basename(images1[i]))
        fileName_2.append(os.path.basename(images2[i]))


    #Create the necessary DataFrame here
    df_zone = pd.DataFrame(dictionaryZoneList).astype(float)
    df_fileName_1 = pd.DataFrame(fileName_1, columns=['File_Name_1'])
    df_fileName_2 = pd.DataFrame(fileName_2, columns=['File_Name_2'])
    df_outputFile = pd.DataFrame(outputPhoto, columns=['Output File'])

    #create final dataFrame
    final_df = pd.concat([df_fileName_1, df_fileName_2, df_zone, df_outputFile], axis=1)

    final_df.index = final_df.index + 1 #set index + 1 to match the excel spreadsheet w/ headers
    final_df.to_excel('Zone.xlsx', header=True, index=True)

    #draw the new boxes
    example_image = Image.open(images1[0]).convert('RGB')
    #call the zone method
    visual_zone = zoneVisual(example_image, zones)
    visual_zone.save('example zone.png')

    print("Done Processing")


if __name__ == '__main__':
    main()
