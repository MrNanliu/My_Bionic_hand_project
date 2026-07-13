import sys
import traceback
import os
import pickle
import re
import time
from collections import deque
import cv2
import mediapipe as mp
import numpy as np
from PyQt5.QtCore import QThread, QTimer, Qt, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import (QApplication, QComboBox, QFileDialog, QGridLayout, QGroupBox, QHBoxLayout,
    QLabel, QMainWindow, QPushButton, QTextEdit, QVBoxLayout, QWidget)
import pyqtgraph as pg
import serial
import serial.tools.list_ports
import torch
import torch.nn as nn

def global_exception_handler(exctype, value, tb):
    print("\n=================== CRASH TRACEBACK ===================")
    traceback.print_exception(exctype, value, tb)
    print("=======================================================\n")

sys.excepthook = global_exception_handler

class EMGCNN(nn.Module):
    def __init__(self, num_classes=5):
        super(EMGCNN, self).__init__()
        self.conv1 = nn.Conv1d(6, 16, kernel_size=3, padding=1)
        self.relu = nn.ReLU()
        self.pool1 = nn.MaxPool1d(2)
        self.conv2 = nn.Conv1d(16, 32, kernel_size=3, padding=1)
        self.pool2 = nn.MaxPool1d(2)
        self.dropout = nn.Dropout(0.3)
        self.flatten = nn.Flatten()
        self.fc1 = nn.Linear(32 * 10, 64)
        self.fc2 = nn.Linear(64, num_classes)

    def forward(self, x):
        x = self.pool1(self.relu(self.conv1(x)))
        x = self.pool2(self.relu(self.conv2(x)))
        x = self.dropout(x)
        x = self.flatten(x)
        x = self.relu(self.fc1(x))
        x = self.fc2(x)
        return x

class SerialDataReceiver(QThread):
    data_received = pyqtSignal(list)
    connection_error = pyqtSignal(str)

    def __init__(self, port, baud_rate):
        super().__init__()
        self.port = port
        self.baud_rate = baud_rate
        self.serial_port = None
        self.is_running = False

    def run(self):
        try:
            self.serial_port = serial.Serial(
                self.port, self.baud_rate, timeout=1
            )
            self.is_running = True
        except Exception as e:
            self.connection_error.emit(str(e))
            return

        while self.is_running:
            if self.serial_port.in_waiting > 0:
                try:
                    line = (
                        self.serial_port.readline()
                        .decode("ascii", errors="ignore")
                        .replace("\x00", "")
                        .strip()
                    )
                    if line:
                        match = re.search(r"\[(.*?)\]", line)
                        if match:
                            vals = [
                                float(v.strip())
                                for v in match.group(1).split(",")
                                if v.strip()
                            ]
                            if len(vals) >= 12:
                                self.data_received.emit(vals[:12])
                except Exception:
                    pass

    def stop(self):
        self.is_running = False
        if self.cap:
            self.cap.release()
        try:
            if hasattr(self, 'hands') and self.hands:
                self.hands.close()
        except Exception:
            pass

