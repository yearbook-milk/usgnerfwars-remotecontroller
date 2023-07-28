import cv2
import helpers
import numpy as np
import remote
import pickle
import os

ip = None
port = None
remote.setupParameters()

decision = input("Start in [r]emote mode or [l]ocal control/test mode? ")

if decision == "r":
    if ip == None or port == None:   
        try:
            ip = input("IP address of the remote turret? ")
            port = int(input("TCP port number? "))
            remote.setupParameters(tcpport = port, udpport = 0)
            remote.init_connection(ip)
        except Exception as e:
            print(f"Failed to establish a connection to the remote: {e}")
elif decision == 'l':
    import servo_relay_interface as sri
    pass
else:
    exit()



aimcontrol = np.zeros((300,300,3), np.uint8)
fullwindow = np.zeros((800,1000,3), np.uint8)
unlockControls = True
pitch = 0
yaw = 0


if decision == "r":
    buttons = [
        ["Rev", (0,150,255), lambda: print("Rev command sent.."), (540,50)],
        ["Fire", (0,0,255), lambda: print("Fire command sent.."), (620,50)],
        
        ["Forget Tgt", (255,255,0), lambda: issueCommandTCP("forget"), (540,120)],
        ["LPO", (255,255,255), lambda: issueCommandTCP("toggle_lpo"), (720,120)],
        ["Reinit Pipeln", (0,255,0), lambda: issueCommandTCP("updatepipeline"), (790,120)],
        
        ["Graceful D/C", (0,0,255), lambda: issueCommandTCP("stop"), (800,270)],
        ["Restart", (0,255,255), lambda: issueCommandTCP("restart"), (800,330)],


        ["0", (0,255,255), lambda: issueCommandTCP("select 0"), (540,190)],
        ["1", (0,255,255), lambda: issueCommandTCP("select 1"), (540+(35 * 1),190)],
        ["2", (0,255,255), lambda: issueCommandTCP("select 2"), (540+(35 * 2),190)],
        ["3", (0,255,255), lambda: issueCommandTCP("select 3"), (540+(35 * 3),190)],
        ["4", (0,255,255), lambda: issueCommandTCP("select 4"), (540+(35 * 4),190)],
        ["5", (0,255,255), lambda: issueCommandTCP("select 5"), (540+(35 * 5),190)],
        ["6", (0,255,255), lambda: issueCommandTCP("select 6"), (540+(35 * 6),190)],
        ["7", (0,255,255), lambda: issueCommandTCP("select 7"), (540+(35 * 7),190)],
        ["8", (0,255,255), lambda: issueCommandTCP("select 8"), (540+(35 * 8),190)],
        ["9", (0,255,255), lambda: issueCommandTCP("select 9"), (540+(35 * 9),190)],

        
    ]
else:
    buttons = [
        ["Rev", (0,150,255), lambda: print("Local Rev command sent.."), (540,50)],
        ["Fire", (0,0,255), lambda: print("Local Fire command sent.."), (620,50)],
        ["Quit", (0,0,255), lambda: exit(), (800,570)],
    ]

if decision == "r":
    text = [
        ["Fire Ctrl ->", (255,255,255), 0.8, (350,50)],
        ["AutoCtrl ->", (255,255,255), 0.8, (350,120)],
        ["<- ManualCtrl     Networking ->", (255,255,255), 0.8, (350,260)],
        ["cv2-based GUI Rendering Engine", (255,255,255), 0.4, (10,690)]
    ]
else:
    text = [
        ["Fire Ctrl ->", (255,255,255), 0.8, (350,50)],
        ["AutoCtrl [is disabled]", (255,255,255), 0.8, (350,120)],
        ["<- ManualCtrl     Networking [is disabled]", (255,255,255), 0.8, (350,260)],
        ["cv2-based GUI Rendering Engine  :  LOCAL CONTROL ONLY", (255,255,255), 0.4, (10,690)]
    ]

def UIupdate():
    global fullwindow
    for i in buttons:
        cv2.putText(
            fullwindow,
            i[0],
            (i[3][0] - 4, i[3][1]),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            i[1]
        )
        cv2.rectangle(fullwindow, (i[3][0]-10,i[3][1]-30), (i[3][0]+int(1 * len(i[0]) * 15),i[3][1]+20), i[1], 1)
    for i in text:
        cv2.putText(
            fullwindow,
            i[0],
            (i[3][0], i[3][1]),
            cv2.FONT_HERSHEY_SIMPLEX,
            i[2],
            i[1]
        )

