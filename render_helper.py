import numpy as np
import cv2
import math


# Colors (B, G, R)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (0, 0, 255)
ORANGE = (0, 110, 250)


def calculate_angle(angle, x, y, radius):
    angle = math.radians(-90 - angle)
    circle_x = x + radius * math.cos(angle)
    circle_y = y + radius * math.sin(angle)
    return circle_x, circle_y


def draw_half_circle(frame, x, y, color, thickness):
    radius=100
    axes = (radius,radius)
    angle = 0
    startAngle = 0
    endAngle = -180
    center = (x, y)
    cv2.ellipse(frame, center, axes, angle, startAngle, endAngle, color, thickness)


def draw_redzone(frame, x, y):
    overlay = frame.copy()
    radius=98
    axes = (radius,radius)
    angle = 0
    startAngle = 0
    endAngle = -45
    center = (x, y)
    thickness = -1
    color = (0,0,255)
    alpha = 0.3
    cv2.ellipse(overlay, center, axes, angle, startAngle, endAngle, color, thickness)
    cv2.ellipse(overlay, center, axes, angle, -135, -180, color, thickness)
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)


def draw_dash(frame, circle_center_x, circle_center_y, avg_angle):
    draw_redzone(frame, circle_center_x, circle_center_y)
    draw_half_circle(frame, circle_center_x, circle_center_y, BLACK, thickness=10)

    # Draw Colored Arc + Colored Angle Text
    if avg_angle >= 40 or avg_angle <= -40:
        draw_half_circle(frame, circle_center_x, circle_center_y, RED, thickness=6)
        # Need to compensate for angle orientation
        # Biker leaning left = positive prediction, photo rotates right (+)
        # Biker leaning right = negative prediction, photo rotates left (-)
        cv2.putText(frame, "{0:0.1f}".format(avg_angle * -1), (circle_center_x - 40, circle_center_y - 120), cv2.FONT_HERSHEY_SIMPLEX, 1.0, RED, thickness=2)

    elif (avg_angle < 40 and avg_angle >= 30) or (avg_angle > -40 and avg_angle <= -30):
        draw_half_circle(frame, circle_center_x, circle_center_y, ORANGE, thickness=6)
        cv2.putText(frame, "{0:0.1f}".format(avg_angle * -1), (circle_center_x - 40, circle_center_y - 120), cv2.FONT_HERSHEY_SIMPLEX, 1.0, ORANGE, thickness=2)

    else:
        draw_half_circle(frame, circle_center_x, circle_center_y, GREEN, thickness=6)
        cv2.putText(frame, "{0:0.1f}".format(avg_angle * -1), (circle_center_x - 40, circle_center_y - 120), cv2.FONT_HERSHEY_SIMPLEX, 1.0, GREEN, thickness=2)