class CameraThread(QThread):
    frame_ready = pyqtSignal(QImage)
    vision_state = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.is_running = False
        self.cap = None
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.state_history = deque(maxlen=7)

    def run(self):
        self.cap = cv2.VideoCapture(0)
        self.is_running = True

        while self.is_running:
            ret, frame = self.cap.read()
            if not ret:
                continue

            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb_frame)

            raw_state = "Unknown"

            if results.multi_hand_landmarks and results.multi_handedness:
                for idx, handedness in enumerate(results.multi_handedness):
                    if handedness.classification[0].label != "Right":
                        continue

                    lms = results.multi_hand_landmarks[idx]
                    self.mp_draw.draw_landmarks(
                        rgb_frame, lms, self.mp_hands.HAND_CONNECTIONS
                    )

                    p0 = np.array([lms.landmark[0].x, lms.landmark[0].y])
                    p9 = np.array([lms.landmark[9].x, lms.landmark[9].y])
                    p4 = np.array([lms.landmark[4].x, lms.landmark[4].y])
                    p8 = np.array([lms.landmark[8].x, lms.landmark[8].y])
                    p12 = np.array([lms.landmark[12].x, lms.landmark[12].y])
                    p16 = np.array([lms.landmark[16].x, lms.landmark[16].y])
                    p20 = np.array([lms.landmark[20].x, lms.landmark[20].y])

                    palm_size = np.linalg.norm(p9 - p0)

                    if palm_size > 0:
                        pinch_dist_middle = (
                            np.linalg.norm(p4 - p12) / palm_size
                        )
                        pinch_dist_ring = np.linalg.norm(p4 - p16) / palm_size
                        fist_score = (
                            np.linalg.norm(p8 - p0)
                            + np.linalg.norm(p12 - p0)
                            + np.linalg.norm(p16 - p0)
                            + np.linalg.norm(p20 - p0)
                        ) / (4 * palm_size)

                        dy = (p9[1] - p0[1]) / palm_size

                        if fist_score < 1.3:
                            raw_state = "Fist"
                        elif pinch_dist_middle < 0.35 or pinch_dist_ring < 0.35:
                            raw_state = "Pinch"
                        elif dy < -0.65:
                            raw_state = "Wrist Up"
                        elif dy > 0.65:
                            raw_state = "Wrist Down"
                        else:
                            raw_state = "Open Hand"
                    break

            self.state_history.append(raw_state)
            counts = {}
            for s in self.state_history:
                counts[s] = counts.get(s, 0) + 1
            stable_state = max(counts, key=counts.get)

            self.vision_state.emit(stable_state)

            h, w, ch = rgb_frame.shape
            bytes_line = ch * w
            q_img = QImage(
                rgb_frame.data, w, h, bytes_line, QImage.Format_RGB888
            )
            self.frame_ready.emit(q_img)

            time.sleep(0.03)

    def stop(self):
        self.is_running = False
        if self.cap:
            self.cap.release()
        self.hands.close()

class BionicHandDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.window_size = 150
        self.num_channels = 12
        self.smooth_channels = [7, 5, 1, 3, 11, 9]
        self.cnn_labels = [
            "Open Hand",
            "Fist",
            "Pinch",
            "Wrist Up",
            "Wrist Down",
        ]

        self.target_gestures = [
            "open_hand",
            "fist",
            "pinch",
            "wrist_up",
            "wrist_down",
        ]
        self.base_dataset_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "EMG_raw_datasets",
        )

        self.plot_buffers = {
            ch: deque(maxlen=self.window_size) for ch in self.smooth_channels
        }

        self.is_connected = False
        self.receiver = None
        self.camera_thread = None

        self.is_key_recording = False
        self.key_record_buffer = []

        self.is_testing = False
        self.inference_model = None
        self.model_type = None
        self.current_vision_label = "Unknown"

        pg.setConfigOptions(antialias=False, useOpenGL=False)
        self.initialise_ui()
        self.refresh_ports()
        self.start_camera()
        self.init_dataset_directories()

        self.inference_counter = 0

        self.TARGET_MEANS = np.array([6716.9, 5965.5, 6070.9, 5771.9, 5751.1, 5892.9])

        self.muscle_state_history = deque(maxlen=8)

        self.log_box.append("--- System Ready ---")
        self.log_box.append("Tips: Press 'R' to manually reset baseline.")

        self.bias_offset = np.zeros(6)
        self.vision_stabilization_buffer = deque(maxlen=100)

    def init_dataset_directories(self):
        for gesture in self.target_gestures:
            path = os.path.join(self.base_dataset_dir, gesture)
            if not os.path.exists(path):
                os.makedirs(path)

    def initialise_ui(self):
        self.setWindowTitle("Bionic Hand Control Dashboard")
        self.resize(1600, 1000)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        left_widget = QWidget()
        left_layout = QGridLayout(left_widget)
        self.plots = []
        self.curves = []

        for idx, ch_idx in enumerate(self.smooth_channels):
            plot = pg.PlotWidget(title=f"CH {ch_idx}")
            plot.setBackground("#1e1e1e")
            plot.showGrid(x=True, y=True, alpha=0.3)
            plot.enableAutoRange(axis=pg.ViewBox.YAxis)
            plot.setAutoVisible(y=True)

            curve = plot.plot(pen=pg.mkPen(color="#00ff00", width=1.5))
            self.plots.append(plot)
            self.curves.append(curve)

            left_layout.addWidget(plot, idx // 2, idx % 2)

        right_layout = QVBoxLayout()

        self.camera_label = QLabel()
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setStyleSheet(
            "background-color: #000000; border: 2px solid #555;"
        )
        self.camera_label.setMinimumSize(480, 360)

        control_layout = QGridLayout()

        self.combo_port = QComboBox()
        self.btn_refresh = QPushButton("Refresh Ports")
        self.btn_refresh.clicked.connect(self.refresh_ports)

        self.combo_baud = QComboBox()
        self.combo_baud.addItems(["9600", "115200", "256000"])
        self.combo_baud.setCurrentText("115200")

        self.btn_connect = QPushButton("Connect")
        self.btn_connect.clicked.connect(self.toggle_connection)

        self.btn_clear = QPushButton("Clear Graphs")
        self.btn_clear.clicked.connect(self.clear_graphs)

        control_layout.addWidget(QLabel("Port:"), 0, 0)
        control_layout.addWidget(self.combo_port, 0, 1)
        control_layout.addWidget(self.btn_refresh, 0, 2)

        control_layout.addWidget(QLabel("Baud:"), 1, 0)
        control_layout.addWidget(self.combo_baud, 1, 1, 1, 2)

        control_layout.addWidget(self.btn_connect, 2, 0)
        control_layout.addWidget(self.btn_clear, 2, 1, 1, 2)

        record_group = QGroupBox("Class-Specific Data Collection")
        record_layout = QGridLayout()

        self.combo_record_gesture = QComboBox()
        self.combo_record_gesture.addItems(self.target_gestures)

        self.label_record_status = QLabel("Press SPACE to trigger recording")
        self.label_record_status.setStyleSheet("font-weight: bold; color: #a83232;")
        self.label_record_status.setAlignment(Qt.AlignCenter)

        record_layout.addWidget(QLabel("Select Gesture:"), 0, 0)
        record_layout.addWidget(self.combo_record_gesture, 0, 1)
        record_layout.addWidget(self.label_record_status, 1, 0, 1, 2)
        record_group.setLayout(record_layout)

        mapping_group = QGroupBox("Robotic Hand Mapping Route")
        mapping_layout = QGridLayout()

        robotic_actions = [
            "None",
            "Power Grasp",
            "Precision Pinch",
            "Wrist Flexion",
            "Wrist Extension",
            "Rest",
        ]

        self.combo_map_fist = QComboBox()
        self.combo_map_fist.addItems(robotic_actions)
        self.combo_map_fist.setCurrentText("Power Grasp")

        self.combo_map_pinch = QComboBox()
        self.combo_map_pinch.addItems(robotic_actions)
        self.combo_map_pinch.setCurrentText("Precision Pinch")

        self.combo_map_wrist_up = QComboBox()
        self.combo_map_wrist_up.addItems(robotic_actions)
        self.combo_map_wrist_up.setCurrentText("Wrist Extension")

        self.combo_map_wrist_down = QComboBox()
        self.combo_map_wrist_down.addItems(robotic_actions)
        self.combo_map_wrist_down.setCurrentText("Wrist Flexion")

        mapping_layout.addWidget(QLabel("Fist ->"), 0, 0)
        mapping_layout.addWidget(self.combo_map_fist, 0, 1)
        mapping_layout.addWidget(QLabel("Pinch ->"), 1, 0)
        mapping_layout.addWidget(self.combo_map_pinch, 1, 1)
        mapping_layout.addWidget(QLabel("Wrist Up ->"), 2, 0)
        mapping_layout.addWidget(self.combo_map_wrist_up, 2, 1)
        mapping_layout.addWidget(QLabel("Wrist Down ->"), 3, 0)
        mapping_layout.addWidget(self.combo_map_wrist_down, 3, 1)

        mapping_group.setLayout(mapping_layout)

        action_layout = QHBoxLayout()

        self.btn_test = QPushButton("Load Model & Test")
        self.btn_test.setStyleSheet("font-weight: bold; padding: 10px;")
        self.btn_test.clicked.connect(self.toggle_live_inference)

        self.btn_eval = QPushButton("Evaluate Dataset File")
        self.btn_eval.setStyleSheet("font-weight: bold; padding: 10px;")
        self.btn_eval.clicked.connect(self.evaluate_dataset_file)

        action_layout.addWidget(self.btn_test)
        action_layout.addWidget(self.btn_eval)

        feedback_group = QGroupBox("Live Feedback")
        feedback_layout = QGridLayout()

        self.label_vision = QLabel("Vision: Unknown")
        self.label_vision.setStyleSheet(
            "color: white; font-weight: bold; background-color: #2e2e2e;"
            " padding: 5px; border: 1px solid #555;"
        )
        self.label_muscle = QLabel("Inference: Resting State")
        self.label_muscle.setStyleSheet(
            "color: white; font-weight: bold; background-color: #2e2e2e;"
            " padding: 5px; border: 1px solid #555;"
        )

        feedback_layout.addWidget(QLabel("Vision:"), 0, 0)
        feedback_layout.addWidget(self.label_vision, 0, 1)
        feedback_layout.addWidget(QLabel("Inference:"), 1, 0)
        feedback_layout.addWidget(self.label_muscle, 1, 1)

        feedback_group.setLayout(feedback_layout)

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setStyleSheet(
            "background-color: #1e1e1e; color: #00ff00; font-family: Consolas;"
        )
        self.log_box.append("System ready.")

        right_layout.addWidget(self.camera_label, 2)
        right_layout.addLayout(control_layout)
        right_layout.addWidget(record_group)
        right_layout.addWidget(mapping_group)
        right_layout.addWidget(feedback_group)
        right_layout.addLayout(action_layout)
        right_layout.addWidget(self.log_box, 2)

        main_layout.addWidget(left_widget, 2)
        main_layout.addLayout(right_layout, 1)

    def refresh_ports(self):
        self.combo_port.clear()
        ports = serial.tools.list_ports.comports()
        for p in ports:
            self.combo_port.addItem(p.device)
        self.log_box.append(f"Scanned {len(ports)} ports.")

    def toggle_connection(self):
        if not self.is_connected:
            port = self.combo_port.currentText()
            baud_text = self.combo_baud.currentText()

            if not port:
                self.log_box.append("No port selected.")
                return

            self.receiver = SerialDataReceiver(port, int(baud_text))
            self.receiver.data_received.connect(self.update_data)
            self.receiver.connection_error.connect(self.handle_error)
            self.receiver.start()

            self.is_connected = True
            self.btn_connect.setText("Disconnect")
            self.combo_port.setEnabled(False)
            self.combo_baud.setEnabled(False)
            self.log_box.append(f"Connected to {port} at {baud_text} baud.")
        else:
            if self.receiver:
                self.receiver.stop()
                self.receiver.wait()

            self.is_connected = False
            self.btn_connect.setText("Connect")
            self.combo_port.setEnabled(True)
            self.combo_baud.setEnabled(True)
            self.log_box.append("Disconnected.")

    def toggle_live_inference(self):
        if not self.is_testing:
            options = QFileDialog.Options()
            file_name, _ = QFileDialog.getOpenFileName(self, "Select Trained Model", "", "Model Files (*.pkl *.pth);;PyTorch Files (*.pth);;All Files (*)", options=options)

            if file_name:
                try:
                    model_dir = os.path.dirname(file_name)
                    base_name = os.path.basename(file_name)

                    if file_name.endswith(".pth"):
                        model = EMGCNN(num_classes=5)
                        model.load_state_dict(torch.load(file_name, map_location=torch.device("cpu")))
                        model.eval()
                        self.inference_model = model
                        self.model_type = "cnn"
                        scaler_path = os.path.join(model_dir, "scaler.pkl")
                    else:
                        with open(file_name, "rb") as f:
                            self.inference_model = pickle.load(f)
                        self.model_type = "rf"
                        scaler_path = os.path.join(model_dir, "rf_scaler.pkl")
                        if not os.path.exists(scaler_path):
                            scaler_path = os.path.join(model_dir, "scaler.pkl")

                    if os.path.exists(scaler_path):
                        with open(scaler_path, "rb") as f:
                            self.scaler = pickle.load(f)
                    else:
                        self.scaler = None

                    self.is_testing = True
                    self.btn_test.setText("Stop Testing")
                    self.log_box.append(f"{base_name} loaded.")
                except Exception as e:
                    self.log_box.append(f"Load Error: {str(e)}")
        else:
            self.is_testing = False
            self.inference_model = None
            self.scaler = None
            self.model_type = None
            self.btn_test.setText("Load Model & Test")
            self.label_muscle.setText("Inference: Resting State")
            self.log_box.append("Deactivated.")

    def evaluate_dataset_file(self):
        if self.inference_model is None:
            self.log_box.append("Error: Please load a model first using 'Load Model & Test'.")
            return

        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Select Recorded Raw Data File",
            self.base_dataset_dir,
            "Text Files (*.txt);;All Files (*)",
            options=options,
        )

        if not file_name:
            return

        try:
            data = []
            with open(file_name, "r", encoding="utf-8") as f:
                content = f.read().replace("\\n", "\n")
                for line in content.splitlines():
                    line = line.strip()
                    if line:
                        vals = [float(x) for x in line.split()]
                        if len(vals) == 6:
                            data.append(vals)

            data_arr = np.array(data)
            if len(data_arr) < 40:
                self.log_box.append("Error: Dataset file has fewer than 40 samples.")
                return

            predictions = []
            confidences = []

            for i in range(0, len(data_arr) - 40 + 1, 5):
                window = data_arr[i : i + 40].copy()
                for ch in range(6):
                    med = np.median(window[:, ch])
                    mask = np.abs(window[:, ch] - med) > 120
                    window[mask, ch] = med

                if self.model_type == "cnn":
                    win_raw = window.T
                    win_zero = win_raw - np.mean(win_raw, axis=1, keepdims=True)
                    win_flat = win_zero.reshape(1, -1)
                    if self.scaler is not None:
                        win_flat = self.scaler.transform(win_flat)
                    cnn_input = win_flat.reshape(1, 6, 40)
                    outputs = self.inference_model(torch.FloatTensor(cnn_input))
                    probs = torch.softmax(outputs, dim=1).detach().numpy()[0]
                    prediction_idx = np.argmax(probs)
                    confidence = probs[prediction_idx]
                    raw_pred = self.target_gestures[prediction_idx]
                else:
                    features = self.extract_advanced_features(window)
                    features_arr = np.array(features).reshape(1, -1)
                    if self.scaler is not None:
                        features_arr = self.scaler.transform(features_arr)
                    
                    probs = self.inference_model.predict_proba(features_arr)[0]
                    prediction_idx = np.argmax(probs)
                    confidence = probs[prediction_idx]

                    if hasattr(self.inference_model, "classes_"):
                        cls_val = self.inference_model.classes_[prediction_idx]
                        if isinstance(cls_val, (int, np.integer)):
                            raw_pred = self.target_gestures[int(cls_val)]
                        else:
                            raw_pred = str(cls_val).lower()
                    else:
                        raw_pred = self.target_gestures[prediction_idx]

                predictions.append(raw_pred)
                confidences.append(confidence)

            counts = {}
            for p in predictions:
                counts[p] = counts.get(p, 0) + 1

            total = len(predictions)
            summary_str = []
            for gesture, count in sorted(
                counts.items(), key=lambda x: x[1], reverse=True
            ):
                pct = (count / total) * 100
                display_name = gesture.replace("_", " ").title()
                summary_str.append(f"{display_name}: {pct:.1f}% ({count}/{total})")

            avg_conf = np.mean(confidences) if confidences else 0.0
            base_fname = os.path.basename(file_name)

            self.log_box.append(f"--- Evaluation Result: {base_fname} ---")
            self.log_box.append(f"Avg Confidence: {avg_conf:.2f}")
            for s in summary_str:
                self.log_box.append(f"  > {s}")

        except Exception as e:
            self.log_box.append(f"Evaluation Error: {str(e)}")

    def handle_error(self, msg):
        self.log_box.append(f"Error: {msg}")
        self.btn_connect.setText("Connect")
        self.is_connected = False
        self.combo_port.setEnabled(True)
        self.combo_baud.setEnabled(True)

    def clear_graphs(self):
        for ch in self.smooth_channels:
            self.plot_buffers[ch].clear()
        for curve in self.curves:
            curve.setData([])

    def start_camera(self):
        self.camera_thread = CameraThread()
        self.camera_thread.frame_ready.connect(self.update_feed)
        self.camera_thread.vision_state.connect(self.update_vision)
        self.camera_thread.start()

    def update_feed(self, img):
        pix = QPixmap.fromImage(img)
        scaled = pix.scaled(
            self.camera_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
        self.camera_label.setPixmap(scaled)

    def update_vision(self, state):
        self.current_vision_label = state
        self.label_vision.setText(f"Vision: {state}")

    def start_key_triggered_recording(self):
        selected_gesture = self.combo_record_gesture.currentText()
        self.log_box.append(f"Starting raw signal collection for [{selected_gesture}]...")
        self.label_record_status.setText(f"Recording [{selected_gesture}]...")
        self.label_record_status.setStyleSheet("font-weight: bold; color: #00ff00;")

        self.key_record_buffer = []
        self.is_key_recording = True

        QTimer.singleShot(2500, lambda: self.stop_key_triggered_recording(selected_gesture))

    def stop_key_triggered_recording(self, gesture):
        self.is_key_recording = False
        self.label_record_status.setText("Press SPACE to trigger recording")
        self.label_record_status.setStyleSheet("font-weight: bold; color: #a83232;")

        if len(self.key_record_buffer) < 20:
            self.log_box.append("Recording time too short, ignored.")
            return

        timestamp = dt.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{gesture}_raw_{timestamp}.txt"
        target_dir = os.path.join(self.base_dataset_dir, gesture)
        if not os.path.exists(target_dir): os.makedirs(target_dir)
        full_path = os.path.join(target_dir, filename)

        try:
            with open(full_path, "w", encoding="utf-8") as f:
                for row in self.key_record_buffer:
                    f.write(" ".join(map(str, row)) + "\n")
            self.log_box.append(f"Saved: {filename}")
        except Exception as e:
            self.log_box.append(f"Save failed: {e}")

    def extract_advanced_features(self, window):
        features = []
        for i in range(window.shape[1]):
            ch_data = window[:, i]
            rms = np.sqrt(np.mean(ch_data**2))
            mav = np.mean(np.abs(ch_data))
            wl = np.sum(np.abs(np.diff(ch_data)))
            zcr = np.sum(np.diff(np.sign(ch_data)) != 0)
            std = np.std(ch_data)
            
            features.extend([rms, mav, wl, zcr, std])
            
        return features

    def update_data(self, vals):
        raw_vals = [float(vals[i]) for i in self.smooth_channels]
        calibrated_vals = [raw_vals[i] - self.bias_offset[i] for i in range(len(self.smooth_channels))]

        for idx, val in enumerate(calibrated_vals):
            ch = self.smooth_channels[idx]
            self.plot_buffers[ch].append(val)
            self.curves[idx].setData(list(self.plot_buffers[ch]))

        self.vision_stabilization_buffer.append(self.current_vision_label)
        if len(self.vision_stabilization_buffer) >= 100:
            open_hand_count = self.vision_stabilization_buffer.count("Open Hand")
            ratio = open_hand_count / len(self.vision_stabilization_buffer)
            if ratio > 0.9:
                recent_raws = []
                for idx, ch in enumerate(self.smooth_channels):
                    recent_cal = np.array(list(self.plot_buffers[ch])[-20:])
                    recent_raw = recent_cal + self.bias_offset[idx]
                    recent_raws.append(np.median(recent_raw))
                self.perform_vision_calibration(recent_raws)
            self.vision_stabilization_buffer.clear()

        if self.is_key_recording:
            self.key_record_buffer.append(calibrated_vals)

        elif self.is_testing and self.inference_model is not None:
            self.inference_counter += 1

            if self.inference_counter >= 5:
                self.inference_counter = 0

                try:
                    if len(self.plot_buffers[self.smooth_channels[0]]) < 40:
                        return

                    temp_window = []
                    for ch in self.smooth_channels:
                        ch_data = np.array(list(self.plot_buffers[ch])[-40:])
                        
                        padded = np.pad(ch_data, (2, 2), mode='edge')
                        stacked = np.stack([padded[i:i+40] for i in range(5)])
                        filtered_ch = np.median(stacked, axis=0)
                            
                        temp_window.append(filtered_ch)

                    window_data = np.array(temp_window)

                    if self.model_type == "cnn":
                        win_zero = window_data - np.mean(window_data, axis=1, keepdims=True)
                        win_flat = win_zero.reshape(1, -1)
                        if self.scaler is not None:
                            win_flat = self.scaler.transform(win_flat)
                        cnn_input = win_flat.reshape(1, 6, 40)
                        outputs = self.inference_model(torch.FloatTensor(cnn_input))
                        probs = torch.softmax(outputs, dim=1).detach().numpy()[0]
                        prediction_idx = np.argmax(probs)
                        confidence = probs[prediction_idx]
                        raw_prediction = self.target_gestures[prediction_idx]
                    else:
                        window_data_T = window_data.T
                        features = self.extract_advanced_features(window_data_T)
                        features_arr = np.array(features).reshape(1, -1)
                        if self.scaler is not None:
                            features_arr = self.scaler.transform(features_arr)
                        probs = self.inference_model.predict_proba(features_arr)[0]
                        classes = self.inference_model.classes_
                        prediction_idx = np.argmax(probs)
                        confidence = probs[prediction_idx]
                        raw_prediction = str(classes[prediction_idx]).lower()

                    if confidence < 0.35:
                        stable_raw = "open_hand"
                    else:
                        stable_raw = raw_prediction

                    self.muscle_state_history.append(stable_raw)
                    counts = {}
                    for s in self.muscle_state_history:
                        counts[s] = counts.get(s, 0) + 1
                    smoothed_prediction = max(counts, key=counts.get)

                    display_text = smoothed_prediction.replace("_", " ").title()
                    self.label_muscle.setText(f"Inference: {display_text} ({confidence:.2f})")

                except Exception as e:
                    error_msg = f"Inference Error: {str(e)}"
                    if getattr(self, 'last_error_msg', "") != error_msg:
                        self.log_box.append(error_msg)
                        self.last_error_msg = error_msg
                        print(f"DEBUG: {error_msg}")

    def perform_vision_calibration(self, raw_vals):
        target_offset = np.array(raw_vals) - self.TARGET_MEANS
        offset_delta = np.abs(target_offset - self.bias_offset)
        max_delta = np.max(offset_delta)

        self.log_box.append(f"Checking calibration... Max delta: {max_delta:.1f}")

        alpha = 0.1
        if 15 < max_delta < 200:
            self.bias_offset = (1 - alpha) * self.bias_offset + alpha * target_offset
            self.log_box.append("Auto-calibrated! Drift corrected.")
        elif max_delta >= 200:
            self.log_box.append("Calibration ignored: Active muscle contraction detected.")
        else:
            self.log_box.append("Calibration silent: Signal is stable.")
    def manual_reset_baseline(self):
        calibrated_vals = np.array([self.plot_buffers[ch][-1] for ch in self.smooth_channels])
        raw_vals = calibrated_vals + self.bias_offset
        self.bias_offset = raw_vals - self.TARGET_MEANS
        self.clear_graphs()
        self.muscle_state_history.clear()
        self.log_box.append("Hard Reset: Baseline reset & Buffer cleared!")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            if self.is_connected and not self.is_key_recording:
                self.start_key_triggered_recording()
        elif event.key() == Qt.Key_R:
            self.manual_reset_baseline()
        else:
            super().keyPressEvent(event)
                
    def closeEvent(self, event):
        if self.is_connected and self.receiver:
            self.receiver.stop()
            self.receiver.wait()
        if self.camera_thread:
            self.camera_thread.stop()
            self.camera_thread.wait()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BionicHandDashboard()
    window.show()
    sys.exit(app.exec_())