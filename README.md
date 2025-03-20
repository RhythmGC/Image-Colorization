# Image Colorization API

A FastAPI-based API for image colorization with MongoDB Atlas integration.

## Features

- Upload and store original images
- Retrieve all images or a specific image by ID
- Update image information
- Delete images
- Mark images as colorized with path to colorized version

## Setup

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the root directory with your MongoDB Atlas credentials:
   ```
   ATLAS_PASSWORD=your_password_here
   ```
4. Update the MongoDB connection string in `API/database.py` if needed

## Running the API

Start the FastAPI server:

```bash
cd API
python main.py
```

The API will be available at http://localhost:8000

## API Documentation

Once the server is running, you can access the automatic interactive API documentation at:
- http://localhost:8000/docs (Swagger UI)
- http://localhost:8000/redoc (ReDoc)

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | / | Welcome message |
| GET | /images | Get all images |
| GET | /images/{image_id} | Get a specific image by ID |
| POST | /images | Create a new image entry |
| POST | /upload-image | Upload an image file and create database entry |
| PUT | /images/{image_id} | Update an existing image |
| DELETE | /images/{image_id} | Delete an image |
| PUT | /images/{image_id}/colorize | Mark an image as colorized |

## Example Usage

### Upload an image
```bash
curl -X POST "http://localhost:8000/upload-image" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/your/image.jpg"
```

The API will use the filename (without extension) as the title if no title is provided. If you want to specify a custom title:

```bash
curl -X POST "http://localhost:8000/upload-image" \
  -H "Content-Type: multipart/form-data" \
  -F "title=My Custom Title" \
  -F "description=A beautiful landscape" \
  -F "file=@/path/to/your/image.jpg"
```

### Get all images
```bash
curl -X GET "http://localhost:8000/images"
```

### Mark an image as colorized
```bash
# Using curl to upload a colorized image file
curl -X PUT "http://localhost:8000/images/123456789/colorize" \
  -F "colorized_image=@/path/to/colorized/image.jpg"
```
