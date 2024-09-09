from dataclasses import dataclass
from typing import Dict, Literal, Self
import numpy as np


@dataclass
class DetectedObject:
    label: str
    bbox: np.ndarray
    height: int
    width: int

    @staticmethod
    def parse_objects(objects_detected: Dict[int, list[Self]]) -> str:
        """Given a dict of tracking data, this method parses what happens in the video."""

        # init the return list
        descriptions = []

        # iterate objects in dict
        for k, v in objects_detected.items():

            # get image width and height
            width = v[0].width
            height = v[0].height

            # calculate the normalised centroid at the point the detected object enters the screen
            enter_bbox = v[0].bbox
            enter_centroid_ratio = (
                ((enter_bbox[2] + enter_bbox[0]) / 2) / width,
                ((enter_bbox[3] + enter_bbox[1]) / 2) / height,
            )

            # calculate the normalised centroid at the point the detected object exits the screen
            exit_bbox = v[-1].bbox
            exit_centroid_ratio = (
                ((exit_bbox[2] + exit_bbox[0]) / 2) / width,
                ((exit_bbox[3] + exit_bbox[1]) / 2) / height,
            )

            # get the detected regions of the entry point
            enter_x_pos, enter_y_pos = DetectedObject._parse_position_to_regions(
                enter_centroid_ratio
            )
            # get the detected regions of the exit point
            exit_x_pos, exit_y_pos = DetectedObject._parse_position_to_regions(
                exit_centroid_ratio
            )

            # format and add the description to the return descriptions
            descriptions.append(
                f"""{v[0].label} entered at {enter_y_pos} {enter_x_pos} of the screen, and exited at {exit_y_pos} {exit_x_pos} of the screen"""
            )

        return "\n".join(descriptions)

    @classmethod
    def _parse_position_to_regions(
        cls, position: tuple[float, float]
    ) -> tuple[Literal["left", "centre", "right"], Literal["top", "centre", "bottom"]]:
        """Split the image into a 3x3 grid and return a tuple of natural language descriptions of the postion given."""
        
        # pull normalised x and y floats from position tuple
        x, y = position

        # deals with x axis
        if x < 0.34:
            x_pos = "left"
        elif x < 0.67:
            x_pos = "centre"
        else:
            x_pos = "right"

        # deals with y axis
        if y < 0.34:
            y_pos = "top"
        elif y < 0.67:
            y_pos = "centre"
        else:
            y_pos = "bottom"

        # returns tuple of regions
        return (x_pos, y_pos)
