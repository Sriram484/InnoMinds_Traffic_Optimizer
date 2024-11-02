import paho.mqtt.client as mqtt
import time
from collections import deque
import threading
import os
import ssl
import json

# Paths to your certificate, private key, and Root CA file
ca_cert_path = "AmazonRootCA1.pem"   # Replace with the path to your Amazon Root CA
cert_file_path = "certificate.pem.crt"  # Replace with the path to your device certificate
key_file_path = "private.pem.key"    # Replace with the path to your private key

DEFAULT_DELAY = 30

# Default Delaying the execution
print(f"Delaying For {DEFAULT_DELAY}s...")
time.sleep(30)

# Common MQTT setup
# mqtt_broker = "192.168.105.30"
# mqtt_port = 1883

AWS_IOT_ENDPOINT = "a2r4mm3a3xnjy9-ats.iot.ap-south-1.amazonaws.com"
mqtt_port = 8883; 

# Specific setup for Intersection B
mqtt_topic_B = "traffic_lights_B"
mqtt_topic_C = "ambulanceBToC"  # Topic for ESP32 C
mqtt_topic_D = "OverRide"  # Demo

client_B = mqtt.Client()

def on_connect_B(client, userdata, flags, rc):
    print(f"Connected to B with result code {rc}")
    client.subscribe(mqtt_topic_B)
    client.subscribe("ambulanceAToB")
    client.subscribe("OverRideBlock")
    client.subscribe("OverRideUnblock")


def on_message_B(client, userdata, msg):

    print(f"Received message on B '{msg.payload.decode()}' on topic '{msg.topic}'")

    if msg.topic == "ambulanceAToB":
        # Process the ambulance alert from A
        print("Processing ambulance alert from A...")
        # Schedule adding lane 0 to the interrupt queue after 20 seconds
        timer = threading.Timer(20, add_lane_to_interrupt_queue_B, args=[0])
        timer.start()

    elif msg.topic == "OverRideBlock":
        if traffic_cycle_active and not cycle_paused:
            stop_traffic_cycle()

    elif msg.topic == "OverRideUnblock":
        # Resume the traffic cycle
        if cycle_paused:
            resume_traffic_cycle()

    elif msg.topic == "temperature":
        # Print the MQTT topic for demo purposes
        print(f"MQTT Topic for demo: {mqtt_topic_D}")

client_B.on_connect = on_connect_B
client_B.on_message = on_message_B

# client_B.connect(mqtt_broker, mqtt_port, 60)

# Connect to AWS IoT Core
# Configure TLS/SSL
client_B.tls_set(ca_certs=ca_cert_path,
                 certfile=cert_file_path,
                 keyfile=key_file_path,
                 tls_version=ssl.PROTOCOL_TLSv1_2)

client_B.connect(AWS_IOT_ENDPOINT, mqtt_port, 60)
client_B.loop_start()

# Override Functionality
def stop_traffic_cycle():
    """
    Pauses the traffic cycle by setting cycle_paused to True.
    """
    global cycle_paused
    cycle_paused = True
    print("Traffic cycle paused at the current state.")
    send_command_to_arduino(client_B, mqtt_topic_B, "ALL_RED")

def resume_traffic_cycle():
    """
    Resumes the traffic cycle by setting cycle_paused to False and continuing the cycle.
    """
    global cycle_paused, proper_state_index, actual_state_index
    cycle_paused = False
    proper_state_index = 0
    actual_state_index = 0
    print("Resuming the traffic cycle...")

# Timing intervals
normal_green_interval = 10  # seconds for green light during normal cycle
interrupt_green_interval = 15  # seconds for green light when handling an interrupt
yellow_interval = 3  # seconds for yellow light
alert_expiry_time = 30  # seconds to reset the alert status

# Traffic light states
states = ["NS_GREEN", "NS_YELLOW", "EW_GREEN", "EW_YELLOW", "SN_GREEN", "SN_YELLOW", "WE_GREEN", "WE_YELLOW"]

# Track processed alerts and detections
processed_lanes_B = set()
last_detection = {}

# Initial cycle state
proper_state_index = 0
actual_state_index = 0

# Global variable to track traffic cycle state
traffic_cycle_active = True
cycle_paused = False

