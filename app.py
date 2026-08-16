from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required, validate_dive_form

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///logbook.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show logbook of the current user"""
    user_logbook = db.execute(
        "SELECT * FROM logbook WHERE user_id = ?", session["user_id"]
    )
    dive_sites = db.execute("SELECT divesite FROM divesites")
    return render_template(
        "index.html", user_logbook=user_logbook, dive_sites=dive_sites
    )


@app.route("/add_dive", methods=["GET", "POST"])
@login_required
def add_dive():

    if request.method == "POST":

        dive, error = validate_dive_form(request.form)

        if error:
            flash(error)
            return redirect("/add_dive")

        existing = db.execute(
            "SELECT id FROM logs WHERE user_id = ? AND number = ?",
            session["user_id"],
            dive["number"],
        )

        if existing:
            flash("Dive number already exists")
            return redirect("/add_dive")

        db.execute(
            """
            INSERT INTO logs (
                user_id,
                number,
                datetime,
                divesite_id,
                dive_time,
                max_depth,
                av_depth,
                start_pressure,
                end_pressure,
                volume,
                sac,
                water_temp,
                visibility,
                notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            session["user_id"],
            dive["number"],
            dive["datetime"],
            dive["divesite_id"],
            dive["dive_time"],
            dive["max_depth"],
            dive["av_depth"],
            dive["start_pressure"],
            dive["end_pressure"],
            dive["volume"],
            dive["sac"],
            dive["water_temp"],
            dive["visibility"],
            dive["notes"],
        )

        flash("Dive Added Successfully")
        return redirect("/")

    divesites = db.execute("SELECT id, divesite FROM divesites ORDER BY divesite")

    return render_template("add_dive.html", divesites=divesites)


@app.route("/dive")
@login_required
def dive():
    """View a Dive from Logbook"""

    dive_number = request.args.get("number")

    if not dive_number:
        flash("Invalid Dive")
        return redirect("/")

    dive = db.execute(
        "SELECT * FROM logbook WHERE number = ? AND user_id = ?",
        dive_number,
        session["user_id"],
    )

    if not dive:
        flash("Dive Not Found")
        return redirect("/")

    return render_template("dive.html", dive=dive[0])


@app.route("/update_dive", methods=["GET", "POST"])
@login_required
def update_dive():

    if request.method == "POST":

        dive_id = request.form.get("id")

        owner = db.execute(
            "SELECT id FROM logs WHERE id = ? AND user_id = ?",
            dive_id,
            session["user_id"],
        )

        if not owner:
            flash("Dive Not Found")
            return redirect("/")

        dive, error = validate_dive_form(request.form)

        if error:
            flash(error)
            return redirect(f"/update_dive?id={dive_id}")

        existing = db.execute(
            "SELECT id FROM logs WHERE number = ? AND id != ?", dive["number"], dive_id
        )

        if existing:
            flash("Dive number already exists")
            return redirect(f"/update_dive?id={dive_id}")

        db.execute(
            """
            UPDATE logs
            SET
                number = ?,
                datetime = ?,
                divesite_id = ?,
                dive_time = ?,
                max_depth = ?,
                av_depth = ?,
                start_pressure = ?,
                end_pressure = ?,
                volume = ?,
                sac = ?,
                water_temp = ?,
                visibility = ?,
                notes = ?
            WHERE id = ?
            AND user_id = ?
            """,
            dive["number"],
            dive["datetime"],
            dive["divesite_id"],
            dive["dive_time"],
            dive["max_depth"],
            dive["av_depth"],
            dive["start_pressure"],
            dive["end_pressure"],
            dive["volume"],
            dive["sac"],
            dive["water_temp"],
            dive["visibility"],
            dive["notes"],
            dive_id,
            session["user_id"],
        )

        flash("Dive Updated Successfully")
        return redirect("/")

    dive_id = request.args.get("id")

    if not dive_id:
        flash("Invalid Dive")
        return redirect("/")

    dive = db.execute(
        "SELECT * FROM logbook WHERE id = ? AND user_id = ?",
        dive_id,
        session["user_id"],
    )

    if not dive:
        flash("Dive Not Found")
        return redirect("/")

    divesites = db.execute("SELECT id, divesite FROM divesites ORDER BY divesite")

    return render_template("update_dive.html", dive=dive[0], divesites=divesites)


@app.route("/delete_dive", methods=["POST"])
@login_required
def delete_dive():
    """Delete a Dive from the Logbook"""
    dive_id = request.form.get("id")
    if not dive_id:
        flash("Invalid Dive")
        return redirect("/")
    existing = db.execute(
        "SELECT id FROM logs WHERE id = ? AND user_id = ?", dive_id, session["user_id"]
    )
    if not existing:
        flash("Dive Not Found")
        return redirect("/")
    db.execute("DELETE FROM logs WHERE id = ?", dive_id)
    flash("Dive Deleted Successfully")
    return redirect("/")


@app.route("/dive_sites", methods=["GET"])
@login_required
def dive_sites():
    """View Dive Sites"""
    dive_sites = db.execute("SELECT * FROM divesites ORDER BY divesite")
    return render_template("dive_sites.html", dive_sites=dive_sites)


@app.route("/add_dive_site", methods=["GET", "POST"])
@login_required
def add_dive_site():
    """Add a New Dive Site"""
    if request.method == "POST":
        dive_site_name = request.form.get("dive_site").strip()
        if not dive_site_name:
            flash("Dive Site name is required")
            return redirect("/add_dive_site")
        existing = db.execute(
            "SELECT id FROM divesites WHERE LOWER(divesite) = LOWER(?)", dive_site_name
        )
        if existing:
            flash("Dive Site already exists")
            return redirect("/add_dive_site")
        db.execute("INSERT INTO divesites (divesite) VALUES (?)", dive_site_name)
        flash("Dive Site Added Successfully")
        return redirect("/dive_sites")

    return render_template("add_dive_site.html")


@app.route("/delete_divesite", methods=["POST"])
@login_required
def delete_divesite():
    """Delete a Dive Site"""
    divesite_id = request.form.get("divesite_id")
    if not divesite_id:
        flash("Invalid Dive Site")
        return redirect("/dive_sites")
    existing = db.execute("SELECT id FROM divesites WHERE id = ?", divesite_id)
    if not existing:
        flash("Dive Site Not Found")
        return redirect("/dive_sites")
    dives = db.execute("SELECT 1 FROM logs WHERE divesite_id = ? LIMIT 1", divesite_id)
    if dives:
        flash("Cannot delete a dive site that has logged dives")
        return redirect("/dive_sites")
    db.execute("DELETE FROM divesites WHERE id = ?", divesite_id)
    flash("Dive Site Deleted Successfully")
    return redirect("/dive_sites")


@app.route("/stats")
@login_required
def stats():
    """Show Statistics of the User"""
    stats = db.execute("SELECT * FROM stats WHERE user_id = ?", session["user_id"])

    if not stats:
        flash("No dives logged yet")
        return redirect("/")

    return render_template("stats.html", stats=stats[0])


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            flash("Must provide username")
            return redirect("/login")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Must provide password")
            return redirect("/login")

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE LOWER(username) = LOWER(?)",
            request.form.get("username"),
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            flash("Invalid Username and/or Password")
            return redirect("/login")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["name"] = rows[0]["name"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":
        # Ensure name was submitted
        if not request.form.get("name"):
            flash("Must provide Name")
            return redirect("/register")

        # Ensure username was submitted
        if not request.form.get("username"):
            flash("Must provide Username")
            return redirect("/register")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Must provide Password")
            return redirect("/register")

        # Ensure confirmation password was submitted
        elif not request.form.get("confirmation"):
            flash("Must provide confirmation Password")
            return redirect("/register")

        if db.execute(
            "SELECT * FROM users WHERE LOWER(username) = LOWER(?)",
            request.form.get("username"),
        ):
            flash("Username already exists")
            return redirect("/register")
        elif request.form.get("password") != request.form.get("confirmation"):
            flash("Passwords do not match")
            return redirect("/register")
        else:
            db.execute(
                "INSERT INTO users (name, username, hash) VALUES (?, ?, ?);",
                request.form.get("name"),
                request.form.get("username"),
                generate_password_hash(request.form.get("password")),
            )
            rows = db.execute(
                "SELECT * FROM users WHERE LOWER(username) = LOWER(?)",
                request.form.get("username"),
            )
            session["user_id"] = rows[0]["id"]
            session["name"] = rows[0]["name"]
            return redirect("/")
    else:
        return render_template("register.html")


@app.route("/account")
@login_required
def account():
    """Update Account Username or Password"""
    rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
    username = rows[0]["username"]
    return render_template("account.html", username=username)


@app.route("/newusername", methods=["POST"])
@login_required
def newusername():
    """Update Username"""
    # Ensure username was submitted
    if not request.form.get("username"):
        flash("Must provide Username")
        return redirect("/account")

    # Ensure password was submitted
    elif not request.form.get("password"):
        flash("Must provide Password")
        return redirect("/account")

    # Query database for current username
    rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])

    # Ensure username exists and password is correct
    if not check_password_hash(rows[0]["hash"], request.form.get("password")):
        flash("Invalid Password")
        return redirect("/account")
    else:
        db.execute(
            "UPDATE users SET username = ? WHERE id = ?",
            request.form.get("username"),
            session["user_id"],
        )
        flash("Username Updated!!")
        return redirect("/")


@app.route("/newpassword", methods=["POST"])
@login_required
def newpassword():
    """Update Password"""
    # Ensure password was submitted
    if not request.form.get("password"):
        flash("Must provide Password")
        return redirect("/account")
    elif not request.form.get("newpassword"):
        flash("Must provide New Password")
        return redirect("/account")
    elif not request.form.get("confirmation"):
        flash("Must provide Confirmation Password")
        return redirect("/account")
    elif request.form.get("newpassword") != request.form.get("confirmation"):
        flash("New Password and Confirmation Password do not match")
        return redirect("/account")

    # Query database for current password
    rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])

    # Ensure password is correct
    if not check_password_hash(rows[0]["hash"], request.form.get("password")):
        flash("Invalid Password")
        return redirect("/account")
    else:
        db.execute(
            "UPDATE users SET hash = ? WHERE id = ?",
            generate_password_hash(request.form.get("newpassword")),
            session["user_id"],
        )
        flash("Password Updated!!")
        return redirect("/")


@app.route("/deleteuser", methods=["POST"])
@login_required
def deleteuser():
    """Delete Account"""
    # Ensure password was submitted
    if not request.form.get("password"):
        flash("Must provide Password")
        return redirect("/account")

    # Query database for current username
    rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])

    # Ensure username exists and password is correct
    if not check_password_hash(rows[0]["hash"], request.form.get("password")):
        flash("Invalid Password")
        return redirect("/account")
    else:
        db.execute("DELETE FROM users WHERE id = ?", session["user_id"])
        session.clear()
        flash("Account Deleted")
        return redirect("/login")
