import remote, cv2
import numpy as np
import pickle

remote.setupParameters()
try:
    remote.init_connection(input("Addr? "))
except Exception as e:
    print(f"Failed to establish a connection to the remote: {e}")

fn = 1
buffer = b""
while True:
    r = remote.readFrom("UDP", remote.UDP_SOCKET, 65534)
    if r:
        frame = pickle.loads(r)
        frame = cv2.resize(frame, (480,360))
        cv2.imshow("feed", frame)
        

    cv2.waitKey(1)
        

# 10.81.0.156
# 192.168.137.1
