import cv2
import mediapipe as mp
import math
import serial
import csv
import time
import os

SERIAL_PORT = 'COM5'  
BAUD_RATE = 115200

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

SAVE_PATH = os.path.join(SCRIPT_DIR, "raw_datasets")

if not os.path.exists(SAVE_PATH):
    os.makedirs(SAVE_PATH)

FILENAME = os.path.join(SAVE_PATH, f"il_data_{int(time.time())}.csv")

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
    print(f"Serial port {SERIAL_PORT} connected.")
except serial.SerialException:
    print("Failed to connect. Ensure Arduino Serial Monitor is closed.")
    exit()

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5)
cap = cv2.VideoCapture(0)

f = open(FILENAME, mode='w', newline='')
writer = csv.writer(f)
writer.writerow(['Timestamp', 'Inner_Env', 'Outer_Env', 'Index_Dist', 'Mid_Dist', 'Ring_Dist', 'Pinky_Dist'])

print(f"Data will be saved to: {FILENAME}")
print("Recording started. Press 'q' to stop.")

try:
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            break

        image = cv2.flip(image, 1)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = hands.process(image_rgb)

        emg_inner = 0.0
        emg_outer = 0.0
        
        if ser.in_waiting > 0:
            try:
                line = ser.readline().decode('utf-8').strip()
                if "Inner_Envelope:" in line and "Outer_Envelope:" in line:
                    parts = line.split(',')
                    emg_inner = float(parts[0].split(':')[1])
                    emg_outer = float(parts[1].split(':')[1])
            except (ValueError, IndexError, UnicodeDecodeError):
                pass 

        distances = [0.0, 0.0, 0.0, 0.0]
        if results.multi_hand_landmarks and results.multi_handedness:
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                if handedness.classification[0].label == "Right":
                    lm = hand_landmarks.landmark
                    t_tip = lm[4] 

                    distances = [
                        math.hypot(lm[8].x - t_tip.x, lm[8].y - t_tip.y),
                        math.hypot(lm[12].x - t_tip.x, lm[12].y - t_tip.y),
                        math.hypot(lm[16].x - t_tip.x, lm[16].y - t_tip.y),
                        math.hypot(lm[20].x - t_tip.x, lm[20].y - t_tip.y)
                    ]

                    mp.solutions.drawing_utils.draw_landmarks(
                        image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        current_time = time.time()
        writer.writerow([current_time, emg_inner, emg_outer] + distances)

        cv2.putText(image, f"Inner: {emg_inner:.1f}", (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(image, f"Outer: {emg_outer:.1f}", (30, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 165, 255), 2)
        cv2.putText(image, f"Index Dist: {distances[0]:.2f}", (30, 150),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        cv2.putText(image, f"Mid Dist: {distances[1]:.2f}", (30, 200),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        cv2.imshow('TetherIA - Synchronised Data Collector', image)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    f.close()
    cap.release()
    ser.close()
    cv2.destroyAllWindows()
    print(f"Recording finished. Data saved to {FILENAME}")