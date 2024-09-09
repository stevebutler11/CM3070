from flask import Blueprint, Response, jsonify
import atexit
from src.logger.systemd_logger import SystemdLogger
from src.servos.servos import Servos

# setup systemd logger
systemd_logger = SystemdLogger()

# setup servos
servos = Servos(logger=systemd_logger, delta_angle=10)

servo_controls_blueprint = Blueprint("servos", __name__)


@servo_controls_blueprint.route("/left")
def move_left() -> Response:
    """Move servo left"""
    servos.decr_pan()
    return jsonify({"moved": "left"})


@servo_controls_blueprint.route("/right")
def move_right() -> Response:
    """Move servo right"""
    servos.incr_pan()
    return jsonify({"moved": "right"})


@servo_controls_blueprint.route("/up")
def move_up() -> Response:
    """Move servo up"""
    servos.decr_tilt()
    return jsonify({"moved": "up"})


@servo_controls_blueprint.route("/down")
def move_down() -> Response:
    """Move servo down"""
    servos.incr_tilt()
    return jsonify({"moved": "down"})


@servo_controls_blueprint.route("/home")
def home() -> Response:
    """Move the servos to the homed position"""
    servos.home()
    return jsonify({"moved": "home"})
