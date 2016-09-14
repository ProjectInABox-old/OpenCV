'''
This program uses running average method for background subtraction. 
In the difference image (object image - running average), pixels below threshold value are ignored and contours smaller than min_area are ignored.
'''

import cv2
import numpy as np
from picamera.array import PiRGBArray
from picamera import PiCamera
import argparse, datetime, time
import trackingHelper


if __name__ == '__main__':

    # initialize camera
    camera = PiCamera()
    width = 640
    height = 480
    camera.rotation = 180
    camera.resolution = (width,height)#TODO
    camera.framerate = 10
    rawCapture = PiRGBArray(camera, size=(width,height))

    # warm up and set up
    print 'Warming Up ... 3 seconds'
    time.sleep(3)
    avg = None
    motionCounter = 0
    th = 10 #TODO thresh value for difference image
    min_area = 1000 #TODO min area to filter small contours in diff image
    entrance_coord = (110, 0)
    room_occupied = False
    print 'Starting ...'

    # capture frames from the camera
    for f in camera.capture_continuous(rawCapture, format='bgr', use_video_port=True):
        frame = f.array
	frame = cv2.resize(frame, (width/4, height/4))
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        img = cv2.GaussianBlur(img, (5,5), 0) #TODO kernel size
	img = img.astype(float)
        # initialize background average
        if avg is None:
            avg = img.copy().astype(float) # moving average type must be float
            rawCapture.truncate(0)
            continue
        # update background average
        cv2.accumulateWeighted(img, avg, 0.4)
        diff = cv2.absdiff(img, avg)
        # threshold difference image
	diff = diff.astype(np.uint8)
        ret, diff = cv2.threshold(diff, th, 255, cv2.THRESH_BINARY)
        # dilate thresholded image
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7,7))
        diff = cv2.dilate(diff, kernel, iterations=2)
        cnts, hier = cv2.findContours(diff.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # only keep the big contours
        for cnt in cnts:
            if cv2.contourArea(cnt) < min_area:
                continue
	    frame = trackingHelper.draw_rectangle(cnt, frame)
            print 'Something is moving'
        '''
        # show output frames
        cv2.imshow("Output", frame)
	cv2.imshow('Dilated', diff)
	if cv2.waitKey(1)=='q':
	    break
	'''
        rawCapture.truncate(0)








