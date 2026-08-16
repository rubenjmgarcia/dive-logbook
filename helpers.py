from flask import redirect, session, request
from functools import wraps


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function

def validate_dive_form(form):
    """Validate form data and return a dive dictionary"""

    number = request.form.get("number")
    datetime = request.form.get("datetime")
    divesite_id = request.form.get("divesite_id")
    dive_time = request.form.get("dive_time")
    max_depth = request.form.get("max_depth")

    if not number:
        return None, "Dive number is required"

    if not datetime:
        return None, "Date and time is required"

    if not divesite_id:
        return None, "Dive site is required"

    if not dive_time:
        return None, "Dive time is required"

    if not max_depth:
        return None, "Maximum depth is required"

    datetime = datetime.replace("T", " ")

    av_depth = request.form.get("av_depth") or None
    start_pressure = request.form.get("start_pressure") or None
    end_pressure = request.form.get("end_pressure") or None
    volume = request.form.get("volume") or 12
    water_temp = request.form.get("water_temp") or None
    visibility = request.form.get("visibility") or None
    notes = request.form.get("notes") or None

    try:
        dive_time = int(dive_time)
        max_depth = float(max_depth)
        volume = float(volume)

        if av_depth:
            av_depth = float(av_depth)

        if start_pressure:
            start_pressure = int(start_pressure)

        if end_pressure:
            end_pressure = int(end_pressure)

        if water_temp:
            water_temp = int(water_temp)

        if visibility:
            visibility = int(visibility)

    except ValueError:
        return None, "Invalid numeric value"

    if av_depth is not None and av_depth >= max_depth:
        return None, "Average depth must be less than maximum depth"

    if (
        start_pressure is not None
        and end_pressure is not None
        and end_pressure > start_pressure
    ):
        return None, "End pressure cannot exceed start pressure"

    sac = None

    if (
        start_pressure is not None
        and end_pressure is not None
        and av_depth is not None
    ):
        sac = round(
            ((start_pressure - end_pressure) * volume)
            / ((av_depth / 10 + 1) * dive_time),
            2,
        )

    dive = {
        "number": number,
        "datetime": datetime,
        "divesite_id": divesite_id,
        "dive_time": dive_time,
        "max_depth": max_depth,
        "av_depth": av_depth,
        "start_pressure": start_pressure,
        "end_pressure": end_pressure,
        "volume": volume,
        "sac": sac,
        "water_temp": water_temp,
        "visibility": visibility,
        "notes": notes,
    }

    return dive, None
