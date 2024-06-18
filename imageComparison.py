from PIL import Image, ImageChops, ImageTk, ImageEnhance, ImageFilter
import numpy as np
import tkinter as tk
from tkinter import filedialog
import pandas as pd
import os
import cv2
from pathlib import Path
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
    



#method to calculate the difference between the first two photos
def calcDiffPhoto(image_1,image_2) -> float:
    #image to array using numpy
    differenceInPhoto = ImageChops.difference(image_1, image_2)
    diff_array = np.array(differenceInPhoto)

    #find non-zero indexes of the array
    non_zero = np.count_nonzero(diff_array)
    total_arrays = diff_array.size

    return (non_zero/total_arrays) * 100




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


#for the use case for when iterating through not only files but subdirectories
#def getImagesFolderInFolder(directory_1):
    #images_1 = []
    #directories = []
    #utilize walk from root to dir to files
    #for root_1, dirs_1, files_1 in os.walk(directory_1):
        #iterate through any folders
            #for dirs in dirs_1:
                #directories.append(dirs)
                #for file_name_1 in files_1:
                    #if file_name_1.lower().endswith(('.png', '.jpg', '.jpeg')):
                        #images_1.append(os.path.join(root_1, file_name_1))
        #for each files that ends with .png .jpg and .jpeg, append to the initialized array above

    #print(directories)
    #print(images_1)
    #return images_1

#simple iteration to get all images from a given directory
def getImages(directory):
    images = []
    #Utilize walk from root to dir to files
    for root, _, files in os.walk(directory):
        #For each file that ends with .png, .jpg, and .jpeg, append to the initialized array above
        for file_name in files:
            #consider for the upper case .png vs .PNG
            if file_name.lower().endswith(('.png', '.jpg', '.jpeg')):

                #append the values with its root i.e. whole path file to the list above and return
                images.append(os.path.join(root, file_name))
    return images


def getImagesFromFolders(directory_1, directory_2):
    #create lists to hold all images from both directories
    all_images_1 = getImages(directory_1)
    all_images_2 = getImages(directory_2)

    #Create dictionaries to hold images by subdirectory
    #The idea is to have dictionary with definitions being SUBDIRECTORIES and the keys being the image path
    images_by_dir_1 = {}
    images_by_dir_2 = {}

    #Fill the dictionaries with images, categorized by subdirectory
    for image in all_images_1:
        
        #find relevant relative path from the image to the directory
        subdir = os.path.relpath(os.path.dirname(image), directory_1)
        if subdir not in images_by_dir_1:
            images_by_dir_1[subdir] = []
        images_by_dir_1[subdir].append(image)

    for image in all_images_2:
        subdir = os.path.relpath(os.path.dirname(image), directory_2)
        if subdir not in images_by_dir_2:
            images_by_dir_2[subdir] = []
        images_by_dir_2[subdir].append(image)

    #Initialize lists to contain matched items
    matched_images_1 = []
    matched_images_2 = []

    #iterate through the subdirectories and find common ones
    common_subdirs = set(images_by_dir_1.keys()).intersection(images_by_dir_2.keys())
    different_subdirs = set(images_by_dir_1.keys()).symmetric_difference(images_by_dir_2.keys())

    print(f"Directories {different_subdirs} are not matched.")

    #iterate through common subdirectories and match images
    for subdir in common_subdirs:
        #create temporary variable that stores subdirectories and it's item. NOT AN ARRAY of ALL
        temp_1 = images_by_dir_1[subdir]
        temp_2 = images_by_dir_2[subdir]

        print(temp_2)
        print(f"Processing subdir '{subdir}' with {len(temp_1)} and {len(temp_2)} images respectively.")

        #initialize counting variables
        i, j = 0, 0


        #iterate through while length of the two arrays are less than the values of the initalized variables above
        while i < len(temp_1) and j < len(temp_2):
            file_1 = os.path.basename(temp_1[i])
            file_2 = os.path.basename(temp_2[j])

            #THIS IS WHERE YOU GO TO CHANGE WHAT ATTRIBUTES TO LOOK AT. FOR NOW I CODE BASED ON NAMING, IF WE WANT TO DO ORDER, WE CAN EXPLORE THAT OPTION

            #going by name, if file name are equal (Not directory based)
            if file_1 == file_2:
                matched_images_1.append(temp_1[i])
                matched_images_2.append(temp_2[j])
                i += 1
                j += 1

            #if first file file is less than second i.e. 1,2,3,4 attached at the end
            elif file_1 < file_2:
                matched_images_1.append(temp_1[i])
                matched_images_2.append("MISSING")
                i += 1

            #for the opposite direction, consider this
            else:
                matched_images_1.append("MISSING")
                matched_images_2.append(temp_2[j])
                j += 1

        #Handle remaining unmatched files by appending them appropriately
        while i < len(temp_1):
            matched_images_1.append(temp_1[i])
            matched_images_2.append("MISSING")
            i += 1
        #do the same thing here until length of the array is not less than j
        while j < len(temp_2):
            matched_images_1.append("MISSING")
            matched_images_2.append(temp_2[j])
            j += 1

    #Handle different subdirectories. Listing out all subdirectories, not just the common one
    for subdir in different_subdirs:
        if subdir in images_by_dir_1:
            for image in images_by_dir_1[subdir]:
                matched_images_1.append(image)
                matched_images_2.append("MISSING")
        else:
            for image in images_by_dir_2[subdir]:
                matched_images_1.append("MISSING")
                matched_images_2.append(image)

    #return both list
    return matched_images_1, matched_images_2




