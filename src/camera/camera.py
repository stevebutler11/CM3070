import time
from threading import get_ident, Event, Thread
from typing import Any, Generator, NoReturn, Self

from picamera2 import Picamera2
import cv2
import numpy as np

from src.detector.detector import BaseDetector


# elements of this page: https://blog.miguelgrinberg.com/post/flask-video-streaming-revisited
# were used in the following camera classes, albeit heavily modified


class CameraEvent:
    """An Event-like class that signals all active clients when a new frame is
    available.
    """

    def __init__(self):
        self._events = {}

    def wait(self) -> bool:
        """Invoked from each client's thread to wait for the next frame."""
        ident = get_ident()
        if ident not in self._events:
            # Add a new event for this client
            self._events[ident] = [Event(), time.time()]
        return self._events[ident][0].wait()

    def set(self) -> None:
        """Invoked by the camera thread when a new frame is available."""
        now = time.time()
        to_remove = []

        for ident, (event, timestamp) in self._events.items():
            if not event.is_set():
                # if this client's event is not set, then set it
                # also update the last set timestamp to now
                event.set()
                self._events[ident][1] = now

            # if the client's event is already set, it means the client
            # did not process a previous frame
            # if the event stays set for more than 5 seconds, then assume
            # the client is gone and remove it
            elif now - timestamp > 5:
                to_remove.append(ident)

        for ident in to_remove:
            del self._events[ident]

    def clear(self) -> None:
        """Invoked from each client's thread after a frame was processed."""
        ident = get_ident()
        if ident in self._events:
            self._events[ident][0].clear()


class Camera:
    # class-level attributes (shared between camera instances)
    _thread = None  # background thread that reads frames from camera
    _frame = None  # current frame is stored here by background thread
    _detector = None
    _event = CameraEvent()
    _should_stop = False
    _camera_num = 0

    def __init__(self, detector: BaseDetector, camera_num: int):
        Camera._camera_num = camera_num
        self.start(detector)

    def get_frame(self):
        """Return the current camera frame."""
        # wait for a signal from the camera thread
        Camera._event.wait()
        Camera._event.clear()

        return Camera._frame

    @staticmethod
    def frames(
        detector: BaseDetector, camera_num: int
    ) -> Generator[bytes, Any, NoReturn]:
        """"""
        with Picamera2(camera_num=camera_num) as picam:
            # setup picam
            picam.configure(
                picam.create_preview_configuration(
                    main={"format": "RGB888", "size": (640, 480)}
                )
            )

            picam.start()
            # let picam warm up
            time.sleep(1)

            try:
                while True:
                    # get the current frame as an array
                    img_arr = picam.capture_array()
                    # process frame and annotate it with detector
                    annotated_frame = detector.process_img(img_arr)
                    # yield tuple of img_arr and annotated frame as bytes
                    yield img_arr, cv2.imencode(".jpg", annotated_frame)[1].tobytes()
            finally:
                picam.stop()

    @staticmethod
    def should_switch(image: np.ndarray, std_threshold=30, noir_threshold=250) -> bool:
        """Returns whether the camera input should be switched due to percieved brightness, based on the image passed."""

        # get greyscale of img array
        grey_image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

        # Calculate the average 'brightness'
        avg_brightness = np.mean(grey_image)
        
        # if noir camera
        if Camera._camera_num == 1:
            if avg_brightness > noir_threshold:
                # it's light
                return True
        # normal camera
        else:
            if avg_brightness < std_threshold:
                # it's dark
                return True
        return False

    @staticmethod
    def switch_camera_num():
        """Helper function to switch the camera_num between 0 and 1."""
        if Camera._camera_num == 1:
            Camera._camera_num = 0
        else:
            Camera._camera_num = 1

    @classmethod
    def _run(cls: Self) -> None:
        """Camera background thread."""
        print("Starting camera thread.")

        # get the class frames iterator
        frames_iterator = cls.frames(Camera._detector, Camera._camera_num)

        # for each frame yielded
        for img_arr, frame in frames_iterator:
            # set class frame
            Camera._frame = frame
            # send signal to clients
            Camera._event.set()

            time.sleep(0)
            
            # flag has been set to stop the bg thread. deal with this
            if Camera._should_stop:
                frames_iterator.close()
                print("Stopping camera thread.")
                break
            
            # check if conditions require camera switching.
            if Camera.should_switch(img_arr):
                # switch camera num
                Camera.switch_camera_num()
                # stop generating
                frames_iterator.close()
                Camera._thread = None
                print("Switching camera.")
                # restart thread now the camera_num has been switched
                Camera.start(Camera._detector)
                return

        # reset flags
        Camera._thread = None
        Camera._should_stop = False

    @classmethod
    def start(cls: Self, detector: BaseDetector) -> None:
        """Start the background camera image processing thread."""
        Camera._detector = detector
        if Camera._thread is None or not Camera._thread.is_alive():
            # start background frame thread
            Camera._thread = Thread(target=cls._run)
            Camera._thread.start()
            # wait until first frame is available
            Camera._event.wait()

    @classmethod
    def stop(cls: Self) -> None:
        """Schedule stopping of the background camera image processing thread."""
        Camera._should_stop = True
