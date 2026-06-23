import sys
import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt
from workers import SerialWorker, VisionWorker

class BionicHandGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TetherIA - sEMG Control Interface")
        self.resize(1200, 800)

        self.inner_data = np.zeros(500)
        self.outer_data = np.zeros(500)

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
        self.video_label = QLabel()
        self.video_label.setMinimumSize(640, 480)
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setStyleSheet("background-color: black;")
        right_layout.addWidget(self.video_label)

        self.btn_train = QPushButton("Start Training")
        self.btn_calibrate = QPushButton("Calibrate")
        right_layout.addWidget(self.btn_train)
        right_layout.addWidget(self.btn_calibrate)

        main_layout.addLayout(right_layout, stretch=1)

    def _start_threads(self):
        self.serial_thread = SerialWorker('COM5', 115200)
        self.serial_thread.data_received.connect(self.update_plot)
        self.serial_thread.start()

        self.vision_thread = VisionWorker(0)
        self.vision_thread.frame_ready.connect(self.update_video)
        self.vision_thread.start()

    def update_plot(self, inner_val, outer_val):
        self.inner_data[:-1] = self.inner_data[1:]
        self.inner_data[-1] = inner_val
        self.outer_data[:-1] = self.outer_data[1:]
        self.outer_data[-1] = outer_val

        self.inner_curve.setData(self.inner_data)
        self.outer_curve.setData(self.outer_data)

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