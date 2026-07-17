"""Hand landmark detection using MediaPipe's Tasks API.

This module owns all MediaPipe usage. GUI code calls into HandDetector and
draw_landmarks() but never imports mediapipe directly.

Requires a hand_landmarker.task model file at assets/models/hand_landmarker.task
(see README/setup instructions — not fetched at runtime by this code).
"""

import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks import python as mp_tasks
from mediapipe.tasks.python import vision as mp_vision

logger = logging.getLogger("mgx.vision")

_MODEL_PATH = (
    Path(__file__).resolve().parent.parent.parent / "assets" / "models" / "hand_landmarker.task"
)

# Standard MediaPipe hand topology: which of the 21 landmarks connect to which.
# This is fixed skeletal structure, not something the Tasks API migration changes.
_HAND_CONNECTIONS = (
    (0, 1), (1, 2), (2, 3), (3, 4),  # thumb
    (0, 5), (5, 6), (6, 7), (7, 8),  # index
    (5, 9), (9, 10), (10, 11), (11, 12),  # middle
    (9, 13), (13, 14), (14, 15), (15, 16),  # ring
    (13, 17), (17, 18), (18, 19), (19, 20),  # pinky
    (0, 17),  # palm base
)

_LANDMARK_COLOR = (0, 0, 255)  # red, BGR
_CONNECTION_COLOR = (0, 200, 0)  # green, BGR
_LANDMARK_RADIUS = 4
_CONNECTION_THICKNESS = 2


@dataclass
class HandDetectionResult:
    """Result of processing a single frame.

    landmarks: one entry per detected hand, each a list of 21 (x, y, z)
    normalized coordinates (0.0-1.0 relative to frame width/height).
    """

    landmarks: list[list[tuple[float, float, float]]] = field(default_factory=list)
    raw_results: Any = None

    @property
    def hand_count(self) -> int:
        return len(self.landmarks)

    @property
    def hand_detected(self) -> bool:
        return self.hand_count > 0


class HandDetector:
    """Wraps MediaPipe's HandLandmarker (Tasks API) for hand landmark detection.

    Uses VIDEO running mode: synchronous, one call per frame with a
    monotonically increasing timestamp, matching our existing per-frame
    polling loop in the GUI.
    """

    def __init__(
        self,
        max_num_hands: int = 1,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
    ):
        if not _MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Hand landmarker model not found at {_MODEL_PATH}. "
                "Download hand_landmarker.task from MediaPipe's model repository "
                "and place it at this path (see README setup instructions)."
            )

        options = mp_vision.HandLandmarkerOptions(
            base_options=mp_tasks.BaseOptions(model_asset_path=str(_MODEL_PATH)),
            running_mode=mp_vision.RunningMode.VIDEO,
            num_hands=max_num_hands,
            min_hand_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )
        self._landmarker = mp_vision.HandLandmarker.create_from_options(options)
        self._start_time = time.monotonic()
        logger.info("HandDetector initialized (max_num_hands=%d)", max_num_hands)

    def process(self, bgr_frame: np.ndarray) -> HandDetectionResult:
        """Detect hand landmarks in a BGR frame.

        Converts to RGB internally (MediaPipe requires RGB input) and wraps
        it in an mp.Image, as required by the Tasks API.
        """
        rgb_frame = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        timestamp_ms = int((time.monotonic() - self._start_time) * 1000)

        results = self._landmarker.detect_for_video(mp_image, timestamp_ms)

        landmarks: list[list[tuple[float, float, float]]] = []
        if results.hand_landmarks:
            for hand in results.hand_landmarks:
                landmarks.append([(lm.x, lm.y, lm.z) for lm in hand])

        return HandDetectionResult(landmarks=landmarks, raw_results=results)

    def close(self) -> None:
        self._landmarker.close()
        logger.info("HandDetector closed")


def draw_landmarks(bgr_frame: np.ndarray, result: HandDetectionResult) -> None:
    """Draw all landmarks and hand connections onto bgr_frame in place.

    Manual OpenCV drawing since the Tasks API has no drawing_utils equivalent.
    Uses result.landmarks (normalized coordinates), not raw_results, so this
    function has no dependency on the underlying MediaPipe result type.
    """
    if not result.landmarks:
        return

    height, width = bgr_frame.shape[:2]

    for hand in result.landmarks:
        points = [(int(x * width), int(y * height)) for x, y, _ in hand]

        for start_idx, end_idx in _HAND_CONNECTIONS:
            cv2.line(bgr_frame, points[start_idx], points[end_idx], _CONNECTION_COLOR, _CONNECTION_THICKNESS)

        for point in points:
            cv2.circle(bgr_frame, point, _LANDMARK_RADIUS, _LANDMARK_COLOR, cv2.FILLED)
