import pytest
from unittest.mock import MagicMock, patch
import cv2
import numpy as np
from src.camera.camera import Camera, CameraEvent


@pytest.fixture
def mock_picamera():
    """Fixture to mock Picamera2."""
    with patch("src.camera.camera.Picamera2") as mock_picamera2:
        mock_picamera_instance = MagicMock()
        mock_picamera2.return_value = mock_picamera_instance
        yield mock_picamera_instance


@pytest.fixture
def mock_detector():
    """Fixture to mock the BaseDetector."""
    mock_detector = MagicMock()
    mock_detector.process_img.side_effect = (
        lambda img: img
    )  # return same image for testing purposes
    yield mock_detector


def test_get_frame(mock_detector):
    """Test that `get_frame` returns the current frame after the event is set."""
    # Mock frame and event behavior
    Camera._frame = b"mock_frame_data"
    Camera._event = MagicMock()

    # make sure wait() returns True, and clear() is called
    Camera._event.wait.return_value = True

    # init camera and call get_frame
    cam = Camera(mock_detector, camera_num=0)
    frame = cam.get_frame()

    # check wait and clear were called
    Camera._event.wait.assert_called()
    Camera._event.clear.assert_called()

    # Check that the returned frame is the mocked frame
    assert frame == b"mock_frame_data"

    # thread keeps running unless you stop it
    Camera.stop()
