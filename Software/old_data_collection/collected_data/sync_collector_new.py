import cv2
import mediapipe as mp
import serial
import time
import csv
import threading
import queue
import math

emg_data_list = []
stop_event = threading.Event()

def read_serial_data(port, baudrate):
    ser = serial.Serial(port, baudrate, timeout=0.01)
    while not stop_event.is_set():
        if ser.in_waiting > 0:
            try:
                line = ser.readline().decode('utf-8').strip()
                if "Inner_Envelope:" in line and "Outer_Envelope:" in line:
                    parts = line.split(',')
                    inner = float(parts[0].split(':')[1])
                    outer = float(parts[1].split(':')[1])
                    emg_data_list.append((time.time(), inner, outer))
            except:
                pass
    ser.close()