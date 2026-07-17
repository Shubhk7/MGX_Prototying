"""Rolling FPS calculation with no dependency on camera hardware or GUI."""

from collections import deque


class FPSCounter:
    """Computes a rolling average FPS from a stream of frame timestamps.

    This class has no knowledge of OpenCV, Qt, or any I/O — it only does
    arithmetic on timestamps — so it can be unit tested without a camera.
    """

    def __init__(self, window_size: int = 30):
        if window_size < 1:
            raise ValueError("window_size must be at least 1")
        self._window_size = window_size
        self._timestamps: deque[float] = deque(maxlen=window_size)

    def tick(self, timestamp: float) -> None:
        """Record a new frame timestamp (seconds, e.g. from time.monotonic())."""
        self._timestamps.append(timestamp)

    @property
    def fps(self) -> float:
        """Current rolling FPS, or 0.0 if not enough samples yet."""
        if len(self._timestamps) < 2:
            return 0.0
        elapsed = self._timestamps[-1] - self._timestamps[0]
        if elapsed <= 0:
            return 0.0
        frame_intervals = len(self._timestamps) - 1
        return frame_intervals / elapsed

    def reset(self) -> None:
        """Clear all recorded timestamps."""
        self._timestamps.clear()
