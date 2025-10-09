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

glover_connection = glover.Connection("10.0.0.9", 5000)

calibrated_heading = 0 

while True:
    time.sleep(1 / 30)  # 30 fps

    if any([i.button_pressed for i in imus.values()]):
        print("Please hold the calibration pose")

        time.sleep(2)

        calibrated_heading = imumocap.solvers.calibrate(root, {n: i.matrix for n, i in imus.items()}, calibration_pose, Mounting.Z_FORWARDS)

        print("Calibrated")

    imumocap.set_pose_from_imus(root, {n: i.matrix for n, i in imus.items()}, -calibrated_heading)

    links = {l.name: l for l in root.flatten()}

    left_forearm = Matrix(rotation=(links["Left Forearm"].get_joint_world() * imumocap.Matrix.align_py_nx_pz()), xyz=links["Left Forearm"].get_end_world().xyz)
    right_forearm = Matrix(rotation=(links["Right Forearm"].get_joint_world() * imumocap.Matrix.align_ny_px_pz()), xyz=links["Right Forearm"].get_end_world().xyz)
    
    viewer_connection.send(
        [
            *imumocap.viewer.link_to_primitives(root),
            *imumocap.viewer.joints_to_primitives(joints, "Left"),
            Axes(left_forearm, 0.25),
            Axes(right_forearm, 0.25)
        ]
    )

    glover_connection.send(root, joints)
