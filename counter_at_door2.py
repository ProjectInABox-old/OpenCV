'''
This program uses running average method for background subtraction. 
In the difference image (object image - running average), pixels below threshold
    value are ignored and only the largest contour is kept.
Assuming this camera is on the side of entrance. Left side is door. Walking from
    left to right is entering and walking from right to left is leaving.
The program also counts how many people coming in and leaving the room,
    outputing the number of occupants in the room.
Restrictions:
    - The camera has to be stablized.
    - The background should be fairly consistant.
    - the environment should be well-lit
    - It only detects one person at a time. 
'''

import cv2
import numpy as np
from picamera.array import PiRGBArray
from picamera import PiCamera
import argparse, datetime, time
import trackingHelper


def in_area_one(dist):
    # at door
    if dist>at_door_dist[0] and dist<at_door_dist[1]:
        return True
    return False

def in_area_two(dist):
    # near door
    if dist>near_door_dist[0] and dist<near_door_dist[1]:
        return True
    return False


if __name__ == '__main__':

    # initialize camera
    camera = PiCamera()
    camera.rotation = 180
    width = 640
    height = 480
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
    entrance_coord = np.array([0, height/8])
    room_occupied = False
    dist = 1000 #TODO a random number initialization
    at_door = False
    near_door = False
    at_door_dist = [0,40]
    near_door_dist = [100,120]
    time_init = time.time()
    people_counter = 0
    print 'starting ...'

    # capture frames from the camera
    for f in camera.capture_continuous(rawCapture, format='bgr', use_video_port=True):
        frame = f.array
	frame = cv2.resize(frame, (width/4, height/4))
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        img = cv2.GaussianBlur(img, (5,5), 0) #TODO kernel size
	img = img.astype(float)
        # initialize background average
        if avg is None:
            avg = img.copy().astype(float) # moving average must be float
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
        # only keep the largest contour
	moving = False
	min_area = 1000
        for cnt in cnts:
	    area = cv2.contourArea(cnt)
            if area < min_area:
                continue
	    min_area = area
	    largest_cnt = cnt
	    moving = True
	if moving:
            # draw rectangle and get position of moving object
	    moving = False
	    frame = trackingHelper.draw_rectangle(largest_cnt, frame)
	    object_coord = trackingHelper.find_position(largest_cnt)
	    # use x_dist between entrance and object
	    dist = object_coord[0] - entrance_coord[0]
	if True:
	    # checking leaving
	    if not at_door and not near_door and in_area_two(dist):
		time1 = time.time()
		near_door = True
		#print 'near door'
	    elif near_door:
		time_diff = time.time() - time1
		#print dist
		if time_diff<2 and time_diff>0.3 and in_area_one(dist):
                    near_door = False
		    print 'leaving'
		    people_counter -= 1
		    if people_counter>0:
                        print 'number of occupants:', people_counter
                        print 'room occupied\n'
                    elif people_counter==0:
                        print 'number of occupants:', people_counter
                        print 'room empty\n'
		    else:
                        print 'counting error\n'
		elif time_diff>2:
                    near_door = False
                    dist = 1000
	    # checking entering
	    elif not at_door and not near_door and in_area_one(dist):
		time1 = time.time()
		at_door = True
		#print 'at door'
	    elif at_door:
		time_diff = time.time() - time1
		#print dist
		if time_diff<2 and time_diff>0.3 and in_area_two(dist):
                    at_door = False
		    print 'entering'
		    people_counter += 1
		    if people_counter>-1:
                        print 'number of occupants:', people_counter
                        print 'room occupied\n'
                    elif people_counter==0:
                        print 'number of occupants:', people_counter
                        print 'room empty\n'
		    else:
                        print 'counting error\n'
		elif time_diff>2:
                    at_door = False
                    dist = 1000
	'''
        # show output frames
        cv2.imshow("Output", frame)
	cv2.imshow('Dilated', diff)
	if cv2.waitKey(1)=='q':
	    break
	'''
        rawCapture.truncate(0)








