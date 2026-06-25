import sys
import os
import time
import pandas as pd
import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QComboBox
from PyQt5.QtGui import QImage, QPixmap, QFont
from PyQt5.QtCore import Qt
from data_streams import SerialWorker, VisionWorker
from model_handler import ModelHandler

try:
    from aero_open_sdk.aero_hand import AeroHand
except ImportError:
    AeroHand = None

class BionicHandGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TetherIA - sEMG Control Interface")
        self.resize(1200, 950)

        self.inner_data = np.zeros(500)
        self.outer_data = np.zeros(500)

        self.gesture_map = {
            0: "Standby",
            1: "Fist",
            2: "Wrist Up",
            3: "Wrist Down",
            4: "Pinch",
            5: "Open"
        }

        self.training_active = False
        self.control_active = False
        self.gesture_sequence = [5, 4, 3, 2]
        self.current_seq_idx = 0
        self.samples_collected = 0
        self.target_samples = 10

        self.state = 'IDLE'
        self.vision_confirm_frames = 0
        self.required_confirm_frames = 5
        self.capture_start_time = 0
        self.capture_duration = 0.5

        self.current_inner_max = 0
        self.current_outer_max = 0
        self.collected_data = []

        self.window_size = 15
        self.inner_buffer = []
        self.outer_buffer = []
        self.best_features = [0.0, 0.0, 0.0, 0.0, 0.0]

        self.model_handler = None
        self.peak_triggered = False

        
        self.gesture_toggle_states = {2: False, 3: False, 4: False, 5: False}

        try:
            if AeroHand:
                self.hand = AeroHand('COM4', baudrate=921600)
            else:
                self.hand = None
        except:
            self.hand = None

        self._setup_ui()
        self._start_threads()

    def _setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        left_layout = QVBoxLayout()
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setYRange(0, 1023)
        self.inner_curve = self.plot_widget.plot(self.inner_data, pen='g', name="Inner EMG")
        self.outer_curve = self.plot_widget.plot(self.outer_data, pen='y', name="Outer EMG")
        left_layout.addWidget(self.plot_widget)

        main_layout.addLayout(left_layout, stretch=2)

        right_layout = QVBoxLayout()

        self.instruction_label = QLabel("Ready to start training.")
        self.instruction_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.instruction_label.setAlignment(Qt.AlignCenter)
        self.instruction_label.setStyleSheet("color: #0078D7; margin: 5px; padding: 5px; border: 2px solid #0078D7;")
        right_layout.addWidget(self.instruction_label)

        self.gesture_label = QLabel("Current Vision Status: Initialising...")
        self.gesture_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.gesture_label.setAlignment(Qt.AlignCenter)
        self.gesture_label.setStyleSheet("color: gray; margin: 5px;")
        right_layout.addWidget(self.gesture_label)

        self.video_label = QLabel()
        self.video_label.setMinimumSize(640, 360)
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setStyleSheet("background-color: black;")
        right_layout.addWidget(self.video_label)

        model_select_layout = QHBoxLayout()
        model_select_label = QLabel("Classifier Model:")
        model_select_label.setFont(QFont("Arial", 11, QFont.Bold))
        self.combo_model = QComboBox()
        self.combo_model.addItems(["Random Forest (RF)", "Support Vector Machine (SVM)"])
        model_select_layout.addWidget(model_select_label)
        model_select_layout.addWidget(self.combo_model)
        right_layout.addLayout(model_select_layout)

        self.mapping_container = QWidget()
        mapping_layout = QVBoxLayout(self.mapping_container)
        self.mapping_combos = {}
        
        for gid in [2, 3, 4, 5]:
            row = QHBoxLayout()
            name_label = QLabel(f"{self.gesture_map[gid]} Mapping:")
            name_label.setFont(QFont("Arial", 11))
            combo = QComboBox()
            combo.addItems(["None", "Touch Pinkie", "Fist Close", "Hand Open", "Pinch Action"])
            row.addWidget(name_label)
            row.addWidget(combo)
            mapping_layout.addLayout(row)
            self.mapping_combos[gid] = combo
            
        right_layout.addWidget(self.mapping_container)

        self.btn_train = QPushButton("Start Training")
        self.btn_train.setMinimumHeight(35)
        self.btn_train.clicked.connect(self.start_training)
        
        self.btn_calibrate = QPushButton("Calibrate")
        self.btn_calibrate.setMinimumHeight(35)
        
        self.btn_control = QPushButton("Enable Control Mode")
        self.btn_control.setMinimumHeight(35)
        self.btn_control.setStyleSheet("background-color: #E1E1E1;")
        self.btn_control.clicked.connect(self.toggle_control_mode)
        
        right_layout.addWidget(self.btn_train)
        right_layout.addWidget(self.btn_calibrate)
        right_layout.addWidget(self.btn_control)

        main_layout.addLayout(right_layout, stretch=1)

    def _start_threads(self):
        self.serial_thread = SerialWorker('COM3', 115200) 
        self.serial_thread.data_received.connect(self.update_plot)
        self.serial_thread.start()

        self.vision_thread = VisionWorker(0)
        self.vision_thread.frame_ready.connect(self.update_video)
        self.vision_thread.gesture_detected.connect(self.process_vision_state)
        self.vision_thread.start()

    def start_training(self):
        if self.training_active or self.control_active:
            return
        self.training_active = True
        self.btn_train.setEnabled(False)
        self.btn_control.setEnabled(False)
        self.combo_model.setEnabled(False)
        self.current_seq_idx = 0
        self.samples_collected = 0
        self.collected_data = []
        self.set_next_target()

    def toggle_control_mode(self):
        if self.training_active:
            return
        if not self.control_active:
            selected_mode = 'RF' if self.combo_model.currentIndex() == 0 else 'SVM'
            target_file = 'emg_gesture_model.pkl' if selected_mode == 'RF' else 'svm_emg_model.pkl'
            
            if not os.path.exists(target_file):
                self.instruction_label.setText(f"Error: {target_file} missing. Run training script first.")
                return
                
            self.model_handler = ModelHandler(mode=selected_mode)
            self.control_active = True
            self.btn_control.setText("Disable Control Mode")
            self.btn_control.setStyleSheet("background-color: #00AA00; color: white;")
            self.btn_train.setEnabled(False)
            self.combo_model.setEnabled(False)
            self.instruction_label.setText(f"Live Control Active [{selected_mode} Mode]")
        else:
            self.control_active = False
            self.btn_control.setText("Enable Control Mode")
            self.btn_control.setStyleSheet("background-color: #E1E1E1; color: black;")
            self.btn_train.setEnabled(True)
            self.combo_model.setEnabled(True)
            self.instruction_label.setText("Control Mode Deactivated.")

    def set_next_target(self):
        if self.current_seq_idx >= len(self.gesture_sequence):
            self.finish_training()
            return

        target_id = self.gesture_sequence[self.current_seq_idx]
        target_name = self.gesture_map[target_id]
        self.instruction_label.setText(f"Action required: {target_name} [{self.samples_collected}/{self.target_samples}]")
        self.state = 'WAIT_VISION'
        self.vision_confirm_frames = 0

    def process_vision_state(self, gesture_id):
        text = self.gesture_map.get(gesture_id, "Unknown")
        self.gesture_label.setText(f"Current Vision Status: {text}")
        
        if gesture_id == 0:
            self.gesture_label.setStyleSheet("color: gray; margin: 5px;")
        else:
            self.gesture_label.setStyleSheet("color: #00AA00; margin: 5px;")

        if not self.training_active:
            return

        if self.state == 'WAIT_VISION':
            target_id = self.gesture_sequence[self.current_seq_idx]
            if gesture_id == target_id:
                self.vision_confirm_frames += 1
                if self.vision_confirm_frames >= self.required_confirm_frames:
                    self.state = 'CAPTURING'
                    self.current_inner_max = 0
                    self.current_outer_max = 0
                    self.capture_start_time = time.time()
                    self.instruction_label.setText("Capturing peak... HOLD!")
            else:
                self.vision_confirm_frames = 0

        elif self.state == 'WAIT_RESET':
            if gesture_id == 5:
                self.vision_confirm_frames += 1
                if self.vision_confirm_frames >= self.required_confirm_frames:
                    self.set_next_target()
            else:
                self.vision_confirm_frames = 0

    def update_plot(self, inner_val, outer_val):
        self.inner_data[:-1] = self.inner_data[1:]
        self.inner_data[-1] = inner_val
        self.outer_data[:-1] = self.outer_data[1:]
        self.outer_data[-1] = outer_val

        self.inner_curve.setData(self.inner_data)
        self.outer_curve.setData(self.outer_data)

        self.inner_buffer.append(inner_val)
        self.outer_buffer.append(outer_val)
        
        if len(self.inner_buffer) > self.window_size:
            self.inner_buffer.pop(0)
            self.outer_buffer.pop(0)

        if self.training_active and self.state == 'CAPTURING':
            if len(self.inner_buffer) == self.window_size:
                current_inner_var = np.var(self.inner_buffer)
                current_outer_var = np.var(self.outer_buffer)
                current_ratio = inner_val / (outer_val + 1e-6)

                if inner_val > self.current_inner_max:
                    self.current_inner_max = inner_val
                    self.best_features = [inner_val, outer_val, current_ratio, current_inner_var, current_outer_var]

            if time.time() - self.capture_start_time >= self.capture_duration:
                target_id = self.gesture_sequence[self.current_seq_idx]
                
                self.collected_data.append([time.time(), target_id] + self.best_features)
                
                self.samples_collected += 1
                if self.samples_collected >= self.target_samples:
                    self.current_seq_idx += 1
                    self.samples_collected = 0
                
                self.state = 'WAIT_RESET'
                self.vision_confirm_frames = 0
                self.instruction_label.setText("Relax. Return to Open Hand.")
                self.best_features = [0.0, 0.0, 0.0, 0.0, 0.0]
                self.current_inner_max = 0

        elif self.control_active and self.model_handler:
            if len(self.inner_buffer) == self.window_size:
                current_inner_var = np.var(self.inner_buffer)
                current_outer_var = np.var(self.outer_buffer)
                current_ratio = inner_val / (outer_val + 1e-6)
                
                features = [inner_val, outer_val, current_ratio, current_inner_var, current_outer_var]
                predicted_gesture = self.model_handler.predict(features)
                
                if predicted_gesture in [2, 3, 4]:
                    if not self.peak_triggered:
                        self.peak_triggered = True
                        self.execute_mapped_action(predicted_gesture)
                        
                elif predicted_gesture == 5:
                    if self.peak_triggered:
                        self.peak_triggered = False
                        self.instruction_label.setText("EMG Predicted: Open (Trigger Lock Reset)")

    def execute_mapped_action(self, gesture_id):
        action = self.mapping_combos[gesture_id].currentText()
        
        if action == "None":
            self.instruction_label.setText(f"EMG Predicted: {self.gesture_map[gesture_id]} (No Action Mapped)")
            return
            
        self.gesture_toggle_states[gesture_id] = not self.gesture_toggle_states[gesture_id]
        current_state = self.gesture_toggle_states[gesture_id]
        
        self.instruction_label.setText(f"Triggered: {self.gesture_map[gesture_id]} -> {action} ({current_state})")
        
        if not self.hand:
            return
            
        if action == "Touch Pinkie":
            if current_state:
                self.hand.set_joint_positions([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0])
            else:
                self.hand.set_joint_positions([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        elif action == "Fist Close":
            if current_state:
                self.hand.set_joint_positions([0.0, 1.0, 0.0, 1.0, 1.0, 1.0, 1.0])
            else:
                self.hand.set_joint_positions([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        elif action == "Hand Open":
            self.hand.set_joint_positions([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        elif action == "Pinch Action":
            if current_state:
                self.hand.set_joint_positions([0.0, 0.5, 0.0, 0.0, 0.5, 0.0, 0.0])
            else:
                self.hand.set_joint_positions([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])

    def finish_training(self):
        self.training_active = False
        self.state = 'IDLE'
        self.btn_train.setEnabled(True)
        self.btn_control.setEnabled(True)
        self.combo_model.setEnabled(True)
        
        df = pd.DataFrame(self.collected_data, columns=['Timestamp', 'Label', 'Inner_Env', 'Outer_Env', 'Ratio', 'Inner_Var', 'Outer_Var'])
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        target_dir = os.path.join(current_dir, 'sEMG_raw_datasets')
        os.makedirs(target_dir, exist_ok=True)
        
        filename = os.path.join(target_dir, f"il_data_{int(time.time())}_labelled.csv")
        df.to_csv(filename, index=False)
        self.instruction_label.setText(f"Dataset saved. Run Random_forest.py or SVM.py to update models.")

    def update_video(self, frame):
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        q_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self.video_label.setPixmap(QPixmap.fromImage(q_img).scaled(
            self.video_label.width(), self.video_label.height(), Qt.KeepAspectRatio))

    def closeEvent(self, event):
        self.serial_thread.stop()
        self.vision_thread.stop()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BionicHandGUI()
    window.show()
    sys.exit(app.exec_())