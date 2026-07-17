import pytest

from core.camera.fps_counter import FPSCounter


def test_fps_returns_zero_with_no_samples():
    counter = FPSCounter()
    assert counter.fps == 0.0


def test_fps_returns_zero_with_one_sample():
    counter = FPSCounter()
    counter.tick(0.0)
    assert counter.fps == 0.0


def test_fps_calculates_correctly_for_steady_rate():
    counter = FPSCounter(window_size=10)
    # 10 frames, one every 1/30 second -> ~30 fps
    for i in range(10):
        counter.tick(i * (1 / 30))
    assert counter.fps == pytest.approx(30.0, rel=1e-3)


def test_fps_window_respects_max_size():
    counter = FPSCounter(window_size=3)
    for i in range(10):
        counter.tick(float(i))
    # Only the last 3 timestamps should be kept: 7, 8, 9 -> 2 intervals over 2s = 1 fps
    assert counter.fps == pytest.approx(1.0, rel=1e-3)


def test_reset_clears_samples():
    counter = FPSCounter()
    counter.tick(0.0)
    counter.tick(1.0)
    counter.reset()
    assert counter.fps == 0.0


def test_invalid_window_size_raises():
    with pytest.raises(ValueError):
        FPSCounter(window_size=0)
