import socket

import numpy as np
from imumocap import Joint, Link, Matrix


class Connection:
    def __init__(self, ip_address: str = "localhost", port: int = 5000) -> None:
        self.__address = (ip_address, port)

        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.__socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 65535)

        self.__buffer_size = self.__socket.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF)

    def __del__(self) -> None:
        self.__socket.close()

    def send(self, root: Link, joints: dict[str:Joint]) -> None:
        links = {l.name: l for l in root.flatten()}

        neck_alpha, neck_beta, neck_gamma = joints["Neck"].get()

        torso_alpha, torso_beta, torso_gamma = joints["Upper Torso"].get()

        left_shoulder_alpha, left_shoulder_beta, left_shoulder_gamma = joints["Left Shoulder"].get()

        right_shoulder_alpha, right_shoulder_beta, right_shoulder_gamma = joints["Right Shoulder"].get()

        left_elbow_alpha, _, left_elbow_gamma = joints["Left Elbow"].get()

        right_elbow_alpha, _, right_elbow_gamma = joints["Right Elbow"].get()

        left_hand_xyz = links["Left Forearm"].get_end_world().xyz

        left_hand_distance = np.linalg.norm(left_hand_xyz)

        right_hand_xyz = links["Right Forearm"].get_end_world().xyz

        right_hand_distance = np.linalg.norm(right_hand_xyz)

        hands_distance = np.linalg.norm(links["Right Forearm"].get_end_world().xyz - links["Left Forearm"].get_end_world().xyz)

        nwu_to_ned = Matrix(rot_x=180)  # north west up to north east down

        left_glove = (nwu_to_ned * Matrix(rotation=(links["Left Forearm"].get_joint_world() * Matrix.align_py_px_nz()), xyz=links["Left Forearm"].get_end_world().xyz)).quaternion
        right_glove = (nwu_to_ned * Matrix(rotation=(links["Right Forearm"].get_joint_world() * Matrix.align_ny_nx_nz()), xyz=links["Right Forearm"].get_end_world().xyz)).quaternion

        def format(value):
            return f"{value:.6f}"

        json = (
            "{"
            + ",".join(
                [
                    f'"neck":{{"alpha":{format(neck_alpha)},"beta":{format(neck_beta)},"gamma":{format(neck_gamma)}}},'
                    f'"torso":{{"alpha":{format(torso_alpha)},"beta":{format(torso_beta)},"gamma":{format(torso_gamma)}}},'
                    f'"left_shoulder":{{"alpha":{format(left_shoulder_alpha)},"beta":{format(left_shoulder_beta)},"gamma":{format(left_shoulder_gamma)}}},'
                    f'"right_shoulder":{{"alpha":{format(right_shoulder_alpha)},"beta":{format(right_shoulder_beta)},"gamma":{format(right_shoulder_gamma)}}},'
                    f'"left_elbow":{{"alpha":{format(left_elbow_alpha)},"gamma":{format(left_elbow_gamma)}}},'
                    f'"right_elbow":{{"alpha":{format(right_elbow_alpha)},"gamma":{format(right_elbow_gamma)}}},'
                    f'"left_hand_xyz":[{format(left_hand_xyz[0])},{format(left_hand_xyz[1])},{format(left_hand_xyz[2])}],'
                    f'"left_hand_distance": {format(left_hand_distance)},'
                    f'"right_hand_xyz":[{format(right_hand_xyz[0])},{format(right_hand_xyz[1])},{format(right_hand_xyz[2])}],'
                    f'"right_hand_distance":{format(right_hand_distance)},'
                    f'"hands_distance":{format(hands_distance)},'
                    f'"left_glove":[{format(left_glove[0])}, {format(left_glove[1])}, {format(left_glove[2])}, {format(left_glove[3])}],'
                    f'"right_glove":[{format(right_glove[0])}, {format(right_glove[1])}, {format(right_glove[2])}, {format(right_glove[3])}]'
                ]
            )
            + "}"
        )

        data = json.encode("ascii")

        if len(data) > self.__buffer_size:
            raise ValueError(f"The data size is {len(data)}, which exceeds the buffer size of {self.__buffer_size}.")

        self.__socket.sendto(data, self.__address)
