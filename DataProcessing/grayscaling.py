import cv2
import shutil

def grayscale(image, fileName,temp_output_path):
    # Convert to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Save the grayscale image
    cv2.imwrite(f"{temp_output_path}/grayscale-{fileName}", gray_image)
    print(f"Image saved in the folder {temp_output_path}/{fileName}")
    print(fileName)
    print(image.shape)
    print(gray_image.shape)
    return gray_image

def copy_paste(source, destination):
    shutil.copy(source, destination)  # Copies content, permissions, and metadata
    print("File copied with metadata successful!")

def processImage(input_path,temp_output_path):
    # Read the image
    image = cv2.imread(input_path)
    filename = input_path.split("/")[-1]
    # Convert the image to grayscale
    copy_paste(input_path, f"{temp_output_path}/{filename}")
    gray_image = grayscale(image,filename,temp_output_path)
    return gray_image


processImage("Data/Frame/VIDEO4/frame_0286.jpg","Data/Presentation1/Data4")