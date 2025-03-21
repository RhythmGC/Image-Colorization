from fastapi import FastAPI, HTTPException, Body, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import uvicorn
import os
from pydantic import BaseModel
from Storage.cloudinary_upload import upload_image as upload_to_cloudinary
from Storage.cloudinary_upload import delete_image_from_cloudinary, extract_public_id_from_url, save_image
from Model.inference import Gen_Image
from Database.database import (
    ImageBase,
    ImageCreate,
    ImageResponse,
    get_all_images,
    get_image_by_id,
    create_image,
    update_image,
    delete_image
)
import tempfile
import numpy as np
from PIL import Image
import uuid
import cv2

app = FastAPI(title="Image Colorization API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)
@app.get("/")
async def root():
    return {"message": "Hello there, This is the Image Colorization API from RhythmGC and his friend, the NHQM group"}

# Get all images
@app.get("/images", response_model=List[dict], status_code=200)
async def get_images():
    """
    Get all images from the database.
    """
    images = get_all_images()
    return images

# Get image by ID
@app.get("/images/{image_id}", response_model=dict, status_code=200)
async def get_image(image_id: str):
    """
    Get a specific image by its ID.
    """
    image = get_image_by_id(image_id)
    if not image:
        raise HTTPException(status_code=404, detail=f"Image with ID {image_id} not found")
    return image

# Create a new image
@app.post("/images", response_model=dict, status_code=201)
async def create_new_image(image: ImageCreate = Body(...)):
    """
    Create a new image entry in the database.
    """
    image_data = image.dict()
    created_image = create_image(image_data)
    return created_image

# Create a new image with file upload
@app.post("/upload-image", response_model=dict, status_code=201)
async def upload_image(
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    file: UploadFile = File(...),
    auto_colorize: bool = Form(False),  # New parameter to optionally colorize automatically
):
    """
    Upload a new image file to Cloudinary and create an entry in the database.
    If no title is provided, the filename will be used as the title.
    If auto_colorize is True, the image will be colorized automatically.
    """
    try:
        # Read the file content
        content = await file.read()
        
        # Use filename as title if no title is provided
        if title is None:
            # Remove file extension to get cleaner title
            title = os.path.splitext(file.filename)[0]
        
        # Create a temporary file for Cloudinary upload
        temp_file = f"temp_{file.filename}"
        with open(temp_file, "wb") as f:
            f.write(content)
        
        # Upload image to Cloudinary
        cloudinary_url = upload_to_cloudinary(temp_file)
        
        
        # Create image entry in database
        image_data = {
            "title": title,
            "description": description,
            "cloudinary_url": cloudinary_url,
            "colorized": False
        }
        
        print(f"Attempting to save to database: {image_data}")
        created_image = create_image(image_data)
        print(f"Database response: {created_image}")
        
        # If auto_colorize is True, colorize the image
        if auto_colorize and created_image:
            try:
                # Colorize the image
                colorized_image = Gen_Image(cloudinary_url)
                
                # Save colorized image to a temporary file
                colorized_temp_file = f"temp_colorized_{file.filename}"
                cv2.imwrite(colorized_temp_file, colorized_image * 255)  # Convert normalized image back to 0-255 range
                
                # Upload colorized image to Cloudinary
                colorized_cloudinary_url = upload_to_cloudinary(colorized_temp_file)
                
                # Update image entry with colorized information
                update_data = {
                    "colorized": True,
                    "colorized_cloudinary_url": colorized_cloudinary_url
                }
                
                updated_image = update_image(created_image["_id"], update_data)
                
                # Clean up colorized temporary file
                if os.path.exists(colorized_temp_file):
                    os.remove(colorized_temp_file)
                
                # Remove the original temporary file after everything is done
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                
                return updated_image
            except Exception as e:
                print(f"Error in auto-colorizing: {str(e)}")
                # If colorization fails, return the original image
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                return created_image
        
        # Remove the temporary file
        if os.path.exists(temp_file):
            os.remove(temp_file)
        
        if created_image:
            return created_image
        else:
            raise HTTPException(status_code=500, detail="Failed to save image to database")
    except Exception as e:
        print(f"Error in upload_image: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing upload: {str(e)}")

# Update an image
@app.put("/images/{image_id}", response_model=dict, status_code=200)
async def update_existing_image(image_id: str, image_data: dict = Body(...)):
    """
    Update an existing image by ID.
    """
    image = get_image_by_id(image_id)
    if not image:
        raise HTTPException(status_code=404, detail=f"Image with ID {image_id} not found")
    
    updated_image = update_image(image_id, image_data)
    return updated_image

# Delete an image
@app.delete("/images/{image_id}", status_code=200)
async def delete_existing_image(image_id: str):
    """
    Delete an image by ID from both database and Cloudinary storage.
    """
    image = get_image_by_id(image_id)
    if not image:
        raise HTTPException(status_code=404, detail=f"Image with ID {image_id} not found")
    
    cloudinary_deletion_results = []
    
    # Delete original image from Cloudinary if URL exists
    if image.get("cloudinary_url"):
        public_id = extract_public_id_from_url(image["cloudinary_url"])
        if public_id:
            original_deleted = delete_image_from_cloudinary(public_id)
            cloudinary_deletion_results.append({
                "image_type": "original",
                "success": original_deleted
            })
    
    # Delete colorized image from Cloudinary if URL exists
    if image.get("colorized_cloudinary_url"):
        colorized_public_id = extract_public_id_from_url(image["colorized_cloudinary_url"])
        if colorized_public_id:
            colorized_deleted = delete_image_from_cloudinary(colorized_public_id)
            cloudinary_deletion_results.append({
                "image_type": "colorized",
                "success": colorized_deleted
            })
    
    # Delete from database
    success = delete_image(image_id)
    if success:
        return {
            "message": f"Image with ID {image_id} deleted successfully",
            "cloudinary_results": cloudinary_deletion_results
        }
    else:
        raise HTTPException(status_code=500, detail="Failed to delete image from database")

# Colorize an existing image
@app.post("/images/{image_id}/colorize", response_model=dict, status_code=200)
async def colorize_image(image_id: str):
    """
    Colorize an existing image using the ML model and save the result to Cloudinary.
    """
    image = get_image_by_id(image_id)
    if not image:
        raise HTTPException(status_code=404, detail=f"Image with ID {image_id} not found")
    
    if not image.get("cloudinary_url"):
        raise HTTPException(status_code=400, detail="Image doesn't have a valid Cloudinary URL")
    
    try:
        # Get the cloudinary URL from the existing image
        cloudinary_url = image["cloudinary_url"]
        
        # Colorize the image
        colorized_image = Gen_Image(cloudinary_url)
        
        # Generate a temporary filename
        temp_filename = f"temp_colorized_{image_id}.jpg"
        
        # Save colorized image to a temporary file
        cv2.imwrite(temp_filename, colorized_image * 255)  # Convert normalized image back to 0-255 range
        
        # Upload to Cloudinary
        colorized_cloudinary_url = upload_to_cloudinary(temp_filename)
        
        # Remove the temporary file
        os.remove(temp_filename)
        
        update_data = {
            "colorized": True,
            "colorized_cloudinary_url": colorized_cloudinary_url
        }
        
        updated_image = update_image(image_id, update_data)
        return updated_image
    except Exception as e:
        print(f"Error in colorize_image: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error colorizing image: {str(e)}")

# Mark an image as colorized
@app.put("/images/{image_id}/colorize", response_model=dict, status_code=200)
async def mark_as_colorized(image_id: str, colorized_image: UploadFile = File(...)):
    """
    Mark an image as colorized and upload the colorized image to Cloudinary.
    """
    image = get_image_by_id(image_id)
    if not image:
        raise HTTPException(status_code=404, detail=f"Image with ID {image_id} not found")
    
    # Upload colorized image to Cloudinary
    try:
        # Read the uploaded colorized image
        content = await colorized_image.read()
        
        # Create a temporary file for Cloudinary upload
        temp_file = f"temp_colorized_{colorized_image.filename}"
        with open(temp_file, "wb") as f:
            f.write(content)
        
        # Upload to Cloudinary
        colorized_cloudinary_url = upload_to_cloudinary(temp_file)
        
        # Remove the temporary file
        os.remove(temp_file)
        
        update_data = {
            "colorized": True,
            "colorized_cloudinary_url": colorized_cloudinary_url
        }
        
        updated_image = update_image(image_id, update_data)
        return updated_image
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading colorized image: {str(e)}")

# Upload, colorize and save image in one operation
@app.post("/upload-and-colorize", response_model=dict, status_code=201)
async def upload_and_colorize(
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    file: UploadFile = File(...),
):
    """
    Upload an image, save to database, colorize it, and save colorized version to database.
    """
    try:
        # Read the file content
        content = await file.read()
        
        # Use filename as title if no title is provided
        if title is None:
            title = os.path.splitext(file.filename)[0]
        
        # Create a temporary file for Cloudinary upload
        temp_file = f"temp_{file.filename}"
        with open(temp_file, "wb") as f:
            f.write(content)
        
        # Upload original image to Cloudinary
        cloudinary_url = upload_to_cloudinary(temp_file)
        
        # Create image entry in database
        image_data = {
            "title": title,
            "description": description,
            "cloudinary_url": cloudinary_url,
            "colorized": False
        }
        
        created_image = create_image(image_data)
        
        # Colorize the image
        colorized_image = Gen_Image(cloudinary_url)
        
        # Save colorized image to a temporary file
        colorized_temp_file = f"temp_colorized_{file.filename}"
        cv2.imwrite(colorized_temp_file, colorized_image * 255)  # Convert normalized image back to 0-255 range
        
        # Upload colorized image to Cloudinary
        colorized_cloudinary_url = upload_to_cloudinary(colorized_temp_file)
        
        # Update image entry with colorized information
        update_data = {
            "colorized": True,
            "colorized_cloudinary_url": colorized_cloudinary_url
        }
        
        updated_image = update_image(created_image["_id"], update_data)
        
        # Clean up temporary files
        if os.path.exists(temp_file):
            os.remove(temp_file)
        if os.path.exists(colorized_temp_file):
            os.remove(colorized_temp_file)
        
        return updated_image
        
    except Exception as e:
        print(f"Error in upload_and_colorize: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing upload and colorization: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
