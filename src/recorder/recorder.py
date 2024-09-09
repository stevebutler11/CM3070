import datetime
import time
import ffmpeg
import os
import numpy as np
import numpy.typing as npt
from typing import Dict

from src.db.database import db_session
from src.db.models import VideoSnippet, EmailRecipient
from src.detector.detected_object import DetectedObject
from src.notification.notification import Notification


class Recorder:
    """Recording class for handling recording & processing of surveillance cameras."""

    def __init__(self, output_dir: str, max_duration: int = 20, fps: int = 15) -> None:
        self._output_dir = output_dir
        self._max_duration = max_duration  # Max duration in seconds
        self._fps = fps
        self._is_recording = False
        self._process = None
        self._start_time = None
        # file names
        self._recording_title = None
        self._recording_video_filename = None
        self._recording_thumbnail_filename = None

    def start_recording(self, frame_shape) -> None:
        """Starts the recording process with FFmpeg."""

        # set filename state
        self._recording_title = f'{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}'
        self._recording_video_filename = (
            f"{self._output_dir}/{self._recording_title}.mp4"
        )
        self._recording_thumbnail_filename = (
            f"{self._output_dir}/{self._recording_title}.jpg"
        )

        try:
            # begin piping frames into the output file
            self._process = (
                ffmpeg.input(
                    "pipe:0",
                    format="rawvideo",
                    pix_fmt="bgr24",
                    s=f"{frame_shape[1]}x{frame_shape[0]}",
                    framerate=self._fps,
                )
                .output(
                    self._recording_video_filename,
                    pix_fmt="yuv420p",
                    vcodec="libx264",
                )
                .overwrite_output()
                .run_async(pipe_stdin=True)
            )
            
            # set flags and notify
            self._is_recording = True
            self._start_time = time.time()  # Record the start time
            print(f"Started recording: {self._recording_title}.mp4")

        except Exception as e:
            # reset flags and notify
            print(f"Failed to start recording: {e}")
            self._is_recording = False
            self._recording_title = None
            self._recording_video_filename = None
            self._recording_thumbnail_filename = None

    def stop_recording(
        self,
        tracked_objects: Dict[int, DetectedObject] | None,
        should_save: bool = True,
    ) -> None:
        """Stops the recording process and finalizes the video file."""

        if self._process:
            try:
                self._process.stdin.close()
                self._process.wait()
                print("Stopped recording.")


                if should_save:
                    # if there are tracked objects, try parse descriptions of what they are
                    descriptions = None
                    if tracked_objects:
                        descriptions = DetectedObject.parse_objects(tracked_objects)
                        self.add_metadata(descriptions)
                    
                    # create a thumbnail for the video
                    self.generate_thumbnail()

                    # save the data (and descriptions)
                    self.save_data(descriptions)

            except Exception as e:
                print(f"Failed to stop recording: {e}")
            finally:
                self._process = None

        # reset flags
        self._is_recording = False
        self._start_time = None
        self._recording_title = None
        self._recording_video_filename = None
        self._recording_thumbnail_filename = None

    def write_frame(self, img_arr: np.ndarray) -> None:
        """Writes a frame to the recording if recording is active."""
        if not self._is_recording or self._process is None:
            return

        try:
            elapsed_time = time.time() - self._start_time
            if elapsed_time >= self._max_duration:
                print("Max recording duration reached.")
                self.stop_recording()
            else:
                self._process.stdin.write(img_arr.tobytes())

        # shouldn't happen but just in case
        except BrokenPipeError:
            print("Broken pipe: The FFmpeg process terminated unexpectedly.")
            self.stop_recording(should_save=False)

        except Exception as e:
            print(f"Error writing frame: {e}")
            self.stop_recording(should_save=False)

    def generate_thumbnail(self) -> None:
        """Generate a thumbnail for the recording"""
        (
            ffmpeg.input(self._recording_video_filename, ss=1)
            .filter("scale", 320, -1)
            .output(self._recording_thumbnail_filename, vframes=1)
            .run()
        )

    def add_metadata(self, metadata: str) -> None:
        """Adds metadata to the recorded video. The way FFMPEG works, you cannot update a file's metadata.
        Also, the metadata is not known until the streaming is complete. This means the file must be rewritten.
        """
        try:
            # create temporary file name
            temp_file = f"{self._output_dir}/temp.mp4"

            if os.path.isfile(self._recording_video_filename):
                (
                    # add metadata to video and output to temp file
                    ffmpeg.input(self._recording_video_filename)
                    .output(
                        temp_file,
                        pix_fmt="yuv420p",
                        vcodec="libx264",
                        # below idea taken from https://github.com/kkroening/ffmpeg-python/issues/112#issuecomment-473682038
                        # as ffmpeg-python cannot handle more than one metadata tag currently
                        **{
                            "metadata:g:0": "title=Movement Detected!",
                            "metadata:g:1": f"comment={metadata}",
                        },
                    )
                    .overwrite_output()
                    .run()
                )

                # Replace the original file with the new one with metadata
                os.replace(temp_file, self._recording_video_filename)
                print(f"Added metadata to video: {self._recording_title}.mp4")
            else:
                print(f"{self._recording_title}.mp4 file does not exist")

        except Exception as e:
            print(f"Failed to add metadata to video: {e}")

    def save_data(self, descriptions: str | None) -> None:
        """Save the video and thumbnail to db, and notify users."""
        db_session.add(
            VideoSnippet(
                snippet_title=f"{self._recording_title}.mp4",
                thumbnail_title=f"{self._recording_title}.jpg",
                description=descriptions,
            )
        ),
        db_session.commit()

        body_text = f"Movement was detected by the surveillance camera! \n\nA recording was made. \nThis can be viewed on the dashboard, video {self._recording_title}.mp4"

        if descriptions:
            body_text += f"\n\nThe video features:\n\n{descriptions}"

        Notification.send_emails(
            user=os.environ["SB_MAIL_USERNAME"],
            pwd=os.environ["SB_MAIL_PASSWORD"],
            emails=[r.emailAddress for r in db_session.query(EmailRecipient).all()],
            subject="Movement Detected",
            body=body_text,
        )