def send_command_to_arduino(client, mqtt_topic, command):
    # Format the command as a JSON object
    payload = json.dumps({"command": command})
    client.publish(mqtt_topic, payload)
    print(f"Sent to Arduino: {command}, topic: {mqtt_topic}")

def determine_next_intersection(current_intersection, direction):
    next_intersections = {
        'A': {'NS': 'B', 'EW': 'D', 'SN': None, 'WE': 'E'},
        'B': {'NS': 'C', 'EW': 'F', 'SN': 'A', 'WE': 'G'},
        'C': {'NS': 'D', 'EW': 'H', 'SN': 'B', 'WE': 'I'},
    }
    return next_intersections[current_intersection].get(direction, None)

def determine_direction(lane_id):
    directions = {0: 'NS', 1: 'EW', 2: 'SN', 3: 'WE'}
    return directions.get(lane_id, None)

def handle_interrupt_B(lane_id, vehicle_type):
    timestamp = time.time()
    
    if lane_id not in processed_lanes_B:
        print(f"Detected: Lane {lane_id}, Vehicle {vehicle_type}")
        
        # Mark this lane as processed
        processed_lanes_B.add(lane_id)
        last_detection[lane_id] = {'type': vehicle_type, 'time': timestamp}

        if vehicle_type.lower() == "ambulance":
            send_ambulance_alert_B(lane_id, timestamp)
            interrupt_queue_B.append((lane_id, vehicle_type))  # Append as tuple

            if len(interrupt_queue_B) >= 1:
                process_queue_B()
        # Schedule removal of the lane_id from the set after 60 seconds
        schedule_removal_from_set_B(lane_id)

def add_lane_to_interrupt_queue_B(lane_id):
    vehicle_type = "ambulance"  # Assuming you want to handle an ambulance
    handle_interrupt_B(lane_id, vehicle_type)

def send_all_red_command():
    # Code to set all lights to red
    send_command_to_arduino(client_B, mqtt_topic_B, "ALL_RED")
    print("All lights set to red.")

# Queue to handle waiting interrupts
interrupt_queue_B = deque()

def send_ambulance_alert_B(lane_id, timestamp):
    direction = determine_direction(lane_id)
    message = f"AMBULANCE_DETECTED,{lane_id},{direction},{timestamp}"
    next_intersection = determine_next_intersection('B', direction)
    print(next_intersection)

    if next_intersection == 'A':  # If direction is South to North, send to A
        client_B.publish("ambulanceBToA", message)
        print(f"Sent ambulance alert from B to A: {message}")
    elif next_intersection == 'C':  # Normal flow to C
        client_B.publish("ambulanceBToC", message)
        print(f"Sent ambulance alert from B to C: {message}")
    elif next_intersection == 'H':  # Normal flow to C
        client_B.publish("ambulanceBToH", message)
        print(f"Sent ambulance alert from B to C: {message}")
    elif next_intersection == 'I':  # Normal flow to C
        client_B.publish("ambulanceBToI", message)
        print(f"Sent ambulance alert from B to C: {message}")

def schedule_removal_from_set_B(lane_id):
    def remove_from_set():
        processed_lanes_B.discard(lane_id)
        print(f"Lane {lane_id} is now available for new detections.")
    
    timer = threading.Timer(60, remove_from_set)
    timer.start()

def process_queue_B():
    global actual_state_index, proper_state_index,cycle_paused

    while interrupt_queue_B:
        cycle_paused = True
        lane_id, vehicle_type = interrupt_queue_B.popleft()  # Unpack as tuple

        green_state = states[lane_id * 2]
        yellow_state = states[lane_id * 2 + 1]
        current_state = states[actual_state_index]
        
        if current_state == green_state or current_state == yellow_state:
            send_command_to_arduino(client_B, mqtt_topic_B, green_state)
            time.sleep(interrupt_green_interval)
        else:
            if actual_state_index % 2 == 0:
                actual_state_index += 1
                current_state = states[actual_state_index]
            
            print("Current State:", current_state)

            send_command_to_arduino(client_B, mqtt_topic_B, current_state)
            time.sleep(yellow_interval)

            send_command_to_arduino(client_B, mqtt_topic_B, green_state)
            time.sleep(interrupt_green_interval)

            print("%%%%",yellow_state)
            send_command_to_arduino(client_B, mqtt_topic_B, yellow_state)
            time.sleep(yellow_interval)

    # run_normal_cycle_B()
    cycle_paused = False