def aimControlUpdate():
    global aimcontrol
    aimcontrol = np.zeros((300,300,3), np.uint8)
    cv2.putText(aimcontrol,"-90", (0,10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255))
    cv2.putText(aimcontrol,"0", (150,10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255))
    cv2.putText(aimcontrol,"+90", (270,10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255))

    cv2.putText(aimcontrol,"0", (270,150), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255))
    cv2.putText(aimcontrol,"-90", (270,270), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255))

    aimcontrol = helpers.line(aimcontrol, "X=", 150, (255,255,255))
    aimcontrol = helpers.line(aimcontrol, "Y=", 150, (255,255,255))
    
    

def onClick(event, x, y, f, p, override = False):
    global fullwindow
    updateVideoFeed()

    
    for i in buttons:
        if (i[3][0]-10 <= x <= i[3][0]+int(1 * len(i[0]) * 15)) and (i[3][1]-30 <= y <= i[3][1]+20):
            if (event == cv2.EVENT_LBUTTONDOWN):
                color = i[1]
                i[2]()
            else: color = (50,50,50)
            
        else:
            color= (0,0,0)
            
        cv2.rectangle(fullwindow, (i[3][0]-10,i[3][1]-30), (i[3][0]+int(1 * len(i[0]) * 15),i[3][1]+20), color, -1)
    
    UIupdate()


    
    if ( 0 <= x <= 300 and 0 <= y <= 300):
        global unlockControls, aimcontrol, pitch, yaw
        if unlockControls or override:
            aimControlUpdate()
            aimcontrol = helpers.line(aimcontrol, "X=", x, (255,0,255))
            aimcontrol = helpers.line(aimcontrol, "Y=", y, (255,0,255))
            pitch = -1 * (int((y/300) * 180) - 90)
            yaw   = +1 * (int((x/300) * 180) - 90)
            # with UDP backwash enabled, we can do this so we can just fire and forget
            if decision == "r": remote.sendTo("UDP", remote.UDP_SOCKET, f"absyaw {yaw};abspitch {pitch};", remote.TCP_REMOTE_PEER)
            else:
                sri.pitch(pitch)
                sri.yaw(yaw)
                pass
        if event == cv2.EVENT_LBUTTONDOWN:
            unlockControls = not unlockControls

        #cv2.putText(aimcontrol, f"client: {pitch}deg pitch, {yaw}deg yaw", (30,270), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,255))
        #cv2.putText(aimcontrol, f"controls unlocked: {unlockControls}", (30,290), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,255))
        print(f"Pitch/yaw command sent: {pitch}deg pitch, {yaw}deg yaw")


def issueCommandTCP(cmd):
    try:
        remote.sendTo("TCP", remote.TCP_CONNECTION, f"{cmd};", remote.TCP_REMOTE_PEER)
        print(f"OK! Sent command {cmd}")
    except Exception as e:
        print(f"TCP CmdSend Error: {e}")
        
    if cmd == 'stop' or cmd == "restart":
        remote.TCP_SOCKET.close()
        remote.UDP_SOCKET.close()
        exit()


def updateVideoFeed():
    global fullwindow
    r = remote.readFrom("UDP", remote.UDP_SOCKET, 65534)
    if r:
        try:
            parts = r.split(b"::::")
            frame = pickle.loads(parts[0])
            parts[2] = pickle.loads(parts[2])
            frame = cv2.resize(frame, (parts[2][1], parts[2][0]))
            
            encoded_txt = pickle.loads(parts[1])
            for i in encoded_txt:
                frame = cv2.putText(frame, i[4], (i[0], i[1]), cv2.FONT_HERSHEY_SIMPLEX, i[3], i[2])

            fullwindow[320:320+frame.shape[0],0:0+frame.shape[1]] = frame
        except Exception as e:
            print(f"Decode error! An error occurred when trying to decode the video data received: {e}")


aimControlUpdate()
UIupdate()
if decision == "r": updateVideoFeed()
cv2.namedWindow("manualcontroltrackpad")
cv2.setMouseCallback('manualcontroltrackpad', onClick)

print("UI initialized!")
while True:
    if decision == "r": updateVideoFeed() 
    fullwindow[0:300,0:300] = aimcontrol
    cv2.imshow("manualcontroltrackpad", fullwindow)
    cv2.waitKey(1)

