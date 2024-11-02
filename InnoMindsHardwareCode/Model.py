import cv2
import argparse
from ultralytics import YOLO

# Argument parser to get lane_id and prefix (e.g., A, B) from the command line
parser = argparse.ArgumentParser(description='Run model for specific traffic lane.')
parser.add_argument('lane_id', type=int, help='ID of the traffic lane (0-3)')
parser.add_argument('prefix', type=str, help='Prefix for the lane (e.g., A, B, C)')
args = parser.parse_args()

# Load the model
model = YOLO("model1.pt")

# Path to the video file
video_path = "demoVideo.mp4"

# Set the frame interval to skip frames
frame_interval = 15

# Open the video file
cap = cv2.VideoCapture(video_path)

frame_count = 15
lane_id = args.lane_id  # Assign the provided lane ID
prefix = args.prefix  # Assign the provided prefix (e.g., A, B)

try:
    if not cap.isOpened():
        print("Error opening video file")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frame_interval == 0:
            results = model(frame, conf=0.4)

            for i, result in enumerate(results):
                for box in result.boxes:
                    class_index = int(box.cls)
                    class_name = model.names[class_index] if hasattr(model, 'names') else 'Unknown'

                    # Construct the label with prefix and lane ID
                    label = f"{prefix}{lane_id}"

                    # Write to a text file for processAnalysis.py to read
                    with open(f'{prefix}_lane_{lane_id}_detection.txt', 'w') as f:
                        f.write(f"{label},{class_name}\n")

        frame_count += 1

except Exception as e:
    print(f"Failed to process the video: {e}")
finally:
    cap.release()
    cv2.destroyAllWindows()
