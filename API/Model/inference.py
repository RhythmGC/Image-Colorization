import tensorflow as tf
import numpy as np
from PIL import Image
import os
import time
import requests
from io import BytesIO
import cv2
import matplotlib.pyplot as plt
# from Model import Generator

# Handle imports for both module usage and direct script execution
try:
    # When used as a module in the package
    from API.Model.Model import Generator
except ImportError:
    # When running directly
    try:
        # Try relative import
        from .Model import Generator
    except ImportError:
        # Direct import when run from the Model directory
        from Model import Generator


def Gen_Image(link):
    SIZE = 256
    req = requests.get(link)
    gray = np.array(Image.open(BytesIO(req.content)))
    shape_init = gray.shape
    gray = cv2.cvtColor(gray, cv2.COLOR_BGR2RGB)
    gray = cv2.resize(gray, (SIZE, SIZE))
    gray = gray / 255.0
    gray_tensor = tf.convert_to_tensor(gray, dtype=tf.float32)
    gray_tensor = tf.expand_dims(gray_tensor, axis=0)  # Add batch dimension
    model = Generator()
    model.load_weights("./API/Model/Weight/modelGen_1.h5")
    prediction = model(gray_tensor, training=False)
    prediction = cv2.resize(np.array(prediction).squeeze(0),[shape_init[1],shape_init[0]])
    return prediction


if __name__ == "__main__":
    start_time = time.time()
    prediction = Gen_Image("https://res.cloudinary.com/rhythmgc/image/upload/v1742544399/DAT/zgfjtm6kzaj1vyixocg1.jpg")
    end_time = time.time()
    print(f"Time taken: {end_time - start_time} seconds")
