"""MGX main window.

This module contains only UI wiring. Camera I/O and FPS math live in core/;
this file just displays them.
"""

import logging
import time

import cv2
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core.camera.camera_manager import CameraManager, list_available_cameras
from core.camera.fps_counter import FPSCounter
from core.vision.hand_detector import HandDetector, draw_landmarks

logger = logging.getLogger("mgx.gui")

PREVIEW_WIDTH = 640
PREVIEW_HEIGHT = 480
TIMER_INTERVAL_MS = 15  # ~66 Hz poll rate; actual FPS is capped by the camera


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MGX — Motion Gesture Execution Engine")

        self._camera_manager = CameraManager()
        self._fps_counter = FPSCounter()
        self._hand_detector: HandDetector | None = None

        self._build_ui()
        self._populate_camera_list()

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._on_timer_tick)

    def _build_ui(self) -> None:
        self._camera_combo = QComboBox()
        self._start_button = QPushButton("Start")
        self._stop_button = QPushButton("Stop")
        self._stop_button.setEnabled(False)

        self._preview_label = QLabel("No camera preview")
        self._preview_label.setFixedSize(PREVIEW_WIDTH, PREVIEW_HEIGHT)
        self._preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._preview_label.setStyleSheet("background-color: #202020; color: #888;")

        self._fps_label = QLabel("FPS: --")
        self._hand_status_label = QLabel("Hand: --")
        self._hand_count_label = QLabel("Hands: --")

        controls_layout = QHBoxLayout()
        controls_layout.addWidget(QLabel("Camera:"))
        controls_layout.addWidget(self._camera_combo)
        controls_layout.addWidget(self._start_button)
        controls_layout.addWidget(self._stop_button)
        controls_layout.addStretch()
        controls_layout.addWidget(self._hand_status_label)
        controls_layout.addWidget(self._hand_count_label)
        controls_layout.addWidget(self._fps_label)

        main_layout = QVBoxLayout()
        main_layout.addLayout(controls_layout)
        main_layout.addWidget(self._preview_label)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self._start_button.clicked.connect(self._on_start_clicked)
        self._stop_button.clicked.connect(self._on_stop_clicked)

    def _populate_camera_list(self) -> None:
        cameras = list_available_cameras()
        self._camera_combo.clear()
        if not cameras:
            self._camera_combo.addItem("No camera found")
            self._camera_combo.setEnabled(False)
            self._start_button.setEnabled(False)
            return
        for index in cameras:
            self._camera_combo.addItem(f"Camera {index}", userData=index)

    def _on_start_clicked(self) -> None:
        index = self._camera_combo.currentData()
        if index is None:
            return
        if not self._camera_manager.open(index):
            self._preview_label.setText(f"Failed to open camera {index}")
            return
        self._fps_counter.reset()
        self._hand_detector = HandDetector(max_num_hands=1)
        self._timer.start(TIMER_INTERVAL_MS)
        self._start_button.setEnabled(False)
        self._stop_button.setEnabled(True)
        self._camera_combo.setEnabled(False)

    def _on_stop_clicked(self) -> None:
        self._timer.stop()
        self._camera_manager.release()
        if self._hand_detector is not None:
            self._hand_detector.close()
            self._hand_detector = None
        self._preview_label.setText("No camera preview")
        self._fps_label.setText("FPS: --")
        self._hand_status_label.setText("Hand: --")
        self._hand_count_label.setText("Hands: --")
        self._start_button.setEnabled(True)
        self._stop_button.setEnabled(False)
        self._camera_combo.setEnabled(True)

    def _on_timer_tick(self) -> None:
        frame = self._camera_manager.read_frame()
        if frame is None:
            return

        self._fps_counter.tick(time.monotonic())
        self._fps_label.setText(f"FPS: {self._fps_counter.fps:.1f}")

        if self._hand_detector is not None:
            result = self._hand_detector.process(frame)
            draw_landmarks(frame, result)
            if result.hand_detected:
                self._hand_status_label.setText("Hand: Detected")
            else:
                self._hand_status_label.setText("Hand: Not Detected")
            self._hand_count_label.setText(f"Hands: {result.hand_count}")

        self._render_frame(frame)

    def _render_frame(self, frame) -> None:
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        height, width, channels = rgb_frame.shape
        bytes_per_line = channels * width
        qimage = QImage(
            rgb_frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888
        )
        pixmap = QPixmap.fromImage(qimage).scaled(
            PREVIEW_WIDTH,
            PREVIEW_HEIGHT,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self._preview_label.setPixmap(pixmap)

    def closeEvent(self, event) -> None:
        self._timer.stop()
        self._camera_manager.release()
        if self._hand_detector is not None:
            self._hand_detector.close()
            self._hand_detector = None
        logger.info("Main window closed, camera and hand detector released")
        super().closeEvent(event)
