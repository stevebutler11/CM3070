from flask import Blueprint, Response, jsonify, session

utils_blueprint = Blueprint("utils", __name__)


@utils_blueprint.route("/toggletheme", methods=["POST"])
def toggle_theme() -> Response:
    """Toggle the current theme value in session"""

    # get theme from session
    current_theme = session.get("theme", "light")

    if current_theme == "light":
        new_theme = "dark"
    else:
        new_theme = "light"

    session["theme"] = new_theme
    return jsonify({"newTheme": new_theme})
