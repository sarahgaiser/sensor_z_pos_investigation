import csv
from collections import OrderedDict
from operator import getitem
import itertools

def get_name(long_name):
    split_name = long_name.split('_')
    name = split_name[1]
    if "axial" in long_name:
        name = name + "A"
    elif "stereo" in long_name:
        name = name + "S"

    if "slot" in long_name:
        name = name + "s"
    elif "hole" in long_name:
        name = name + "h"

    return name

def find_ref_sensor(year, volume):
    ref_sensor = ""
    if year == 2016:
        ref_sensor = "L2"
    else:
        ref_sensor = "L3"
    if volume == "top":
        ref_sensor = ref_sensor + "tA"
    else:
        ref_sensor = ref_sensor + "bS"

    return ref_sensor

def determine_rel_z_pos(sensors, year, volume):
    ref_sensor = find_ref_sensor(year, volume)
    ref_pos = sensors[ref_sensor]["z_pos"]
    for sensor_name in sensors.keys():
        sensors[sensor_name]["rel_z_pos"] = sensors[sensor_name]["z_pos"] - ref_pos
    return sensors

def get_sensor_lists_from_file(filename):
    f = open(filename, "r")
    lines = f.readlines()
    f.close()

    top_sensors = {}
    bottom_sensors = {}

    for line in lines:
        split_line = line.split(': ')
        long_name = split_line[0]
        name = get_name(long_name)

        pos = split_line[1].strip("[]\n")
        pos = pos.split(', ')

        if "t" in name:
            top_sensors[name] = {"z_pos": float(pos[2]), "rel_z_pos": 0}
        elif "b" in name:
            bottom_sensors[name] = {"z_pos": float(pos[2]), "rel_z_pos": 0}

        top_sensors = dict(OrderedDict(sorted(top_sensors.items(), key = lambda x: getitem(x[1], 'z_pos'))))
        bottom_sensors = dict(OrderedDict(sorted(bottom_sensors.items(), key = lambda x: getitem(x[1], 'z_pos'))))

    return top_sensors, bottom_sensors

def write_all_sensors_to_csv(sensors_top, sensors_bottom, filename):
    field_names = ["name", "z_pos", "rel_z_pos"]
    all_sensors = {**sensors_top, **sensors_bottom}

    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(field_names)
        for sensor in all_sensors:
            writer.writerow([sensor, all_sensors[sensor]["z_pos"], all_sensors[sensor]["rel_z_pos"]])

def write_multiple_detectors_to_csv(detectors, filename):
    field_names = ["name"]
    for detector in detectors:
        field_names.extend([detector + "_z_pos", detector + "_rel_z_pos"])
    
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(field_names)

        sensor_list = list(detectors[list(detectors.keys())[0]])
        for sensor in sensor_list:
            line = [sensor]
            for detector in detectors:
                if sensor not in detectors[detector]:
                    line.extend(["0.0", "0.0"])
                else:
                    line.extend([detectors[detector][sensor]["z_pos"], detectors[detector][sensor]["rel_z_pos"]])

            writer.writerow(line)

def write_multiple_detectors_to_csv_transposed(detectors, filename, volume="top"):
    if volume == "top":
        field_names = ["detector names", "position", "L1tA", "L1tS", "L2tA", "L2tS", "L3tA", "L3tS", "L4tA", "L4tS",
                       "L5tAs", "L5tAh", "L5tSs", "L5tSh", "L6tAs", "L6tAh", "L6tSs", "L6tSh", "L7tAs", "L7tAh", "L7tSs", "L7tSh"]
    else:
        field_names = ["detector names", "position", "L1bS", "L1bA", "L2bS", "L2bA", "L3bS", "L3bA", "L4bS", "L4bA",
                       "L5bSs", "L5bSh", "L5bAs", "L5bAh", "L6bSs", "L6bSh", "L6bAs", "L6bAh", "L7bSs", "L7bSh", "L7bAs", "L7bAh"]
        
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(field_names)

        for detector in detectors:
            for dist in ["z_pos", "rel_z_pos"]:
                line = [detector, dist]
                for sensor in detectors[detector]:
                    line.append(detectors[detector][sensor][dist])
                if "16" in detector:
                    line.extend([0.0, 0.0])
                writer.writerow(line)

def get_axial_stereo_separation(sensors):
    axial_sensors = {}
    stereo_sensors = {}
    for sensor in sensors:
        if "A" in sensor:
            axial_sensors[sensor] = sensors[sensor]
        elif "S" in sensor:
            stereo_sensors[sensor] = sensors[sensor]

    axial_sensors = dict(OrderedDict(sorted(axial_sensors.items(), key = lambda x: getitem(x[1], 'z_pos'))))
    stereo_sensors = dict(OrderedDict(sorted(stereo_sensors.items(), key = lambda x: getitem(x[1], 'z_pos'))))

    axial_stereo_separation = {}
    for i in range(len(axial_sensors)):
        if "t" in list(axial_sensors.keys())[i]:
            axial_stereo_separation[list(axial_sensors.keys())[i]] = list(stereo_sensors.values())[i]["z_pos"] - list(axial_sensors.values())[i]["z_pos"]
        else:
            axial_stereo_separation[list(stereo_sensors.keys())[i]] = list(axial_sensors.values())[i]["z_pos"] - list(stereo_sensors.values())[i]["z_pos"]

    return axial_stereo_separation

