import time

import imumocap
import imumocap.file
import imumocap.solvers
import imumocap.viewer
from imumocap import Matrix
from imumocap.solvers import Mounting
from imumocap.viewer.primatives import Axes

import glover
import ximu3s

# Load model
root, joints = imumocap.file.load_model("model.json")

calibration_pose = imumocap.get_pose(root)

# Connect to and configure IMUs
imus = ximu3s.setup([l.name for l in root.flatten() if l.name])

# Stream to IMU Mocap Viewer and Glover
viewer_connection = imumocap.viewer.Connection()

glover_connection = glover.Connection()

calibrated_heading = 0

capture_pose = False

while True:
    time.sleep(1 / 30)  # 30 fps

    if any([i.button_pressed for i in imus.values()]):    

        if capture_pose: 
            print("Please hold your custom calibration pose")

            time.sleep(5)
            
            temp_imus = {n: i.matrix for n, i in imus.items()}

            calibrated_heading = (temp_imus[root.name] * Mounting.Z_FORWARDS.value).rot_xyz[2]

            imumocap.set_pose_from_imus(root, {n: i.matrix for n, i in imus.items()}, -calibrated_heading)

            imumocap.file.save_pose("custom_pose.json", joints)

            print("Saved current pose to 'custom_pose.json'")
            
        else: 
            print("Please hold the calibration pose")

            time.sleep(5)

            calibrated_heading = imumocap.solvers.calibrate(root, {n: i.matrix for n, i in imus.items()}, calibration_pose, Mounting.Z_FORWARDS)

            print("Calibrated")

        capture_pose = not capture_pose
                

    imumocap.set_pose_from_imus(root, {n: i.matrix for n, i in imus.items()}, -calibrated_heading)

    imumocap.solvers.translate(root, [0, 0, 0.5])

    links = {l.name: l for l in root.flatten()}

    viewer_connection.send(
        [
            *imumocap.viewer.link_to_primitives(root),
            *imumocap.viewer.joints_to_primitives(joints, "Left"),
        ]
    )

    glover_connection.send(root, joints)
