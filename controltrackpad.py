import cv2
import helpers
import numpy as np

aimcontrol = np.zeros((300,300,3), np.uint8)
fullwindow = np.zeros((700,1000,3), np.uint8)
unlockControls = True
pitch = 0
yaw = 0

buttons = [
    ["Rev", (0,150,255), lambda: print("Rev command sent.."), (540,50)],
    ["Fire", (0,0,255), lambda: print("Fire command sent.."), (620,50)],
    
    ["Forget Tgt", (255,255,0), lambda: print("Forget target command sent.."), (540,120)],
    ["LPO Toggle", (255,255,255), lambda: print("LPOT target command sent.."), (720,120)],

    ["0", (0,255,255), lambda: print("0 select command sent.."), (540,190)],
    ["1", (0,255,255), lambda: print("1 select command sent.."), (540+(35 * 1),190)],
    ["2", (0,255,255), lambda: print("2 select command sent.."), (540+(35 * 2),190)],
    ["3", (0,255,255), lambda: print("3 select command sent.."), (540+(35 * 3),190)],
    ["4", (0,255,255), lambda: print("4 select command sent.."), (540+(35 * 4),190)],
    ["5", (0,255,255), lambda: print("5 select command sent.."), (540+(35 * 5),190)],
    ["6", (0,255,255), lambda: print("6 select command sent.."), (540+(35 * 6),190)],
    ["7", (0,255,255), lambda: print("7 select command sent.."), (540+(35 * 7),190)],
    ["8", (0,255,255), lambda: print("8 select command sent.."), (540+(35 * 8),190)],
    ["9", (0,255,255), lambda: print("9 select command sent.."), (540+(35 * 9),190)],

    
]

text = [
    ["Fire Ctrl ->", (255,255,255), 0.8, (350,50)],
    ["AutoCtrl ->", (255,255,255), 0.8, (350,120)],
    ["<- ManualCtrl", (255,255,255), 0.8, (350,260)],
    ["cv2-based UI engine demo: github.com/yearbook-milk/usgnerfwars-remotecontroller", (255,255,255), 0.5, (10,690)]   

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
    fullwindow = np.zeros((700,1000,3), np.uint8)

    
    for i in buttons:
        if (i[3][0]-10 <= x <= i[3][0]+int(1 * len(i[0]) * 15)) and (i[3][1]-30 <= y <= i[3][1]+20):
            if (event == cv2.EVENT_LBUTTONDOWN):
                color = i[1]
                i[2]()
            else: color = (50,50,50)
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
        if event == cv2.EVENT_LBUTTONDOWN:
            unlockControls = not unlockControls

        #cv2.putText(aimcontrol, f"client: {pitch}deg pitch, {yaw}deg yaw", (30,270), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,255))
        #cv2.putText(aimcontrol, f"controls unlocked: {unlockControls}", (30,290), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,255))
        print(f"Pitch/yaw command sent: {pitch}deg pitch, {yaw}deg yaw")

aimControlUpdate()
UIupdate()
cv2.namedWindow("manualcontroltrackpad")
cv2.setMouseCallback('manualcontroltrackpad', onClick)

print("UI initialized!")
while True:
    fullwindow[0:300,0:300] = aimcontrol
    cv2.imshow("manualcontroltrackpad", fullwindow)
    cv2.waitKey(1)

