import os
from PIL import Image
import tkinter as tk
from tkinter import filedialog
import pandas as pd
import numpy as np
import cv2
from PIL import ImageChops, ImageEnhance

# Define zones
zones = {
    'Time': [900, 1024, 0, 50],
    'Version': [785, 900, 0, 50],
    'Language': [0, 200, 0, 50],
    'Entire Image': [0, 1024, 0, 768]
}

# Calculate differences in specified zones
def extractROICalculations(image_1, image_2, zones):
    assert image_1.size == image_2.size, "Images are not the same size."
    data_array1 = np.asarray(image_1)
    data_array2 = np.asarray(image_2)
    ROI_dic = {}

    for zone_name, zone_coords in zones.items():
        col1, col2, row1, row2 = zone_coords
        roi_1 = data_array1[row1:row2, col1:col2]
        roi_2 = data_array2[row1:row2, col1:col2]
        roi_difference = np.abs(roi_2 - roi_1)
        channel_difference_sum = np.sum(roi_difference, axis=-1)
        non_zero = np.count_nonzero(channel_difference_sum)
        area = (col2 - col1) * (row2 - row1)
        area_zone = (non_zero / area) * 100
        formatted_area_zone = round(area_zone, 2)
        ROI_dic[zone_name] = formatted_area_zone

    return ROI_dic

# Visualize zones on the image
def zoneVisual(image, zones):
    image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGBA2RGB)
    for zone_index, zone in zones.items():
        col1, col2, row1, row2 = zone
        image_cv = cv2.rectangle(image_cv, (col1, row1), (col2, row2), (255, 0, 0), lineType=1)
        image_cv = cv2.putText(image_cv, zone_index, (col1, row1-10), cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5, color=(255, 255, 255), thickness=1, lineType=cv2.LINE_AA)
    return Image.fromarray(cv2.cvtColor(image_cv, cv2.COLOR_BGR2RGB))

# Get images from a folder
def getImagesFolder(folder_path):
    images = []
    for file_name in os.listdir(folder_path):
        if file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
            images.append(os.path.join(folder_path, file_name))
    return images

# Highlight differences between two images
def highlightDifference(image_1, image_2, opacity):
    image_1 = image_1.convert('RGBA')
    image_2 = image_2.convert('RGBA')
    diff_temp = ImageChops.difference(image_1, image_2)
    diff_temp = np.array(diff_temp)
    mask = (diff_temp[:, :, :3] != [0, 0, 0]).any(axis=-1)
    diff_temp[mask] = [255, 0, 0, 255]
    diff_final = Image.fromarray(diff_temp, 'RGBA')
    image_2.putalpha(int(opacity * 255))
    image_2 = ImageEnhance.Contrast(image_2).enhance(0.6)
    image_2 = ImageEnhance.Brightness(image_2).enhance(1.2)
    final = Image.alpha_composite(image_2, diff_final)
    return final

# Calculate the percentage difference between two images
def calcDiffPhoto(image_1, image_2):
    differenceInPhoto = ImageChops.difference(image_1, image_2)
    diff_array = np.array(differenceInPhoto)
    non_zero = np.count_nonzero(diff_array)
    total_arrays = diff_array.size
    return (non_zero / total_arrays) * 100

# Save the processed image
def saveFile(image, base_name, counter):
    path_file = os.path.join(os.getenv('USERPROFILE'), 'Downloads', 'Picture Difference')
    if not os.path.isdir(path_file):
        os.makedirs(path_file)
    file_path = os.path.join(path_file, f'{base_name}_{counter}.png')
    image.save(file_path)
    return f'{base_name}_{counter}.png'

# Process images folder by folder
def processImagesFromFolders(folder_1, folder_2):
    results = []
    counter = 1

    for root_1, _, files_1 in os.walk(folder_1):
        for root_2, _, files_2 in os.walk(folder_2):
            common_files = set(files_1).intersection(files_2)

            for file_name in common_files:
                if file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                    image_path_1 = os.path.join(root_1, file_name)
                    image_path_2 = os.path.join(root_2, file_name)

                    img1 = Image.open(image_path_1).convert('RGBA')
                    img2 = Image.open(image_path_2).convert('RGBA')

                    difference_test = highlightDifference(img1, img2, 1)
                    output_file_name = saveFile(difference_test, 'difference_name', counter)
                    difference_zone = extractROICalculations(img1, img2, zones)

                    results.append((os.path.basename(image_path_1), os.path.basename(image_path_2), difference_zone, output_file_name))
                    counter += 1

    return results

# Main function
def main():
    root = tk.Tk()
    root.withdraw()

    folder_1 = filedialog.askdirectory()
    folder_2 = filedialog.askdirectory()

    results = processImagesFromFolders(folder_1, folder_2)

    file_names_1, file_names_2, zones_data, output_files = zip(*results)

    df_zone = pd.DataFrame(zones_data).astype(float)
    df_fileName_1 = pd.DataFrame(file_names_1, columns=['File_Name_1'])
    df_fileName_2 = pd.DataFrame(file_names_2, columns=['File_Name_2'])
    df_outputFile = pd.DataFrame(output_files, columns=['Output File'])

    final_df = pd.concat([df_fileName_1, df_fileName_2, df_zone, df_outputFile], axis=1)
    final_df.index = final_df.index + 1
    final_df.to_excel('Zone.xlsx', header=True, index=True)

    example_image = Image.open(os.path.join(folder_1, file_names_1[0])).convert('RGB')
    visual_zone = zoneVisual(example_image, zones)
    visual_zone.save('example_zone.png')

    print("Done Processing")

if __name__ == '__main__':
    main()
