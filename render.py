from __future__ import division
import sys
import numpy as np
import cv2
from caffe_model import *
from render_helper import *


try:
    if len(sys.argv) < 2:
        cap = cv2.VideoCapture("example.mp4")
    else:
        cap = cv2.VideoCapture(sys.argv[1])
except:
    print "Could not open video file"
    raise

# Define the codec and create VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*"X264")
out = cv2.VideoWriter('output.mp4',fourcc, 25, (1280,720))


# Initialize Caffe Model
# Model 1 = mcaug_v1
run_model = 1
net = initialize_caffe(run_model)
net, transformer = preprocessing(net, run_model)


# Training box (area we trained our model on)
x, y = 465, 170    # top-left corner
w, h = 453, 453
circle_center_x, circle_center_y = x + 227, y + 300

avg_angle = 0
avg_technique = 1   # 0 = SMA, 1 = Inverse WMA
smoothing_period = 14   # smooth over 14 frames
circle_x2y2_smoother = [0] * smoothing_period
center_x2, center_y2 = calculate_angle(0, circle_center_x, circle_center_y, radius=100)


while(cap.isOpened()):
    ret, frame = cap.read()
    if ret==True:
        # Create region of interest
        roi = frame[y:y+h, x:x+h]

        # Preprocess 
        roi_resized = cv2.resize(roi, (227, 227), interpolation = cv2.INTER_CUBIC)
        roi_resized[:, :, 0] = cv2.equalizeHist(roi_resized[:, :, 0])
        roi_resized[:, :, 1] = cv2.equalizeHist(roi_resized[:, :, 1])
        roi_resized[:, :, 2] = cv2.equalizeHist(roi_resized[:, :, 2])

        # Use Caffe model to predict
        pred, net_out = predict(net, run_model, transformer, roi_resized)

        # Angle indicator smoother
        # Error reduction: only add frame if within 63 degrees of average
        if abs(pred - avg_angle) <= 63:
            circle_x2y2_smoother.pop(0)
            circle_x2y2_smoother.append(pred)

        # Averaging Techniques:
        if avg_technique == 0:      # SMA
            avg_angle = sum(circle_x2y2_smoother) / len(circle_x2y2_smoother)
        elif avg_technique == 1:    # Inverse WMA (oldest data weighted highest)
            val, weight = 0, 0
            for i in xrange(smoothing_period - 1, -1, -1):    # calculate over 14 frames
                val += (i + 1) * circle_x2y2_smoother[i]
                weight += (i + 1)
            avg_angle = val / weight

        # Draw Angle Indicator
        circle_x2, circle_y2 = calculate_angle(avg_angle, circle_center_x, circle_center_y, radius=70)
        cv2.line(frame, (circle_center_x, circle_center_y), (int(center_x2), int(center_y2)), BLACK, 2) # Center line
        cv2.line(frame, (circle_center_x, circle_center_y), (int(circle_x2), int(circle_y2)), BLACK, 6) # Indicator outline
        cv2.line(frame, (circle_center_x, circle_center_y), (int(circle_x2), int(circle_y2)), WHITE, 2) # Indicator body

        # Draw Dash
        draw_dash(frame, circle_center_x, circle_center_y, avg_angle)

        out.write(frame)
        cv2.imshow('frame',frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break

# Release everything if job is finished
cap.release()
out.release()
cv2.destroyAllWindows()