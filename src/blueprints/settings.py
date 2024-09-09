import json
import os
from typing import Dict

from flask import (
    Blueprint,
    Response,
    render_template,
    request,
    session,
    redirect,
    current_app,
)
from src.camera.camera import Camera
from src.db.models import EmailRecipient, Labels
from src.detector.coco_names import coco_names
from src.db.database import db_session
from src.detector.detector import YoloWorldDetector, YoloV8NDetector


settings_blueprint = Blueprint("settings", __name__)


def get_empty_labels_dict() -> Dict[str, bool]:
    """Get a label dict with all labels set as False"""
    return {l: False for l in coco_names}


# ml models dict
models_dict = {
    "v8world": {
        "model_name": "yolov8world",
        "dropdown_name": "Yolo V8 World (larger, more accurate)",
    },
    "v8nano": {
        "model_name": "yolov8nano",
        "dropdown_name": "Yolo V8 Nano (smaller, less accurate)",
    },
}


@settings_blueprint.route("/settings", methods=["GET", "POST"])
def settings() -> str | Response:
    """Settings page route"""

    # get theme from session
    theme = session.get("theme", "light")

    if request.method == "GET":

        # get labels from db
        labels_db = db_session.query(Labels).where(Labels.id == 1).all()
        labels_dict = labels_db[0].labelsJson

        # get email recipients from db
        recipients = db_session.query(EmailRecipient).all()

        # get model from config
        selected_model=""
        if isinstance(current_app.config["DETECTOR"], YoloWorldDetector):
            selected_model = "v8world"
        elif isinstance(current_app.config["DETECTOR"], YoloV8NDetector):
            selected_model = "v8nano"

        # render
        return render_template(
            "settings.html",
            theme=theme,
            coco_names=labels_dict,
            recipients=recipients,
            models_dict=models_dict,
            selected_model=selected_model
        )

    elif request.method == "POST":

        # if the objects form was triggered
        if "objects_form" in request.form:

            # get new label values
            new_labels = [l for l in request.form.keys()]

            # set new labels in db
            labels_dict = get_empty_labels_dict()
            for l in new_labels:
                if l in labels_dict:
                    labels_dict[l] = True
            db_session.query(Labels).where(Labels.id == 1).update(
                {"labelsJson": labels_dict}
            )
            db_session.commit()

            # stop camera bg thread so new detector can be used
            Camera.stop()

            # get rid of old detector
            del current_app.config["DETECTOR"]

            # create new detector withe the new labels
            recorder = current_app.config["RECORDER"]
            new_detector = YoloWorldDetector(labels=new_labels, recorder=recorder)
            current_app.config["DETECTOR"] = new_detector

            # restart camera background thread
            Camera.start(new_detector)

        # if the email form was triggered
        elif "emails_form" in request.form:

            # validate form
            new_email = request.form["email"]

            # add to db
            db_session.add(EmailRecipient(email_address=new_email))
            db_session.commit()

        # if the ml model change form was triggered
        elif "models_form" in request.form:

            # get the new selection from the form
            new_selection = request.form["ml_selector"]

            # create new detector with current recorder, if one matches
            new_detector = None
            recorder = current_app.config["RECORDER"]

            if new_selection == "v8nano":
                # switch to nano
                new_detector = YoloV8NDetector(recorder=recorder)

            elif new_selection == "v8world":
                # switch to world
                labels_db = db_session.query(Labels).first()  # get labels from db
                labels_dict = labels_db.labelsJson
                labels = [k for k, v in labels_dict.items() if v]

                new_detector = YoloWorldDetector(labels=labels, recorder=recorder)

            # if there is a new detector, reset the camera
            if new_detector:
                # stop camera bg thread so new detector can be used
                Camera.stop()
                # get rid of old detector
                del current_app.config["DETECTOR"]
                current_app.config["DETECTOR"] = new_detector
                # restart camera background thread
                Camera.start(new_detector)

        # redirect (to re-load)
        return redirect("/settings")

    return render_template(
        "settings.html",
        theme=theme,
        coco_names=get_empty_labels_dict(),
        recipients=[],
        models_dict=models_dict,
    )


@settings_blueprint.route("/settings/delete/<id>")
def settings_delete(id: int) -> Response:
    """Delete a specified video then reroute to saved."""

    # delete the record with the passed id
    db_session.query(EmailRecipient).where(EmailRecipient.id == id).delete()
    db_session.commit()

    # redirect to settings
    return redirect("/settings")
