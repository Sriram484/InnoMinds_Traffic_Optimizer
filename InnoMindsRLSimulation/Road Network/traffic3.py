import traci
import sumolib
import math

# Constants
SUMO_CONFIG_FILE = "third.sumocfg"
EMERGENCY_VEHICLE_IDS = ["amu1","amu2","amu3"]
PROXIMITY_THRESHOLD = 30

def main():
    traci.start([sumolib.checkBinary('sumo-gui'), "-c", SUMO_CONFIG_FILE])

    step = 0
    prev_sync = -79 
    next_sync = 0
     
    traffic_lights_state = {
        'B1': {'phase': 0, 'ambulance_override': False, 'override_start_time': 0, 'remaining_seconds': 0},
        'C1': {'phase': 0, 'ambulance_override': False, 'override_start_time': 0, 'remaining_seconds': 0}
    }

    while step < 1500:  
        traci.simulationStep()

        if step % 79 == 0:
            prev_sync += 79
            next_sync += 79

        for tl_id in traci.trafficlight.getIDList():
            for EMERGENCY_VEHICLE_ID in EMERGENCY_VEHICLE_IDS:
                if EMERGENCY_VEHICLE_ID in traci.vehicle.getIDList():
                    controlled_lanes = traci.trafficlight.getControlledLanes(tl_id)
                    road_id = traci.vehicle.getRoadID(EMERGENCY_VEHICLE_ID)

                    matching_lane = find_matching_lane(controlled_lanes, road_id)

                    if matching_lane:
                        amu_pos = traci.vehicle.getPosition(EMERGENCY_VEHICLE_ID)
                        tl_pos = traci.junction.getPosition(tl_id)
                        distance = calculate_distance(amu_pos, tl_pos)

                        if distance <= PROXIMITY_THRESHOLD and not traffic_lights_state[tl_id]['ambulance_override']:
                            print(f" {tl_id} traffic light overridden at step {step} due to incoming ambulance ({EMERGENCY_VEHICLE_ID}).\n")
                            set_ambulance_green_phase(tl_id, road_id)
                            traffic_lights_state[tl_id]['ambulance_override'] = True
                            traffic_lights_state[tl_id]['override_start_time'] = step
                            traffic_lights_state[tl_id]['remaining_seconds'] = next_sync - step

            handle_post_override(tl_id, traffic_lights_state, step, next_sync, prev_sync)

        step += 1

    traci.close()

def find_matching_lane(controlled_lanes, road_id):
    for lane in controlled_lanes:
        if road_id in lane:
            return lane
    return None

def set_ambulance_green_phase(tl_id, road_id):
    current_phase = traci.trafficlight.getPhase(tl_id)

    if road_id[1] == '1' and road_id[3] == '1':
        traci.trafficlight.setPhase(tl_id, 2)  # Green for EW
    elif (road_id[1] == '2' and road_id[3] == '1') or (road_id[1] == '0' and road_id[3] == '1'):
        traci.trafficlight.setPhase(tl_id, 0)  # Green for NS

def handle_post_override(tl_id, traffic_lights_state, step, next_sync, prev_sync):
    state = traffic_lights_state[tl_id]

    if state['ambulance_override']:
        if step - state['override_start_time'] >= 30:
            current_phase = traci.trafficlight.getPhase(tl_id)

            if(current_phase == 0):
                traci.trafficlight.setPhase(tl_id, 1)
            elif(current_phase == 2):
                traci.trafficlight.setPhase(tl_id, 1)

            state['ambulance_override'] = False
            state['phase'] = 0

    phase = traci.trafficlight.getPhase(tl_id)
    if phase == 0:
        if state['phase'] == 0:
            if state['remaining_seconds'] > 0:
                if state['remaining_seconds'] >= 5:
                    traci.trafficlight.setPhaseDuration(tl_id, 35)
                    state['remaining_seconds'] -= 5
                else:
                    duration = 30 + state['remaining_seconds']
                    traci.trafficlight.setPhaseDuration(tl_id, duration)
                    state['remaining_seconds'] = 0
            else:
                traci.trafficlight.setPhaseDuration(tl_id, 30)

            print(f"{tl_id} Trafflic Light")
            print(f"Actual Sync Point   : {prev_sync}")
            print(f"Current Sync Point  : {step}\n")
            # print(f"Next Sync Point     : {next_sync}\n")
            state['phase'] = 1
    else:
        state['phase'] = 0

def calculate_distance(pos1, pos2):
    return math.sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)

if __name__ == "__main__":
    main()
