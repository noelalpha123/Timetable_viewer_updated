import os

from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, url_for
from supabase import Client, create_client

load_dotenv()

app = Flask(__name__)

# Supabase credentials
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Admin password
ADMIN_PASSWORD = "1234"

# Default timetable
DEFAULT_TIMETABLE = {
    "Monday": [
        {
            "time": "9:00 AM",
            "subject": "Math",
            "venue": "Room 101",
            "faculty": "Dr. Salvin Saju",
        },
        {
            "time": "11:00 AM",
            "subject": "Physics",
            "venue": "Room 102",
            "faculty": "Dr. Noel G.J",
        },
        {
            "time": "1:00 PM",
            "subject": "History",
            "venue": "Room 103",
            "faculty": "Ms. Milna",
        },
    ],
    "Tuesday": [
        {
            "time": "10:00 AM",
            "subject": "Chemistry",
            "venue": "Room 104",
            "faculty": "Dr. Salvin Saju",
        },
        {
            "time": "12:00 PM",
            "subject": "Biology",
            "venue": "Room 105",
            "faculty": "Dr. Noel G.J",
        },
        {
            "time": "2:00 PM",
            "subject": "English",
            "venue": "Room 106",
            "faculty": "Ms. Milna",
        },
    ],
    "Wednesday": [
        {
            "time": "9:30 AM",
            "subject": "Computer Science",
            "venue": "Room 107",
            "faculty": "Dr. Salvin Saju",
        },
        {
            "time": "11:30 AM",
            "subject": "Math",
            "venue": "Room 108",
            "faculty": "Dr. Noel G.J",
        },
        {
            "time": "1:30 PM",
            "subject": "Philosophy",
            "venue": "Room 109",
            "faculty": "Ms. Milna",
        },
    ],
}


# Load timetable from Supabase
def load_timetable():
    response = supabase.table("timetable").select("*").execute()
    data = response.data

    if not data:
        save_timetable(DEFAULT_TIMETABLE)
        return DEFAULT_TIMETABLE

    timetable = {}
    for entry in data:
        day = entry["day"]
        if day not in timetable:
            timetable[day] = []
        timetable[day].append(
            {
                "time": entry["time"],
                "subject": entry["subject"],
                "venue": entry["venue"],
                "faculty": entry["faculty"],
            }
        )
    return timetable


# Save timetable to Supabase
def save_timetable(timetable):
    # supabase.table("timetable").delete().neq("id", None).execute()

    # Clear old data

    new_data = []
    for day, sessions in timetable.items():
        for session in sessions:
            new_data.append(
                {
                    "day": day,
                    "time": session["time"],
                    "subject": session["subject"],
                    "venue": session["venue"],
                    "faculty": session["faculty"],
                }
            )

    supabase.table("timetable").insert(new_data).execute()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        entered_password = request.form.get("password")
        if entered_password == ADMIN_PASSWORD:
            return redirect(url_for("admin"))
        else:
            return render_template(
                "login.html", error="Invalid password, please try again."
            )
    return render_template("login.html")


@app.route("/admin", methods=["GET", "POST"])
def admin():
    timetable_data = load_timetable()

    if request.method == "POST":
        for day, sessions in timetable_data.items():
            for i, session in enumerate(sessions):
                new_subject = request.form.get(f"{day}_{session['time']}_subject")
                new_venue = request.form.get(f"{day}_{session['time']}_venue")
                new_faculty = request.form.get(f"{day}_{session['time']}_faculty")

                if new_subject:
                    timetable_data[day][i]["subject"] = new_subject
                if new_venue:
                    timetable_data[day][i]["venue"] = new_venue
                if new_faculty:
                    timetable_data[day][i]["faculty"] = new_faculty

        save_timetable(timetable_data)
        return render_template(
            "timetable.html", timetable=timetable_data, is_admin=True
        )

    return render_template("timetable.html", timetable=timetable_data, is_admin=True)


@app.route("/student")
def student():
    timetable_data = load_timetable()
    return render_template("timetable.html", timetable=timetable_data, is_admin=False)


if __name__ == "__main__":
    app.run(debug=True)