def run_proper_cycle():
    global proper_state_index
    green_time = normal_green_interval if "GREEN" in states[proper_state_index] else yellow_interval
    time.sleep(green_time)
    proper_state_index = (proper_state_index + 1) % len(states)

def run_actual_cycle():
    global actual_state_index, proper_state_index
    send_command_to_arduino(client_B, mqtt_topic_B, states[actual_state_index])
    green_time = normal_green_interval if "GREEN" in states[actual_state_index] else yellow_interval
    time.sleep(green_time)
    actual_state_index = (actual_state_index + 1) % len(states)
    print("Actual vs. Proper:", actual_state_index, proper_state_index)

    if actual_state_index != proper_state_index:
        resync_cycles()  # Ensure resync_cycles is called after each actual cycle

def run_proper_cycle_thread():
    """
    Continuously runs the proper cycle in a loop, adjusting only the lane index.
    """
    while True:
        run_proper_cycle()

def resync_cycles():
    if cycle_paused:
        print("Resync paused due to traffic cycle stop.")
        return  # Exit the resync process if the cycle is paused

    global actual_state_index, proper_state_index

    # Calculate the difference between the proper and actual state indices
    diff = (proper_state_index - actual_state_index) % len(states)

    if diff == 0:
        print("Cycles are already synchronized.")
        return

    print(f"Resyncing: Proper State = {proper_state_index}, Actual State = {actual_state_index}")
    total_green_time = (diff // 2) * normal_green_interval
    num_green_states = sum(1 for i in range(len(states)) if "GREEN" in states[i])
    time_adjustment_per_lane = total_green_time / num_green_states

    for i in range(len(states)):
        if cycle_paused:
            print("Resync paused due to traffic cycle stop.")
            return  # Exit the resync process if the cycle is paused

        if "GREEN" in states[i]:
            adjusted_green_time = max(normal_green_interval - time_adjustment_per_lane, 5)
            print(f"Adjusting {states[i]} with reduced time: {adjusted_green_time}s")
            send_command_to_arduino(client_B, mqtt_topic_B, states[i])
            time.sleep(adjusted_green_time)

        if "YELLOW" in states[i]:
            send_command_to_arduino(client_B, mqtt_topic_B, states[i])
            time.sleep(yellow_interval)

    print("Resync complete, cycles are now aligned.")
    # Update actual_state_index to match proper_state_index after resync
    actual_state_index = proper_state_index

def run_normal_cycle_B():
    global traffic_cycle_active
    global proper_state_index, actual_state_index
    traffic_cycle_active = True

    # Ensure both cycles are in sync at the start
    proper_state_index = 0
    actual_state_index = 0
    print("Starting traffic light cycle B...")

    proper_thread = threading.Thread(target=run_proper_cycle_thread)
    proper_thread.start()

    while traffic_cycle_active:
        if cycle_paused:
            continue  # Pause the actual cycle if instructed
        run_actual_cycle()

def start_traffic_system():
    global proper_state_index, actual_state_index
    # Reset cycle indices to start synchronized
    proper_state_index = 0
    actual_state_index = 0
    run_normal_cycle_B()

def monitor_lane_files_B():
    lane_file = "B_lane_0_detection.txt"  # Only monitor this specific file
    while True:
        try:
            with open(lane_file, "r") as f:
                line = f.readline().strip()
                if line:  # If there's content in the file
                    parts = line.split(",")
                    if len(parts) == 2:
                        lane_id_str, vehicle_type = parts
                        lane_id = int(lane_id_str[1:])  # Extract lane ID as an integer
                        handle_interrupt_B(lane_id, vehicle_type)  # Handle the detected vehicle
            with open(lane_file, "w") as f:
                f.write("")  # Clear the file after reading
        except FileNotFoundError:
            continue  # If the file isn't found, keep checking

        time.sleep(0.5)  # Short pause to prevent high CPU usage


if __name__ == "__main__":

    # Start monitoring lane files in a separate thread
    monitoring_thread = threading.Thread(target=monitor_lane_files_B)
    monitoring_thread.daemon = True
    monitoring_thread.start()
    print("Started lane monitoring thread.")



    start_traffic_system()
    client_B.loop_stop()
    client_B.disconnect()
