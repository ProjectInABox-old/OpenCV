import numpy as np
import cv2

def draw_rectangle(cnt, frame):
    # draw a rectangle over the moving object, return a new frame
    x,y,w,h = cv2.boundingRect(cnt)
    cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 2)
    return frame

def find_position(cnt):
    # find the center coordinates of a moving object
    x,y,w,h = cv2.boundingRect(cnt)
    coord = np.array([x+w/2, y+h/2])
    return coord
