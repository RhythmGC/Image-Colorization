import cv2
import shutil
import os
os.chdir('E:\RhythmGC_Code\DAT\Image-Colorization')
def grayscale(image, fileName,temp_output_path):
    # Convert to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Save the grayscale image
    cv2.imwrite(f"{temp_output_path}/{fileName}", gray_image)
    # print(f"Image saved in the folder {temp_output_path}/{fileName}")
    # print(fileName)
    # print(image.shape)
    # print(gray_image.shape)
    return gray_image

def copy_paste(source, destination):
    shutil.copy(source, destination)  # Copies content, permissions, and metadata

def processImage(input_path,temp_output_path):
    # Read the image
    image = cv2.imread(input_path)
    filename = input_path.split("/")[-1]
    # Convert the image to grayscale
    # copy_paste(input_path, f"{temp_output_path}/{filename}")
    gray_image = grayscale(image,filename,temp_output_path)
    return gray_image

def processFolder(input_folder, output_folder):
    image_files = [f for f in os.listdir(input_folder) if f.endswith(('jpg', 'jpeg', 'png'))]
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    for image_file in image_files:
        print(f"Processing {image_file}")
        processImage(f"{input_folder}/{image_file}", output_folder)

processFolder  ('./Data/original/Color_image/VIDEO1_NhungNguoiVietLenHuyenThoai',
                './Data/original/Grayscale_image/VIDEO1_NhungNguoiVietLenHuyenThoai')
processFolder  ('./Data/original/Color_image/VIDEO2_VaoNamRaBac',
                './Data/original/Grayscale_image/VIDEO2_VaoNamRaBac')
processFolder  ('./Data/original/Color_image/VIDEO3_MuiCoChay',
                './Data/original/Grayscale_image/VIDEO3_MuiCoChay')
processFolder  ('./Data/original/Color_image/VIDEO4_HaNoi12NgayDem',
                './Data/original/Grayscale_image/VIDEO4_HaNoi12NgayDem') 