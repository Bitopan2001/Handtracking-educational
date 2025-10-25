import cv2
import time
import numpy as np
import Handtrackingmodule as htm
import math
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
from ctypes import cast, POINTER

wcam, hcam = 640, 480

cap = cv2.VideoCapture(0)
cap.set(3, wcam)
cap.set(4, hcam)
ptime = 0

detector = htm.handDetector(detectionCon=0.7)

# Get system volume interface
devices = AudioUtilities.GetSpeakers()
volume = devices.EndpointVolume

volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]
vol = 0
volBar = 400
volPercent = 0

print(f"Volume Range: {volRange}")

while True:
    success, img = cap.read()
    if not success:
        continue

    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)

    if len(lmList) != 0:
        x1, y1 = lmList[4][1], lmList[4][2]  # thumb
        x2, y2 = lmList[8][1], lmList[8][2]  # index
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        cv2.circle(img, (x1, y1), 10, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (x2, y2), 10, (255, 0, 255), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
        cv2.circle(img, (cx, cy), 8, (255, 0, 255), cv2.FILLED)

        length = math.hypot(x2 - x1, y2 - y1)

        # Convert hand distance to volume level - use different variable name!
        vol = np.interp(length, [50, 300], [minVol, maxVol])
        volBar = np.interp(length, [50, 300], [400, 150])
        volPercent = np.interp(length, [50, 300], [0, 100])
        print(int(length), vol)
        # Set the volume
        volume.SetMasterVolumeLevel(vol, None)
        
        #print(f"Distance: {int(length)}, Volume: {vol:.2f}")

        if length < 50:
            cv2.circle(img, (cx, cy), 10, (0, 255, 0), cv2.FILLED)
    
    cv2.rectangle(img, (50, 150), (85, 400), (0, 255, 0), 3)
    cv2.rectangle(img, (50, int(volBar)), (85, 400), (0, 255, 0), cv2.FILLED)
    cv2.putText(img, f'VOL: {int(volPercent)}%', (40, 450),cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    ctime = time.time()
    fps = 1 / (ctime - ptime)
    ptime = ctime

    cv2.putText(img, f'FPS: {int(fps)}', (10, 70),cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    cv2.imshow("Img", img)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()