import os
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split

# Define base directories
base_dir = Path("Data/original")
color_dir = base_dir / "Color_image"
gray_dir = base_dir / "Grayscale_image"

# Lists to store data
file_names = []
color_paths = []
gray_paths = []

# Iterate through video directories in the color directory
for video_folder in os.listdir(color_dir):
    color_video_path = color_dir / video_folder
    gray_video_path = gray_dir / video_folder
    
    # Make sure the directory exists in both color and grayscale folders
    if os.path.isdir(color_video_path) and os.path.isdir(gray_video_path):
        # Get all color images
        color_images = [f for f in os.listdir(color_video_path) if f.endswith('.jpg')]
        
        for img_name in color_images:
            # Extract frame name without extension
            frame_base = os.path.splitext(img_name)[0]
            
            # Add data to lists with relative paths (without Color_image or grayscale-image)
            file_names.append(frame_base)
            
            # Format paths with forward slashes
            color_path = f"Color_image/{video_folder}/{img_name}"
            color_paths.append(color_path)
            
            # Check if the corresponding grayscale image exists
            gray_image_path = gray_video_path / img_name
            if os.path.exists(gray_image_path):
                gray_path = f"Grayscale_image/{video_folder}/{img_name}"
                gray_paths.append(gray_path)
            else:
                # If no exact match, try to find any grayscale image with the same frame prefix
                prefix = frame_base.split('_')[0]  # Get 'frame' prefix
                matching_gray_images = [f for f in os.listdir(gray_video_path) 
                                    if f.startswith(prefix) and f.endswith('.jpg')]
                
                if matching_gray_images:
                    # Use the first match if multiple are found
                    gray_path = f"grayscale-image/{video_folder}/{matching_gray_images[0]}"
                    gray_paths.append(gray_path)
                else:
                    # No matching grayscale image found
                    gray_paths.append("")

# Create DataFrame
data = {
    'fileName': file_names,
    'colorPath': color_paths,
    'grayPath': gray_paths
}

df = pd.DataFrame(data)

# First split: 70% train, 30% temp (which will be split into val and test)
train_df, temp_df = train_test_split(df, test_size=0.3, random_state=42)

# Second split: Split temp into val and test (1/3 val, 2/3 test)
val_df, test_df = train_test_split(temp_df, test_size=0.67, random_state=42)

# Save to CSV files
output_dir = base_dir.parent
train_df.to_csv(output_dir / "train.csv", index=False)
val_df.to_csv(output_dir / "val.csv", index=False)
test_df.to_csv(output_dir / "test.csv", index=False)

print(f"CSV files created in {output_dir}")
print(f"Total images processed: {len(file_names)}")
print(f"Train set size: {len(train_df)} ({len(train_df)/len(df)*100:.1f}%)")
print(f"Validation set size: {len(val_df)} ({len(val_df)/len(df)*100:.1f}%)")
print(f"Test set size: {len(test_df)} ({len(test_df)/len(df)*100:.1f}%)")
