# Script: videoStreamRPiZ_OD.py
# Description: This script allows a live video feed to streamed to a local
#              webserver. This script also includes the ability to detect stop
#              signs. This script was adapted from the link below but heavily modified.
#              https://www.pyimagesearch.com/2019/09/02/opencv-stream-video-to-web-browser-html-page/
#              
# 
# Author: Kevin Rivera
# Creation date: 12/04/2020
# Version: v1.0

######################################### Imports ##############################################

from imutils.video import VideoStream
from flask import Response
from flask import Flask
from flask import render_template
import threading
import argparse
import datetime
import imutils
import time
import cv2


######################################### Variables ############################################

outputFrame = None
lock = threading.Lock()
app = Flask(__name__)
vs = VideoStream(usePiCamera=1).start()
time.sleep(2.0)


######################################### Body #################################################

@app.route("/")
def index():
	return render_template("index.html")

def detect_motion(frameCount):

	global vs, outputFrame, lock

	while True:

		frame = vs.read()
		imgContour = frame.copy()
		frame = imutils.resize(frame, width=400)
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		gray = cv2.GaussianBlur(gray, (7, 7), 0)
		imgCanny = cv2.Canny(gray, 50,50)
		contours, heirarchy = cv2.findContours(imgCanny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2:]
		for cnt in contours:
			peri = cv2.arcLength(cnt, True)
			approx = cv2.approxPolyDP(cnt, 0.02*peri, True)
			objCor = len(approx)
			x, y, w, h = cv2.boundingRect(approx)
			if objCor == 8:
				cv2.rectangle(imgContour,(x-w//4,y-h//4), (x+w//2, y+h//2), (0,255,0), 2)
				cv2.putText(imgContour, "Stop sign", (x + (w//2)-100, y+(h//2)-100), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255,0,0), 2)
			else:
				objectType = " "
			cv2.rectangle(imgContour,(x-w//4,y-h//4), (x+w//2, y+h//2), (0,255,0), 2)
			cv2.putText(imgContour, objectType, (x + (w//2)-100, y+(h//2)-100), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255,0,0), 2)
		with lock:
			outputFrame = imgContour

def generate():
	# grab global references to the output frame and lock variables
	global outputFrame, lock
	while True:
		# wait until the lock is acquired
		with lock:
			# check if the output frame is available, otherwise skip
			# the iteration of the loop
			if outputFrame is None:
				continue
			# encode the frame in JPEG format
			(flag, encodedImage) = cv2.imencode(".jpg", outputFrame)
			# ensure the frame was successfully encoded
			if not flag:
				continue
		# yield the output frame in the byte format
		yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
			bytearray(encodedImage) + b'\r\n')

@app.route("/video_feed")
def video_feed():
	return Response(generate(),
		mimetype = "multipart/x-mixed-replace; boundary=frame")

if __name__ == '__main__':
	ap = argparse.ArgumentParser()
	ap.add_argument("-f", "--frame-count", type=int, default=32,
		help="# of frames used to construct the background model")
	args = vars(ap.parse_args())
	t = threading.Thread(target=detect_motion, args=(
		args["frame_count"],))
	t.daemon = True
	t.start()
	app.run(host='192.168.0.22', debug=True,
		threaded=True, use_reloader=False)
vs.stop()
