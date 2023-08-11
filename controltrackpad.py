import cv2
import helpers
import numpy as np
import remote
import pickle
import os
import time
import config

ip = None
port = None
cas_portnumber = 8080
remote.setupParameters()

decision = input("Start in [r]emote mode, [l]ocal control mode, or [g]UI test mode? ")

# if on remote mode, open a connection to the remote before going on
if decision == "r":
    if ip == None or port == None:   
        try:
            ip = input("IP address of the remote? ")
            port = int(input("TCP port number of the remote (enter an int)? "))
            remote.setupParameters(tcpport = port, udpport = 0)
            remote.init_connection(ip)
        except Exception as e:
            print(f"Failed to establish a connection to the remote: {e}")
            
# if on local mode, start the hardware software interface so the local client can control servos 
# you ONLY turn on local mode when you are running this on the pi
elif decision == 'l':
    import servo_relay_interface as sri
    sri.config = config.pin_config
    sri.__initialize()
    pass
    
# if on GUI test mode, act as if networking is enabled but don't actually connect anywhere
elif decision == "g":
    pass
    
# if the user didn't pick r, l or g, exit
else:
    exit()



aimcontrol = np.zeros((300,300,3), np.uint8)
fullwindow = np.zeros((900,1000,3), np.uint8)
unlockControls = True
pitch = 0
yaw = 0

# helper method for opening the config client (which allows us to change detection and tracking parameters live)
def openCfg():
    f = open(os.path.abspath('config_client/configurate.html'), "r")
    c = f.read()
    f.close()
    c_old = c
    c = c.replace("$URL", f"{remote.TCP_REMOTE_PEER}:{cas_portnumber}")
    f = open(os.path.abspath('config_client/configurate.html'), "w")
    f.write(c)
    f.close()
    os.system(f"python -m webbrowser file:///{os.path.abspath('config_client/configurate.html')}")
    time.sleep(0.5)
    f = open(os.path.abspath('config_client/configurate.html'), "w")
    f.write(c_old)
    f.close()  

# load GUI elements
if decision == "r" or decision == "g":
    buttons = [
        ["Rev", (0,150,255), lambda: issueCommandTCP("dtoggle rev"), (540,50)],
        ["Fire Auto", (0,0,255), lambda: issueCommandTCP("dtoggle fire"), (620,50)],
        
        ["Stop Track", (255,255,0), lambda: issueCommandTCP("forget"), (540,120)],
        ["LargestPolygonOnly", (255,255,255), lambda: issueCommandTCP("toggle_lpo"), (720,120)],
        ["Apply Changes", (0,255,0), lambda: issueCommandTCP("updatepipeline"), (800,420)],
        ["Config Pipeln", (255,255,0), openCfg, (800,480)],
        
        ["Graceful D/C", (0,0,255), lambda: issueCommandTCP("stop"), (800,270)],


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
        ["Rev", (0,150,255), lambda: sri.toggleRev(), (540,50)],
        ["Fire", (0,0,255), lambda: sri.toggleFire(), (620,50)],
        ["Quit", (0,0,255), lambda: shutdownLmode(), (800,570)],
    ]

if decision == "r" or decision == "g":
    text = [
        ["Fire Ctrl ->", (255,255,255), 0.8, (350,50)],
        ["Auto Aim->", (255,255,255), 0.8, (350,120)],
        ["<- ManualCtrl     Networking ->", (255,255,255), 0.8, (350,260)],
        ["        CV Pipeln ->", (255,255,255), 0.8, (510,420)],
        ["cv2-based GUI Rendering Engine", (255,255,255), 0.4, (10,690)]
    ]
else:
    text = [
        ["Fire Ctrl ->", (255,255,255), 0.8, (350,50)],
        ["AutoCtrl [is disabled]", (255,255,255), 0.8, (350,120)],
        ["<- ManualCtrl     Networking [is disabled]", (255,255,255), 0.8, (350,260)],
        ["cv2-based GUI Rendering Engine  :  LOCAL CONTROL ONLY", (255,255,255), 0.4, (10,690)]
    ]

# renders all GUI elements again
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

