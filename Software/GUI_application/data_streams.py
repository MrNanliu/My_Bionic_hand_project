import cv2
import serial
import time
import math
import numpy as np
import mediapipe as mp
from PyQt5.QtCore import QThread, pyqtSignal

class SerialWorker(QThread):
    data_received = pyqtSignal(float, float)

    def __init__(self, port, baudrate):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.is_running = True
        self.ser = None

    def run(self):
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=0.01)
            while self.is_running:
                if self.ser.in_waiting > 0:
                    try:
                        line = self.ser.readline().decode('utf-8', errors='ignore').strip()
                        if "Inner_Envelope:" in line and "Outer_Envelope:" in line:
                            parts = line.split(',')
                            inner = float(parts[0].split(':')[1])
                            outer = float(parts[1].split(':')[1])
                            self.data_received.emit(inner, outer)
                    except:
                        pass
        except:
            pass
        finally:
            if self.ser and self.ser.is_open:
                self.ser.close()

    def stop(self):
        self.is_running = False
        self.wait()

class VisionWorker(QThread):
    frame_ready = pyqtSignal(np.ndarray)
    gesture_detected = pyqtSignal(int)

    def __init__(self, camera_index=0):
        super().__init__()
        self.camera_index = camera_index
        self.is_running = True
        self.cap = None
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils

    def run(self):
        self.cap = cv2.VideoCapture(self.camera_index)
        while self.is_running:
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.flip(frame, 1)
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = self.hands.process(rgb_frame)
                
                current_gesture = 0
                
                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        self.mp_draw.draw_landmarks(rgb_frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                        current_gesture = self._classify_gesture(hand_landmarks.landmark)
                
                self.gesture_detected.emit(current_gesture)
                self.frame_ready.emit(rgb_frame)
            
            time.sleep(0.03)

        if self.cap:
            self.cap.release()

    def _classify_gesture(self, lm):
        thumb_tip = lm[4]
        mid_tip = lm[12]
        wrist = lm[0]

        pinch_dist = math.hypot(thumb_tip.x - mid_tip.x, thumb_tip.y - mid_tip.y)

        tips = [8, 12, 16, 20]
        mcps = [5, 9, 13, 17]

        fingers_folded = 0
        for tip, mcp in zip(tips, mcps):
            dist_tip = math.hypot(lm[tip].x - wrist.x, lm[tip].y - wrist.y)
            dist_mcp = math.hypot(lm[mcp].x - wrist.x, lm[mcp].y - wrist.y)
            if dist_tip < dist_mcp:
                fingers_folded += 1

        if pinch_dist < 0.05:
            return 4
        elif fingers_folded >= 3:
            return 1
        elif fingers_folded <= 1:
            y_diff = wrist.y - mid_tip.y
            if y_diff > 0.25:
                return 2
            elif y_diff < -0.25:
                return 3
            else:
                return 5
        
        return 0

    def stop(self):
        self.is_running = False
        self.wait()