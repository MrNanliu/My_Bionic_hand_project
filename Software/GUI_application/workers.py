import cv2
import serial
import time
import numpy as np
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
                        line = self.ser.readline().decode('utf-8').strip()
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

    def __init__(self, camera_index=0):
        super().__init__()
        self.camera_index = camera_index
        self.is_running = True
        self.cap = None

    def run(self):
        self.cap = cv2.VideoCapture(self.camera_index)
        while self.is_running:
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB)
                self.frame_ready.emit(frame)
            time.sleep(0.03)

        if self.cap:
            self.cap.release()

    def stop(self):
        self.is_running = False
        self.wait()