# redraws the aim control module in the top left
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
    
    
# on mouse event, such as mouse move or mouse click
def onClick(event, x, y, f, p, override = False):
    global fullwindow
    updateVideoFeed()

    # if the mouse is over any buttons, highlight them
    for i in buttons:
        if (i[3][0]-10 <= x <= i[3][0]+int(1 * len(i[0]) * 15)) and (i[3][1]-30 <= y <= i[3][1]+20):
            # if there was also a click event reported, act on the button
            if (event == cv2.EVENT_LBUTTONDOWN):
                color = i[1]
                i[2]()
            else: color = (50,50,50)
            
        else:
            color= (0,0,0)
            
        cv2.rectangle(fullwindow, (i[3][0]-10,i[3][1]-30), (i[3][0]+int(1 * len(i[0]) * 15),i[3][1]+20), color, -1)
    
    # update the GUI elements (doesn't include buttons, those are handled somewhere else i would think)
    UIupdate()


    # if the mouse event was over the manual control module
    if ( 0 <= x <= 300 and 0 <= y <= 300):
        global unlockControls, aimcontrol, pitch, yaw
        if unlockControls or override:
            # update the UI (this controls the little purple crosshair)
            aimControlUpdate()
            aimcontrol = helpers.line(aimcontrol, "X=", x, (255,0,255))
            aimcontrol = helpers.line(aimcontrol, "Y=", y, (255,0,255))
            
            # translate the position on screen into a pitch yaw command
            pitch = +1 * (float((y/300) * 180) - 90)
            yaw   = +1 * (float((x/300) * 180) - 90)
            
            # send the pitch/yaw command over network, if networking is enabled
            if decision == "r": remote.sendTo("UDP", remote.UDP_SOCKET, f"absyaw {yaw};abspitch {pitch};", remote.TCP_REMOTE_PEER)
            elif decision == "g": pass
            else:
                sri.pitch(pitch)
                sri.yaw(yaw)
                pass
        
        # if the manual control trackpad is clicked, lock or unlock the controls
        if event == cv2.EVENT_LBUTTONDOWN:
            unlockControls = not unlockControls

        #cv2.putText(aimcontrol, f"client: {pitch}deg pitch, {yaw}deg yaw", (30,270), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,255))
        #cv2.putText(aimcontrol, f"controls unlocked: {unlockControls}", (30,290), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,255))
        print(f"Pitch/yaw command sent: {pitch}deg pitch, {yaw}deg yaw")


# heleper method to send a command over TCP
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

# shutdown in L mode
def shutdownLmode():
    sri.__shutdown()
    exit()

# updates the video feed and other information by reading from socket
def updateVideoFeed():
    global fullwindow

    # listen for any commands over the TCP channel
    r = remote.readFrom("TCP", remote.TCP_CONNECTION, 2048)
    if r:
        try:
            r = str(r, "ascii")
            rs = r.split(" ")
            # the first TCP packet the remote should send after connecting is the port number 
            # of the Java config update HTTP server
            if (rs[0] == "casconfig"):
                global cas_portnumber
                cas_portnumber = int(rs[1])
                print("Set the CAS cfg service port number to port#"+str(rs[1]))

        except Exception as e:
            print(f"Decode error! On reading a TCP packet, error on decode: {e}")
    
    # listen for video data over UDP 
    r = remote.readFrom("UDP", remote.UDP_SOCKET, 65534)
    if r:
        try:
            # there are multiple parts of the UDP packet
            parts = r.split(b"::::")
            
            # unpickle the first part, which is the video data stored as a pickled np array
            frame = pickle.loads(parts[0])
            
            # unpickle the dimenion data, which a tuple containing dimensino data
            # its the same format as image_array_numpy.shape
            parts[2] = pickle.loads(parts[2])
            frame = cv2.resize(frame, (parts[2][1], parts[2][0]))
            
            # unpickle the array of text, which is an array of arrays containing information about where to put text and 
            # how to draw it
            # each text element is an array stored as [int x, int y, tuple color, float textsize, string content]
            encoded_txt = pickle.loads(parts[1])
            for i in encoded_txt:
                frame = cv2.putText(frame, i[4], (i[0], i[1]), cv2.FONT_HERSHEY_SIMPLEX, i[3], i[2])

            # after unpacking text data, draw the video on the GUI
            fullwindow[320:320+frame.shape[0],0:0+frame.shape[1]] = frame
        except Exception as e:
            print(f"Decode error! An error occurred when trying to decode the video data received: {e}")


# update everything first and start up a window
aimControlUpdate()
UIupdate()
if decision == "r": updateVideoFeed()
cv2.namedWindow("manualcontroltrackpad")
cv2.setMouseCallback('manualcontroltrackpad', onClick)

print("UI initialized!")

while True:
    # always update the video feed, update the other stuff only on mouse event
    if decision == "r": updateVideoFeed() 
    fullwindow[0:300,0:300] = aimcontrol
    cv2.imshow("manualcontroltrackpad", fullwindow)
    kb = cv2.waitKey(1)

    # press a button when a key is pressed
    # (for instance, pressing 'g' will press the button that starts with "G" or "g", which in this case is "Graceful D/C"
    for i in buttons:
        if kb > 1:
            if kb == ord(i[0][0].lower()):
                print(f"Function key selected using the keyboard: {kb}->{i[0].lower()}")
                i[2]()    
