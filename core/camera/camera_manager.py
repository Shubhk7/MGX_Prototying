"""Camera enumeration and frame capture.

This module wraps OpenCV's VideoCapture. It has no dependency on the GUI
layer — anything that reads frames from a webcam belongs here, not in gui/.
"""

import logging

import cv2
import numpy as np

logger = logging.getLogger("mgx.camera")

MAX_PROBE_INDEX = 5


def list_available_cameras() -> list[int]:
    """Probe camera indices 0..MAX_PROBE_INDEX-1 and return the ones that open.

    OpenCV has no reliable cross-backend "list all cameras" call, so we
    probe each index by attempting to open it. This is the standard
    pragmatic approach; it can be slow and may briefly trigger camera
    permission prompts on some systems.
    """
    available: list[int] = []
    for index in range(MAX_PROBE_INDEX):
        capture = cv2.VideoCapture(index, cv2.CAP_DSHOW)
        if capture.isOpened():
            available.append(index)
            capture.release()
        else:
            capture.release()
    logger.info("Camera probe found %d device(s): %s", len(available), available)
    return available


class CameraManager:
    """Manages a single open camera device and reads frames from it."""

    def __init__(self):
        self._capture: cv2.VideoCapture | None = None
        self._camera_index: int | None = None

    @property
    def is_open(self) -> bool:
        return self._capture is not None and self._capture.isOpened()

    @property
    def camera_index(self) -> int | None:
        return self._camera_index

    def open(self, index: int) -> bool:
        """Open the camera at the given index. Closes any previously open camera first."""
        self.release()
        capture = cv2.VideoCapture(index, cv2.CAP_DSHOW)
        if not capture.isOpened():
            logger.error("Failed to open camera index %d", index)
            capture.release()
            return False
        self._capture = capture
        self._camera_index = index
        logger.info("Opened camera index %d", index)
        return True

    def read_frame(self) -> np.ndarray | None:
        """Read a single frame. Returns None if the camera isn't open or the read failed."""
        if not self.is_open:
            return None
        ok, frame = self._capture.read()
        if not ok:
            logger.warning("Frame read failed on camera index %s", self._camera_index)
            return None
        return frame

    def release(self) -> None:
        """Release the current camera device, if any."""
        if self._capture is not None:
            self._capture.release()
            logger.info("Released camera index %s", self._camera_index)
        self._capture = None
        self._camera_index = None