#possibly create a show image class to display the two initial pictures and the difference photo?
def main():
    #get file directory
    directory_1 = "C:/Users/rgae/Downloads/D58850_4.02.05"
    directory_2 = "C:/Users/rgae/Downloads/D58850_4.02.05 - Copy"

    #get images from folder
    images1, images2 = getImagesFromFolders(directory_1, directory_2)
 

    #initialize list to store dictionary results for zone differences, filename, and output of the photos
    dictionaryZoneList = []
    fileName_1 = []
    fileName_2 = []
    outputPhoto = []

    #loop the length of the smallest array (to ensure that the lists are comparable) - do this for each subfolder
    for i in range(max(len(images1), len(images2))):
        if os.path.isfile(images1[i]) == True:
            img1_path = Path(images1[i])
        else:
            img1_path = Path("MISSING")

        if os.path.isfile(images2[i]) == True:
            img2_path = Path(images2[i])
        else:
            img2_path = Path("MISSING")

        
        #Open images and convert to RGBA
        if img1_path != Path("MISSING"):
            img1 = Image.open(img1_path).convert('RGBA')
            #Insert FileName if equals path
            fileName_1.append(os.path.join(os.path.basename(os.path.dirname(str(img1_path))), os.path.basename(str(img1_path))))
        elif img1_path == Path("MISSING"):
            img1 = Image.new('RGBA', (1024, 768), (255, 255, 255))
            fileName_1.append("MISSING")
        if img2_path != Path("MISSING"):
            img2 = Image.open(img2_path).convert('RGBA')
            #Insert filename if equals path for fileName_2
            fileName_2.append(os.path.join(os.path.basename(os.path.dirname(str(img2_path))), os.path.basename(str(img2_path))))

        elif img2_path == Path("MISSING"):
            img2 = Image.new('RGBA', (1024, 768), (255, 255, 255))
            fileName_2.append("MISSING")

        #call displayPhotos function
        difference_test = highlightDifference(img1, img2, 1)

        #Save output image
        output_file = saveFile(difference_test, 'difference_name', i + 1)
        outputPhoto.append(output_file)
    

        #calculate the difference in the zones and append new dictionary to the list
        difference_zone = extractROICalculations(img1, img2, zones)
        dictionaryZoneList.append(difference_zone)

        #test
        print(i)


    #Create the necessary DataFrame here
    df_zone = pd.DataFrame(dictionaryZoneList).astype(float)
    df_fileName_1 = pd.DataFrame(fileName_1, columns=['File_Name_1'])
    df_fileName_2 = pd.DataFrame(fileName_2, columns=['File_Name_2'])
    df_outputFile = pd.DataFrame(outputPhoto, columns=['Output File'])

    #create final dataFrame
    final_df = pd.concat([df_zone, df_outputFile, df_fileName_1, df_fileName_2], axis=1)

    final_df.index = final_df.index + 1 #set index + 1 to match the excel spreadsheet w/ headers
    final_df.to_excel('Zone.xlsx', header=True, index=True)

    print(f"File is Done Processing!")
    #draw the new boxes


if __name__ == '__main__':
    main()
