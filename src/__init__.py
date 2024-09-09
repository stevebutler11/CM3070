import os

from flask import Flask, render_template, session
import qrcode

from .blueprints.servo_controls import servo_controls_blueprint
from .blueprints.home import home_blueprint
from .blueprints.saved import saved_blueprint
from .blueprints.settings import settings_blueprint
from .blueprints.utils import utils_blueprint
from .camera.camera import Camera
from .db.database import db_session, init_db
from .db.models import Labels
from .detector.detector import YoloWorldDetector, YoloV8NDetector
from .recorder.recorder import Recorder


def create_app():
    """creates, configures and returns the Flask app"""

    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(SECRET_KEY="dev")

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # setup db
    init_db()

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()

    # config recorder
    output_dir = os.path.join(app.static_folder, "recordings")
    recorder = Recorder(output_dir=output_dir)

    # config detector
    labels_db = db_session.query(Labels).first()  # get labels from db
    labels_dict = labels_db.labelsJson
    labels = [k for k, v in labels_dict.items() if v]
    detector = YoloWorldDetector(labels=labels, recorder=recorder)  # create detector

    # add recorder and detector to app config for access later
    app.config["RECORDER"] = recorder
    app.config["DETECTOR"] = detector

    # register blueprints to setup routes
    app.register_blueprint(home_blueprint)
    app.register_blueprint(saved_blueprint)
    app.register_blueprint(settings_blueprint)
    app.register_blueprint(servo_controls_blueprint)
    app.register_blueprint(utils_blueprint)

    # setup the page not found handler
    @app.errorhandler(404)
    def page_not_found(error):
        theme = session.get("theme", "light")
        return render_template("page_not_found.html", theme=theme), 404

    return app
