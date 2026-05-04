import cv2
import mediapipe as mp
import numpy as np
import serial
import time

ser = serial.Serial('COM5', 115200, timeout=1)
time.sleep(2)

mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - \
              np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180:
        angle = 360 - angle

    return angle

def calculate_shoulder_pitch(shoulder, elbow):
    # forward/back motion (y-axis)
    dx = elbow[0] - shoulder[0]
    dy = elbow[1] - shoulder[1]

    angle = np.degrees(np.arctan2(-dy, dx))
    return np.clip(angle, 0, 180)

def calculate_shoulder_roll(shoulder, elbow):
    # side lifting (x-axis)
    dx = elbow[0] - shoulder[0]
    dy = elbow[1] - shoulder[1]

    angle = np.degrees(np.arctan2(dx, -dy))
    return np.clip(angle, 0, 180)

cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(image)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    try:
        lm = results.pose_landmarks.landmark

        # LEFT
        ls = [lm[11].x, lm[11].y]
        le = [lm[13].x, lm[13].y]
        lw = [lm[15].x, lm[15].y]

        # RIGHT
        rs = [lm[12].x, lm[12].y]
        re = [lm[14].x, lm[14].y]
        rw = [lm[16].x, lm[16].y]

        # ELBOW
        l_elbow = calculate_angle(ls, le, lw)
        r_elbow = calculate_angle(rs, re, rw)

        # SHOULDER
        l_pitch = calculate_shoulder_pitch(ls, le)
        l_roll  = calculate_shoulder_roll(ls, le)

        r_pitch = calculate_shoulder_pitch(rs, re)
        r_roll  = calculate_shoulder_roll(rs, re)

        # Map to servo range
        l_pitch = int(np.clip(l_pitch, 0, 180))
        l_roll  = int(np.clip(l_roll, 0, 180))
        l_elbow = int(np.clip(l_elbow, 0, 180))

        r_pitch = int(np.clip(r_pitch, 0, 180))
        r_roll  = int(np.clip(r_roll, 0, 180))
        r_elbow = int(np.clip(r_elbow, 0, 180))

        # Send all 6 values
        data = f"{l_pitch},{l_roll},{l_elbow},{r_pitch},{r_roll},{r_elbow}\n"
        ser.write(data.encode())

        print(data.strip())

    except:
        pass

    cv2.imshow("Pose", image)

    if cv2.waitKey(10) & 0xFF == 27:
        break

cap.release()
ser.close()
cv2.destroyAllWindows()