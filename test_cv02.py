import numpy as np
import cv2
import time
#import math
import sys
import logging
import os
import pickle as p
#logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')
#L(Lab original) = L(OpenCV) * 100/255.0
#a(Lab original) = a(OpenCV) - 128
#b(Lab original) = b(OpenCV) - 128

# "waitkey(0) hält das Programm an !!!!!"

# initialisiere Webcam
cam = cv2.VideoCapture(0)
time.sleep(3)
cam.set(3,1920)
cam.set(4,1080)
time.sleep(1)

x, y, w, h = 640, 360, 100, 100
deltaX= 50
deltaY = 50
start_point_x =985
start_point_y =500
rec_width = 100
rec_hight =300
color = (255, 0, 0)
# Line thickness of 2 px
thickness = 2
region_vol ='region_vol.data' # Datei zum Speichern
region_farb = 'region_farb.data'


font = cv2.FONT_HERSHEY_SIMPLEX
CycleNo = 0

def setup_custom_logger(name):
    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')
    handler = logging.FileHandler('log.txt', mode='w')
    handler.setFormatter(formatter)
    screen_handler = logging.StreamHandler(stream=sys.stdout)
    screen_handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    logger.addHandler(screen_handler)
    return logger

logger = setup_custom_logger('Vol_Measuring')

def loadStoredPosition():
    global start_point_x,start_point_y,end_point_x,end_point_y
    Positionsliste=[]
    try:
        PositionsFile=open("region_vol.data",'r')
    except IOError:
        return[]
    try:
        Positionsliste = [ word.strip() for word in PositionsFile if word ]

        PositionsFile.close

    except:
         logging.info("Positionsfile konnte nicht komplett gelesen werden")
    print("Positionsliste: ", Positionsliste)
    logging.info("Position geladen x ={}".format(Positionsliste[0]))
    start_point_x = int(Positionsliste[0])
    start_point_y = int(Positionsliste[1])
    end_point_x = int(Positionsliste[2])
    end_point_y = int(Positionsliste[3])
    logging.info("Daten: {} {}  {} {}".format(start_point_x,start_point_y,end_point_x,end_point_y))

loadStoredPosition()


while cam.isOpened():
    ret, frame = cam.read()

    time.sleep(1)
    if ret:
        logging.debug("erfolgreich gelesen   {}".format(CycleNo))
        CycleNo += 1
        cv2.imshow("Kaffee-Messung1", frame)
        key = cv2.waitKey(3)
        if key & 0xFF == 27:
            break
        # print (key)
        elif key == 120:  # x-Taste
            start_point_x = start_point_x + 5
            print("startpoint um 5 erhöht ist jetzt: " ,start_point_x)
        elif key == 88:  # Shift-x -Taste
            start_point_x = start_point_x - 5
        elif key == 121:  # yTaste
            start_point_y = start_point_y + 5
        elif key == 89:  # Shift y-Taste
            start_point_y -= 5
        if key == 98:  # b-Taste
            rec_width += 5
        elif key == 66:  # Shift-b -Taste
            rec_width -= 5
        elif key == 104:  # h-Taste
            rec_hight += 5
        elif key == 72:  # Shift h-Taste
            rec_hight -= 5

        end_point_x = start_point_x + rec_width
        end_point_y = start_point_y + rec_hight
         # Using cv2.rectangle() method
        # Draw a rectangle with blue line borders of thickness of 2 px
        start_point =(start_point_x,start_point_y)
        end_point = (end_point_x, end_point_y)
        # das Rechteck beschriften
        cv2.putText(frame, 'ROI', (start_point_x, start_point_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36, 255, 12), 2)
        frame= cv2.rectangle(frame, start_point, end_point, color, thickness)
        cv2.imshow("mit Rahmen", frame)
        key = cv2.waitKey(3)
        if key & 0xFF == 27:
            break
#ermittelte werte in datei schreiben
Positionsliste =[start_point_x,start_point_y, end_point_x,end_point_y]
try:
    PositionFile= open("region_vol.data",'w')
    for k in Positionsliste:
        PositionFile.writelines(str(k)+"\n")
        logging.info("Inhalt  {}".format(str(k)))
    PositionFile.close()

except:
     logging.info("Positionsfile konnte nicht geschrieben werden")

logging.info("Position geschrieben x ={}".format(Positionsliste[0]))


while cam.isOpened():
    ret, frame = cam.read()
    time.sleep(1)
    start = time.time()
    print("start: ", start)
    time.sleep(1)

    frame_crop = frame[start_point_y:start_point_y + rec_hight, start_point_x:start_point_x + rec_width]
    print("gecropped")
    #cv2.imshow(" ROI-new - Auswertebereich", frame_crop)
    #cv2.waitKey(0)

    frame_gray = cv2.cvtColor(frame_crop, cv2.COLOR_BGR2GRAY)
    print("in gray gewandelt")
    # cv2.line(frame_gray,(100,650),(1000,650),255,2)
    # cv2.imshow("das graue Bild",gray)

    y = 0
    x = 0
    zaehler = 0
    schwelle = 160
    schwellen_ctr = 0
    drunter = 0

    print("Bildgröße", np.size(frame_gray, 0), np.size(frame_gray, 1))
    ende = time.time()

    cv2.imshow("V7- aktuelle Graubild", frame_gray)
    if cv2.waitKey(1) & 0xFF == 27:
        break

    _, frame_thre = cv2.threshold(frame_gray, 127, 255, cv2.THRESH_BINARY)
    print("Schwellwert")

    cv2.imshow("SW-Bild", frame_thre)

    #if cv2.waitKey(0) & 0xFF == 27:
        #break

    #frame_thre = cv2.adaptiveThreshold(frame_gray,255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,2)
    #print("Schwellwert")

    #cv2.imshow("SW-Bild", frame_thre)
    if cv2.waitKey(1) & 0xFF == 27:
        break
    # cv2.threshold returns two values: http://docs.opencv.org/modules/imgproc/doc/miscellaneous_transformations.html#cv2.threshold
    #cv2.imshow("V10- aktuelles thre- Bild", frame_thre)
    #cv2.waitKey(0)
    print("zählen der dunklen Pixel")
    zeros = cv2.countNonZero(frame_thre)
    print("Anzahl nicht Null:", zeros)
    #logger.info("Kaffee-Bohnen-Pixel: {} ".format(zeros))
    logger.info(zeros)
    ende = time.time()
    print("Laufzeit: ", '{:5.3f}s'.format(ende - start))