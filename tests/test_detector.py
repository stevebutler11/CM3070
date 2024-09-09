import pytest
from unittest.mock import Mock, patch
import numpy as np
from src.detector.detector import YoloWorldDetector, BaseDetector


@pytest.fixture
def yolo_mock():
    with patch("src.detector.detector.YOLO") as mock_yolo:
        yield mock_yolo


@pytest.fixture
def recorder_mock():
    return Mock()


def test_default_yolo_world_detector_init(yolo_mock, recorder_mock):
    """Test that the default YoloWorldDetector is instantiated correctly"""
    yolo_mock.return_value = Mock()

    detector = YoloWorldDetector(recorder=recorder_mock)

    assert detector._labels == ["person"]
    assert detector._recorder == recorder_mock
    assert detector._frames_without_tracking == 0
    assert detector._buffer_frames == 10

    yolo_mock.assert_called_once_with("yolov8s-world.pt")
    yolo_mock.return_value.cpu().set_classes.assert_called_once_with(detector._labels)


def test_yolo_world_detector_init(yolo_mock, recorder_mock):
    """Test that the YoloWorldDetector is instantiated correctly with different arguments supplied"""
    yolo_mock.return_value = Mock()

    detector = YoloWorldDetector(
        recorder=recorder_mock, labels=["dog", "cat"], buffer_frames=20
    )

    assert detector._labels == ["dog", "cat"]
    assert detector._recorder == recorder_mock
    assert detector._frames_without_tracking == 0
    assert detector._buffer_frames == 20

    yolo_mock.assert_called_once_with("yolov8s-world.pt")
    yolo_mock.return_value.cpu().set_classes.assert_called_once_with(detector._labels)


def test_process_img_detected(recorder_mock):
    """Test that when an image is processed, the frame is written out"""
    detector = YoloWorldDetector(recorder=recorder_mock)
    img_arr = np.zeros((480, 640, 3))

    detector.process_img(img_arr)

    assert detector._frames_without_tracking == 1
    recorder_mock.write_frame.assert_called_once_with(img_arr)


def test_process_img_stop_recording(recorder_mock):
    """Test that stop_recording is called once the buffer frame limit has been reached"""
    detector = YoloWorldDetector(labels=["person"], recorder=recorder_mock)
    img_arr = np.zeros((480, 640, 3), dtype=np.uint8)

    detector._frames_without_tracking = 10  # Simulate buffer_frames limit reached
    detector._recorder._is_recording = True

    detector.process_img(img_arr)

    recorder_mock.stop_recording.assert_called_once_with(detector._tracked_objects)
