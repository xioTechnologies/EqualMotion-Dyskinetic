import time

import imumocap
import imumocap.file
import imumocap.solvers
import imumocap.viewer
from imumocap import Matrix
from imumocap.solvers import Mounting
from imumocap.viewer.primatives import Axes

import hardware
import glover

# Load model
model = imumocap.file.load_model("model.json")

calibration_pose = model.get_pose()

suit = hardware.Ximu3s(model)

# Stream to IMU Mocap Viewer and Glover
viewer_connection = imumocap.viewer.Connection()

glover_connection = glover.Connection()

calibrated_heading = 0

while True:
    time.sleep(1 / 30)  # 30 fps


    if suit.get_button_pressed():
        viewer_connection.send_text("Please Hold the Calibration Pose")

        time.sleep(2)

        calibrated_heading = imumocap.solvers.calibrate(model, suit.get_imus(), calibration_pose, Mounting.Z_FORWARD)

        viewer_connection.send_text("Calibrated", 2)

    model.set_pose_from_imus(suit.get_imus(), -calibrated_heading)

    imumocap.solvers.translate(model, [0, 0, 0.5])

    viewer_connection.send(imumocap.viewer.model_to_primitives(model, mirror="Left"))

    glover_connection.send(model)