def get_average_position(sensors):
    axial_sensors = {}
    stereo_sensors = {}
    for sensor in sensors:
        if "A" in sensor:
            axial_sensors[sensor] = sensors[sensor]
        elif "S" in sensor:
            stereo_sensors[sensor] = sensors[sensor]

    axial_sensors = dict(OrderedDict(sorted(axial_sensors.items(), key = lambda x: getitem(x[1], 'z_pos'))))
    stereo_sensors = dict(OrderedDict(sorted(stereo_sensors.items(), key = lambda x: getitem(x[1], 'z_pos'))))

    axial_stereo_avg = {}
    for i in range(len(axial_sensors)):
        axial_stereo_avg[i] = (list(stereo_sensors.values())[i]["z_pos"] + list(axial_sensors.values())[i]["z_pos"])/2.0

    return axial_stereo_avg


top_sensors_2019, bottom_sensors_2019 = get_sensor_lists_from_file("geoDumpCat19.txt")
top_sensors_2021, bottom_sensors_2021 = get_sensor_lists_from_file("geoDumpCat21.txt")
top_sensors_ogp, bottom_sensors_ogp = get_sensor_lists_from_file("geoOGP.txt")
top_sensors_2016, bottom_sensors_2016 = get_sensor_lists_from_file("HPS-PhysicsRun2016-Pass2.txt")
top_sensors_2016_db, bottom_sensors_2016_db = get_sensor_lists_from_file("HPS-PhysicsRun2016-Pass2_db.txt")
top_sensors_PhysicsRun2019, bottom_sensors_PhysicsRun2019 = get_sensor_lists_from_file("HPS_PhysicsRun2019_Pass2.txt")
top_sensors_2019_TimDesign, bottom_sensors_2019_TimDesign = get_sensor_lists_from_file("HPS_TimDesign_iter0.txt")
top_sensors_Run2021Pass1_v3, bottom_sensors_Run2021Pass1_v3 = get_sensor_lists_from_file("HPS_Run2021Pass1_v3.txt")

# get_axial_stereo_separation(bottom_sensors2019)
# print(get_average_position(bottom_sensors_2019))

determine_rel_z_pos(top_sensors_2019, 2019, "top")
determine_rel_z_pos(bottom_sensors_2019, 2019, "bottom")

determine_rel_z_pos(top_sensors_2021, 2021, "top")
determine_rel_z_pos(bottom_sensors_2021, 2021, "bottom")

determine_rel_z_pos(top_sensors_ogp, 2019, "top")
determine_rel_z_pos(bottom_sensors_ogp, 2019, "bottom")

determine_rel_z_pos(top_sensors_2016, 2016, "top")
determine_rel_z_pos(bottom_sensors_2016, 2016, "bottom")

determine_rel_z_pos(top_sensors_2016_db, 2016, "top")
determine_rel_z_pos(bottom_sensors_2016_db, 2016, "bottom")

determine_rel_z_pos(top_sensors_PhysicsRun2019, 2019, "top")
determine_rel_z_pos(bottom_sensors_PhysicsRun2019, 2019, "bottom")

determine_rel_z_pos(top_sensors_2019_TimDesign, 2019, "top")
determine_rel_z_pos(bottom_sensors_2019_TimDesign, 2019, "bottom")

determine_rel_z_pos(top_sensors_Run2021Pass1_v3, 2021, "top")
determine_rel_z_pos(bottom_sensors_Run2021Pass1_v3, 2021, "bottom")


# detectors = {"geoDumpCat19": {**top_sensors_2019, **bottom_sensors_2019},
#              "geoDumpCat21": {**top_sensors_2021, **bottom_sensors_2021},
#              "detOGP": {**top_sensors_ogp, **bottom_sensors_ogp},
#              "HPS-PhysicsRun2016-Pass2": {**top_sensors_2016, **bottom_sensors_2016},
#              "HPS-PhysicsRun2016-Pass2_db": {**top_sensors_2016_db, **bottom_sensors_2016_db},
#              "HPS_PhysicsRun2019_Pass2": {**top_sensors_PhysicsRun2019, **bottom_sensors_PhysicsRun2019},
#              "HPS_TimDesign_iter0": {**top_sensors_2019_TimDesign, **bottom_sensors_2019_TimDesign},
#              "HPS_Run2021Pass1_v3": {**top_sensors_Run2021Pass1_v3, **bottom_sensors_Run2021Pass1_v3}}
# write_multiple_detectors_to_csv(detectors, "sensor_positions_master_table.csv")

detectors_top = {"geoDumpCat19": top_sensors_2019,
                 "geoDumpCat21": top_sensors_2021,
                 "detOGP": top_sensors_ogp,
                 "HPS-PhysicsRun2016-Pass2": top_sensors_2016,
                 "HPS-PhysicsRun2016-Pass2_db": top_sensors_2016_db,
                 "HPS_PhysicsRun2019_Pass2": top_sensors_PhysicsRun2019,
                 "HPS_TimDesign_iter0": top_sensors_2019_TimDesign,
                 "HPS_Run2021Pass1_v3": top_sensors_Run2021Pass1_v3}
write_multiple_detectors_to_csv_transposed(detectors_top, "sensor_positions_master_table_top.csv")

detectors_bottom = {"geoDumpCat19": bottom_sensors_2019,
                    "geoDumpCat21": bottom_sensors_2021,
                    "detOGP": bottom_sensors_ogp,
                    "HPS-PhysicsRun2016-Pass2": bottom_sensors_2016,
                    "HPS-PhysicsRun2016-Pass2_db": bottom_sensors_2016_db,
                    "HPS_PhysicsRun2019_Pass2": bottom_sensors_PhysicsRun2019,
                    "HPS_TimDesign_iter0": bottom_sensors_2019_TimDesign,
                    "HPS_Run2021Pass1_v3": bottom_sensors_Run2021Pass1_v3}
write_multiple_detectors_to_csv_transposed(detectors_bottom, "sensor_positions_master_table_bottom.csv", "bottom")

# write_all_sensors_to_csv(top_sensors, bottom_sensors, "sensor_positions_2019.csv")

