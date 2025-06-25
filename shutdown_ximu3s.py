import time

import ximu3

connections = [ximu3.Connection(m.to_udp_connection_info()) for m in ximu3.NetworkAnnouncement().get_messages_after_short_delay()]

for connection in connections:
    connection.open()

for connection in connections:
    connection.send_commands_async(['{"shutdown":null}'], 2, 500, lambda _: None)

time.sleep(2)

for connection in connections:
    connection.close()
