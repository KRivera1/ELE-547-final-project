# Script: StopSign_and Face_detection.py
# Description: This script allows a web camera to be used to detect
#              faces and stop signs. Make sure to install the proper
#              Haar cascade before running this code in order to detect
#              faces.
#              
# 
# Author: Kevin Rivera
# Creation date: 12/05/2020
# Version: v1.0

######################################### Imports ##############################################

import cv2


######################################### Variables ############################################

faceCascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")


######################################### Body #################################################

def getCountours(img):
    contours, heirarchy = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area>2000:
            cv2.drawContours(imgContour,cnt,-1,(255,0,0),2)
            perimeter = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.02*perimeter, True)
            numCorners = len(approx)
            x, y, w, h = cv2.boundingRect(approx)

            if numCorners == 8:
                cv2.rectangle(imgContour,(x,y), (x+w, y+h), (0,255,0), 2)
                cv2.putText(imgContour, "STOP sign", (x + (w//2)-100, y+(h//2)-100), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255,0,0), 2)

            
vid = cv2.VideoCapture(0)
vid.set(3, 640)
vid.set(4, 480)
          
while True:
    success, img = vid.read()
    imgContour = img.copy()
    imgFace = img.copy()
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    imgGray2 = cv2.cvtColor(imgFace, cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(imgGray, (7,7), 1)
    imgCanny = cv2.Canny(imgBlur, 50,50)
    getCountours(imgCanny)
    faces = faceCascade.detectMultiScale(imgGray2, 1.1, 4)
    for (x,y,w,h) in faces:
        cv2.rectangle(imgContour,(x,y),(x+w,y+h), (255,0,0), 2)
        cv2.putText(imgContour, 'Kevin', (x + (w//2)-100, y+(h//2)-100), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255,0,0), 2)
    cv2.imshow("Stop sign detection", imgContour)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break