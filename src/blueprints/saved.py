import os
from datetime import timezone

from flask import (
    Blueprint,
    Response,
    render_template,
    session,
    request,
    redirect,
    url_for,
    current_app,
)

from src.db.models import VideoSnippet
from src.db.database import db_session

saved_blueprint = Blueprint("saved", __name__)


@saved_blueprint.route("/saved", methods=["GET"])
def saved() -> str:
    """Saved page route"""

    # get theme from session
    theme = session.get("theme", "light")

    if request.method == "GET":

        # get recordings from db
        recordings = db_session.query(VideoSnippet).order_by(VideoSnippet.created).all()
        return render_template("saved.html", theme=theme, recordings=recordings)

    return render_template("saved.html", theme=theme)


@saved_blueprint.route("/saved/player/<video_id>")
def player(video_id: int) -> str:
    """player page"""

    # get theme from session
    theme = session.get("theme", "light")

    # get recording from db
    video_db = db_session.query(VideoSnippet).where(VideoSnippet.id == video_id).first()

    # get date, time and format  it
    date = video_db.created.date()
    time = video_db.created.time().strftime("%H:%M:%S")

    return render_template(
        "player.html",
        theme=theme,
        video_title=video_db.snippetTitle,
        video_id=video_id,
        description=video_db.description,
        date=date,
        time=time,
    )


@saved_blueprint.route("/saved/player/delete/<video_id>")
def delete_recording(video_id: int) -> Response:
    """delete video"""

    # get theme from session
    theme = session.get("theme", "light")

    # get entry
    entry = db_session.query(VideoSnippet).where(VideoSnippet.id == video_id)
    vid_db = entry.first()
    snippetTitle = vid_db.snippetTitle
    thumbnailTitle = vid_db.thumbnailTitle

    try:
        # delete db entry
        entry.delete()
        db_session.commit()

        # delete file(s)
        os.remove(os.path.join(current_app.static_folder, f"recordings/{snippetTitle}"))
        os.remove(
            os.path.join(current_app.static_folder, f"recordings/{thumbnailTitle}")
        )

    except Exception as e:
        print("Error deleting video: {e}")

    # redirect to saved
    return redirect(url_for("saved.saved"))
