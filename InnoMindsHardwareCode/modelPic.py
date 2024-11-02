import cv2
import argparse
from ultralytics import YOLO

# Load the model
model = YOLO("model1.pt")

# Path to the video file
image = "dml.jpg"

try:
    results = model(image, conf=0.4)
    for i, result in enumerate(results):
        for box in result.boxes:
            class_index = int(box.cls)
            class_name = model.names[class_index] if hasattr(model, 'names') else 'Unknown'

                 
except Exception as e:
    print(f"Failed to process the video: {e}")

