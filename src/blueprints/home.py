import os
from typing import Any, Generator, NoReturn
from flask import Blueprint, Response, current_app, render_template, session

from src.camera.camera import Camera


home_blueprint = Blueprint("home", __name__)


def gen(camera: Camera) -> Generator[Any | bytes, Any, NoReturn]:
    """Generator func for surveillance camera streaming."""
    yield b"--frame\r\n"
    while True:
        frame = camera.get_frame()
        yield b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n--frame\r\n"


@home_blueprint.route("/")
def index() -> str:
    """Home page route"""

    # get theme from session
    theme = session.get("theme", "light")
    
    return render_template("home.html", theme=theme)


@home_blueprint.route("/video_feed")
def video_feed() -> Response:
    """Surveillance camera streaming route"""

    # get the current detector
    detector = current_app.config["DETECTOR"]

    # create a new instance of a camera with the current detector (start with std camera (0))
    camera = Camera(detector, 0)

    return Response(gen(camera), mimetype="multipart/x-mixed-replace; boundary=frame")
