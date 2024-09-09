from abc import ABCMeta, abstractmethod
from ultralytics import YOLO
import numpy as np

from src.detector.detected_object import DetectedObject
from src.recorder.recorder import Recorder


class BaseDetector(metaclass=ABCMeta):
    """Base class used for all detector classes."""
    @abstractmethod
    def process_img(self, img_arr: np.ndarray) -> np.ndarray:
        """Processes an image np.ndarray argument and then returns it."""
        return


class YoloWorldDetector(BaseDetector):
    """ML detector class based on the Yolo World algorithm."""
    def __init__(
        self,
        recorder: Recorder,
        labels: list[str] = ["person"],
        buffer_frames: int = 10,
    ) -> None:
        # Load the YOLO model
        self._model = YOLO("yolov8s-world.pt").cpu()

        # set labels
        self._labels = labels
        self._model.set_classes(self._labels)

        # Dictionary to hold tracking information
        self._tracked_objects = {}

        # Recorder instance
        self._recorder = recorder

        # Tracking and recording control
        self._frames_without_tracking = 0

        # Buffer period to avoid premature stopping
        self._buffer_frames = buffer_frames

    def process_img(self, img_arr: np.ndarray) -> np.ndarray:
        # get results from model
        results = self._model.track(img_arr, imgsz=96, persist=True, verbose=False)
        # set flag
        tracking_detected = False

        # iterate results
        for result in results:
            # get dims and boxes
            height, width = result.orig_shape
            boxes = result.boxes

            # if tracking (and therefore motion)
            if boxes.is_track:
                # set flag
                tracking_detected = True

                for i, box in enumerate(boxes):
                    # create DetectedObject with box info
                    track_id = int(box.id)
                    d_o = DetectedObject(
                        label=self._labels[int(box.cls)],  # Get label using class index
                        bbox=box.xyxy[0].cpu().numpy(),  # Get bounding box coordinates
                        height=height,
                        width=width,
                    )

                    # store data
                    if track_id not in self._tracked_objects:
                        self._tracked_objects[track_id] = []
                    self._tracked_objects[track_id].append(d_o)

        if tracking_detected:
            # start recording if not already
            self._frames_without_tracking = 0
            if not self._recorder._is_recording:
                self._recorder.start_recording(img_arr.shape)
        else:
            self._frames_without_tracking += 1

        if self._recorder._is_recording:
            # write frame
            self._recorder.write_frame(img_arr)
            # if buffer limit reached for non-activity, stop recording
            if self._frames_without_tracking >= self._buffer_frames:
                self._recorder.stop_recording(self._tracked_objects)

        # annotate frame and return it
        annotated_frame = results[0].plot()
        return annotated_frame



class YoloV8NDetector(BaseDetector):
    """ML detector class based on the Yolo v8 nano algorithm."""
    def __init__(
        self,
        recorder: Recorder,
        buffer_frames: int = 10,
    ) -> None:
        # Load the YOLO model
        self._model = YOLO("yolov8n.pt").cpu()

        # Dictionary to hold tracking information
        self._tracked_objects = {}

        # Recorder instance
        self._recorder = recorder

        # Tracking and recording control
        self._frames_without_tracking = 0

        # Buffer period to avoid premature stopping
        self._buffer_frames = buffer_frames

    def process_img(self, img_arr: np.ndarray) -> np.ndarray:
        # get results from model
        results = self._model.track(img_arr, imgsz=96, persist=True, verbose=False)
        
        # set flag
        tracking_detected = False

        # iterate results
        for result in results:
            # get dims and boxes
            height, width = result.orig_shape
            boxes = result.boxes

            # if tracking (and therefore motion)
            if boxes.is_track:
                # set flag
                tracking_detected = True

                for i, box in enumerate(boxes):
                    # create DetectedObject with box info
                    track_id = int(box.id)
                    d_o = DetectedObject(
                        label=result.names[int(box.cls)],
                        bbox=box.xyxy[0].cpu().numpy(),  # Get bounding box coordinates
                        height=height,
                        width=width,
                    )

                    # store data
                    if track_id not in self._tracked_objects:
                        self._tracked_objects[track_id] = []
                    self._tracked_objects[track_id].append(d_o)

        if tracking_detected:
            # start recording if not already
            self._frames_without_tracking = 0
            if not self._recorder._is_recording:
                self._recorder.start_recording(img_arr.shape)
        else:
            self._frames_without_tracking += 1

        if self._recorder._is_recording:
            # write frame
            self._recorder.write_frame(img_arr)
            # if buffer limit reached for non-activity, stop recording
            if self._frames_without_tracking >= self._buffer_frames:
                self._recorder.stop_recording(self._tracked_objects)

        # annotate frame and return it
        annotated_frame = results[0].plot()
        return annotated_frame

