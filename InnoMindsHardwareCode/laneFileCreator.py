import os

# Define the directory where the text files will be created
directory = "/home/pi/Desktop/Traffic-AnalysisNew/DemoModelTrafficlocation"

# Define user options and lane IDs
user_options = ['A', 'B']
lane_ids = [0, 1, 2, 3]

# Create the directory if it does not exist
os.makedirs(directory, exist_ok=True)

# Create text files for each combination of user option and lane ID
for user in user_options:
    for lane in lane_ids:
        # Define the filename
        filename = f"{user}_lane_{lane}_detection.txt"
        file_path = os.path.join(directory, filename)
        
        # Create the file (it will be empty initially)
        with open(file_path, 'w') as file:
            pass  # Create an empty file

print("Text files created successfully.")
