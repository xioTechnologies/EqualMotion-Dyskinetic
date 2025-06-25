import socket

import numpy as np
from imumocap import Joint, Link


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

        neck_bend, neck_tilt, neck_twist = joints["Neck"].get()

        torso_bend, torso_tilt, torso_twist = joints["Upper Torso"].get()

        left_shoulder_bend, left_shoulder_tilt, left_shoulder_twist = joints["Left Shoulder"].get()

        right_shoulder_bend, right_shoulder_tilt, right_shoulder_twist = joints["Right Shoulder"].get()

        left_elbow_bend, _, left_elbow_twist = joints["Left Elbow"].get()

        right_elbow_bend, _, right_elbow_twist = joints["Right Elbow"].get()

        left_hand_xyz = links["Left Forearm"].get_end_world().xyz - root.get_joint_world().xyz

        left_hand_distance = np.linalg.norm(left_hand_xyz)

        right_hand_xyz = links["Right Forearm"].get_end_world().xyz - root.get_joint_world().xyz

        right_hand_distance = np.linalg.norm(right_hand_xyz)

        hands_distance = np.linalg.norm(links["Right Forearm"].get_end_world().xyz - links["Left Forearm"].get_end_world().xyz)

        def format(value):
            return f"{value:.6f}"

        json = (
            "{"
            + ",".join(
                [
                    f'"neck":{{"bend":{format(neck_bend)},"tilt":{format(neck_tilt)},"twist":{format(neck_twist)}}},'
                    f'"torso":{{"bend":{format(torso_bend)},"tilt":{format(torso_tilt)},"twist":{format(torso_twist)}}},'
                    f'"left_shoulder":{{"bend":{format(left_shoulder_bend)},"tilt":{format(left_shoulder_tilt)},"twist":{format(left_shoulder_twist)}}},'
                    f'"right_shoulder":{{"bend":{format(right_shoulder_bend)},"tilt":{format(right_shoulder_tilt)},"twist":{format(right_shoulder_twist)}}},'
                    f'"left_elbow":{{"bend":{format(left_elbow_bend)},"twist":{format(left_elbow_twist)}}},'
                    f'"right_elbow":{{"bend":{format(right_elbow_bend)},"twist":{format(right_elbow_twist)}}},'
                    f'"left_hand_xyz":[{format(left_hand_xyz[0])},{format(left_hand_xyz[1])},{format(left_hand_xyz[2])}],'
                    f'"left_hand_distance": {format(left_hand_distance)},'
                    f'"right_hand_xyz":[{format(right_hand_xyz[0])},{format(right_hand_xyz[1])},{format(right_hand_xyz[2])}],'
                    f'"right_hand_distance":{format(right_hand_distance)},'
                    f'"hands_distance":{format(hands_distance)}'
                ]
            )
            + "}"
        )

        data = json.encode("ascii")

        if len(data) > self.__buffer_size:
            raise ValueError(f"The data size is {len(data)}, which exceeds the buffer size of {self.__buffer_size}.")

        self.__socket.sendto(data, self.__address)
