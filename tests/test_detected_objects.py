import pytest
import numpy as np

from src.detector.detected_object import DetectedObject


def test_instantiate():
    """Test if a DetecteObject is instantiated correctly"""
    d_o = DetectedObject(
        label="test label", bbox=np.asarray([1, 2, 3, 4]), height=128, width=256
    )

    assert d_o.label == "test label"
    assert (d_o.bbox == np.asarray([1, 2, 3, 4])).all()
    assert d_o.height == 128
    assert d_o.width == 256


def test_parse_objects():
    start = DetectedObject(
        label="person",
        bbox=np.asarray([0.0, 0.0, 100.0, 100.0]),
        height=1028.0,
        width=1028.0,
    )
    end = DetectedObject(
        label="person",
        bbox=np.asarray([900.0, 900.0, 900.0, 900.0]),
        height=1028.0,
        width=1028.0,
    )

    objects_dict = {"1": [start, end]}

    descriptions = DetectedObject.parse_objects(objects_dict)

    assert (
        descriptions
        == "person entered at top left of the screen, and exited at bottom right of the screen"
    )

def test_parse_multiple_objects():
    start_a = DetectedObject(
        label="person",
        bbox=np.asarray([0.0, 0.0, 100.0, 100.0]),
        height=1028.0,
        width=1028.0,
    )
    end_a = DetectedObject(
        label="person",
        bbox=np.asarray([800.0, 800.0, 900.0, 900.0]),
        height=1028.0,
        width=1028.0,
    )

    start_b = DetectedObject(
        label="dog",
        bbox=np.asarray([400.0, 450.0, 500.0, 550.0]),
        height=1028.0,
        width=1028.0,
    )
    end_b = DetectedObject(
        label="dog",
        bbox=np.asarray([0.0, 900.0, 100.0, 950.0]),
        height=1028.0,
        width=1028.0,
    )

    objects_dict = {
        "1": [start_a, end_a],
        "2": [start_b, end_b]
    }

    descriptions = DetectedObject.parse_objects(objects_dict)

    assert (
        descriptions
        == "person entered at top left of the screen, and exited at bottom right of the screen\ndog entered at centre centre of the screen, and exited at bottom left of the screen"
    )
