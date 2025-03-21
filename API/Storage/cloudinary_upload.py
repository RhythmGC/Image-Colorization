import cloudinary
import os
import cloudinary.uploader as uploader
import cloudinary.api
import dotenv
import requests

dotenv.load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True,
)

def upload_image(image_path: str):
    if os.path.exists(image_path):
        print(f"Uploading image: {image_path}")
        result = uploader.upload(image_path, folder="DAT")
        print(f"Upload successful! Image URL: {result['secure_url']}")
        
    else:
        print(f"File does not exist: {image_path}")

    return result["secure_url"]

def delete_image_from_cloudinary(public_id: str):
    """
    Deletes an image from Cloudinary by its public ID.
    The public_id should include the folder, e.g., 'DAT/image_name'.
    Returns True if successful, False otherwise.
    """
    try:
        print(f"Deleting image with public ID: {public_id}")
        result = uploader.destroy(public_id)
        print(f"Delete result: {result}")
        return result.get("result") == "ok"
    except Exception as e:
        print(f"Error deleting image from Cloudinary: {str(e)}")
        return False

def extract_public_id_from_url(url: str):
    """
    Extracts the public ID from a Cloudinary URL.
    Example: https://res.cloudinary.com/cloud_name/image/upload/v1234567890/DAT/image_name.jpg -> DAT/image_name
    """
    try:
        parts = url.split('/')
        # Find the upload part
        upload_index = parts.index('upload')
        # Skip the version part (v1234567890)
        version_index = upload_index + 1
        # Join all parts after the version, removing the file extension
        remaining_parts = parts[version_index+1:]
        filename_with_ext = remaining_parts[-1]
        filename_without_ext = os.path.splitext(filename_with_ext)[0]
        remaining_parts[-1] = filename_without_ext
        return '/'.join(remaining_parts)
    except (ValueError, IndexError) as e:
        print(f"Error extracting public ID from URL {url}: {str(e)}")
        return None

def retrive_image(image_url: str):
    response = requests.get(image_url)
    return response.content

def save_image(image_url: str, image_name: str):
    image = retrive_image(image_url)
    with open(image_name, "wb") as f:
        f.write(image)




