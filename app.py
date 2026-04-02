from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

DB_NAME = "wellness.db"

# -------------------- Helper Functions -------------------- #
def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def insert_activity_if_not_exists(table, user_id, data):
    conn = get_db()
    cur = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")

    if table == "mood":
        cur.execute("INSERT INTO mood(user_id, mood_score, date) VALUES(?,?,?)", 
                    (user_id, data['mood_score'], today))
    elif table == "meditation":
        cur.execute("INSERT INTO meditation(user_id, duration, date) VALUES(?,?,?)",
                    (user_id, data['duration'], today))
    elif table == "sleep":
        cur.execute("INSERT INTO sleep(user_id, hours, quality, reflection, date) VALUES(?,?,?,?,?)",
                    (user_id, data['hours'], data['quality'], data['reflection'], today))
    elif table == "water":
        cur.execute("INSERT INTO water(user_id, glasses, date) VALUES(?,?,?)",
                    (user_id, data['glasses'], today))
    elif table == "habit":
        cur.execute("INSERT INTO habit(user_id, habit_name, done, date) VALUES(?,?,?,?)",
                    (user_id, data['habit_name'], data['done'], today))
    elif table == "journal":
        cur.execute("INSERT INTO journal(user_id, thoughts, gratitude, mood, date) VALUES(?,?,?,?,?)",
                    (user_id, data['thoughts'], data['gratitude'], data['mood'], today))
    conn.commit()
    conn.close()

def get_today_activities(user_id):
    today = datetime.now().strftime("%Y-%m-%d")
    conn = get_db()
    cur = conn.cursor()
    activities = {}

    for table in ["mood","meditation","sleep","water","habit","journal"]:
        cur.execute(f"SELECT * FROM {table} WHERE user_id=? AND date=?", (user_id, today))
        rows = cur.fetchall()
        
        if table == "habit":
            # ✅ Habit is done only if all habits for today are marked done
            activities[table] = len(rows) > 0 and all(row["done"] == 1 for row in rows)
        else:
            activities[table] = len(rows) > 0

    conn.close()
    return activities

# -------------------- Routes -------------------- #
@app.route("/")
def index():
    return redirect("/login")

# -------------------- Register -------------------- #
@app.route("/register", methods=["GET","POST"])
def register():
    message = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username and password:
            conn = get_db()
            cur = conn.cursor()
            try:
                cur.execute("INSERT INTO users(username, password) VALUES(?,?)", (username, password))
                conn.commit()
                message = "✅ Registered successfully! You can login."
            except sqlite3.IntegrityError:
                message = "❌ Username already exists."
            conn.close()
        else:
            message = "❌ Username and password are required."
    return render_template("register.html", message=message)

# -------------------- Login -------------------- #
@app.route("/login", methods=["GET","POST"])
def login():
    message = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username and password:
            conn = get_db()
            cur = conn.cursor()
            cur.execute("SELECT * FROM users WHERE username=? AND password=?", (username,password))
            user = cur.fetchone()
            conn.close()
            if user:
                session["user_id"] = user["id"]
                session["username"] = user["username"]
                return redirect("/dashboard")
            else:
                message="❌ Invalid credentials."
        else:
            message="❌ Username and password are required."
    return render_template("login.html", message=message)

# -------------------- Logout -------------------- #
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# -------------------- Dashboard -------------------- #
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")
    user_id = session["user_id"]
    activities = get_today_activities(user_id)
    quote = "🌟 Your wellness is your superpower today!"
    return render_template("dashboard.html", user=session["username"], quote=quote, activities=activities, score=0)

# -------------------- Mood -------------------- #
@app.route("/mood", methods=["GET","POST"])
def mood():
    if "user_id" not in session:
        return redirect("/login")
    message = None
    quote = "Your mood today sets the tone for tomorrow!"
    user_id = session["user_id"]

    if request.method == "POST":
        score_val = request.form.get("mood_score")
        if score_val:
            try:
                score_val = int(score_val)
                if 1 <= score_val <= 5:
                    insert_activity_if_not_exists("mood", user_id, {"user_id": user_id, "mood_score": score_val})
                    message = "Mood saved ✅"
                else:
                    message = "❌ Mood must be between 1 and 5."
            except ValueError:
                message = "❌ Invalid mood value."
        else:
            message = "❌ Please select your mood."

    return render_template("mood.html", message=message, quote=quote)

# -------------------- Meditation -------------------- #
@app.route("/meditation", methods=["GET","POST"])
def meditation():
    if "user_id" not in session:
        return redirect("/login")
    message = None
    quote = "🧘 Take a moment to calm your mind."
    user_id = session["user_id"]
    if request.method == "POST":
        duration = request.form.get("duration")
        try:
            duration = int(duration) if duration else 5
            insert_activity_if_not_exists("meditation", user_id, {"user_id":user_id,"duration":duration})
            message = "Meditation saved ✅"
        except ValueError:
            message = "❌ Invalid duration."
    return render_template("meditation.html", message=message, quote=quote)

# -------------------- Sleep -------------------- #
@app.route("/sleep", methods=["GET","POST"])
def sleep():
    if "user_id" not in session:
        return redirect("/login")
    message = None
    quote = "🌙 Sleep well to wake up refreshed!"
    user_id = session["user_id"]
    mood_score = None
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT mood_score FROM mood WHERE user_id=? ORDER BY date DESC LIMIT 1", (user_id,))
    row = cur.fetchone()
    if row:
        mood_score = row["mood_score"]
    conn.close()

    if request.method == "POST":
        hours = request.form.get("hours")
        quality = request.form.get("quality","Average")
        reflection = request.form.get("reflection","")
        try:
            hours = int(hours) if hours else 0
            insert_activity_if_not_exists("sleep", user_id, {"user_id":user_id,"hours":hours,"quality":quality,"reflection":reflection})
            message = "Sleep data saved ✅"
        except ValueError:
            message = "❌ Invalid hours."
    return render_template("sleep.html", quote=quote, message=message, mood_score=mood_score)

# -------------------- Water -------------------- #
@app.route("/water", methods=["GET","POST"])
def water():
    if "user_id" not in session:
        return redirect("/login")
    message = None
    quote = "💧 Hydrate well to stay energized!"
    user_id = session["user_id"]

    if request.method == "POST":
        glasses = request.form.get("glasses")
        try:
            glasses = int(glasses) if glasses else 0
            insert_activity_if_not_exists("water", user_id, {"user_id":user_id,"glasses":glasses})
            message = "Water intake saved ✅"
        except ValueError:
            message = "❌ Invalid number of glasses."
    return render_template("water.html", quote=quote, message=message)

# -------------------- Habit -------------------- #
@app.route("/habit", methods=["GET","POST"])
def habit():
    if "user_id" not in session:
        return redirect("/login")
    message = None
    quote = "📅 Track your daily habits!"
    user_id = session["user_id"]
    today = datetime.now().strftime("%Y-%m-%d")
    conn = get_db()
    cur = conn.cursor()

    # Add new habit from form
    if request.method == "POST" and "habit_name" in request.form:
        habit_name = request.form.get("habit_name")
        if habit_name:
            insert_activity_if_not_exists("habit", user_id, {"user_id":user_id,"habit_name":habit_name,"done":0})
            message = "Habit added ✅"
        else:
            message = "❌ Enter a habit name."

    # Handle completion updates
    if request.method == "POST" and "completed_habits" in request.form:
        completed = request.form.getlist("completed_habits")
        for habit_name in completed:
            cur.execute("UPDATE habit SET done=1 WHERE user_id=? AND habit_name=? AND date=?",
                        (user_id, habit_name, today))
        conn.commit()
        message = "Habits updated ✅"

    # Get today's habits
    cur.execute("SELECT habit_name, done FROM habit WHERE user_id=? AND date=?", (user_id,today))
    habits = cur.fetchall()
    conn.close()

    return render_template(
        "habit.html",
        quote=quote,
        habits=[(h["habit_name"], h["done"]) for h in habits],
        message=message,
        recommended_habits=["Drink Water","Meditate","Sleep well"]
    )

# -------------------- Journal -------------------- #
@app.route("/journal", methods=["GET","POST"])
def journal():
    if "user_id" not in session:
        return redirect("/login")
    message = None
    quote = "📖 Reflect to improve your wellness!"
    user_id = session["user_id"]
    today = datetime.now().strftime("%Y-%m-%d")
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM journal WHERE user_id=? AND date=?", (user_id,today))
    notes = cur.fetchone()

    if request.method == "POST":
        thoughts = request.form.get("thoughts","")
        gratitude = request.form.get("gratitude","")
        mood_val = request.form.get("mood","Neutral")
        insert_activity_if_not_exists("journal", user_id, {"user_id":user_id,"thoughts":thoughts,"gratitude":gratitude,"mood":mood_val})
        message = "Journal saved ✅"
    conn.close()
    return render_template("journal.html", quote=quote, notes=notes, message=message, activities=get_today_activities(user_id))

# -------------------- Wellness Score -------------------- #
@app.route("/score")
def score():
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]
    activities = get_today_activities(user_id)

    quote = "🎯 Here’s your wellness score!"

    suggestions = []

    if not activities["mood"]:
        suggestions.append("Log your mood today.")
    if not activities["meditation"]:
        suggestions.append("Do 5 minutes meditation.")
    if not activities["sleep"]:
        suggestions.append("Track your sleep hours.")
    if not activities["water"]:
        suggestions.append("Drink at least 7 glasses of water.")
    if not activities["habit"]:
        suggestions.append("Complete your daily habits.")
    if not activities["journal"]:
        suggestions.append("Write your daily journal.")

    tomorrow_tips = [
        "Drink water regularly.",
        "Sleep at least 7 hours.",
        "Meditate daily for calm mind.",
        "Reflect positive thoughts."
    ]

    return render_template(
        "score.html",
        quote=quote,
        activities=activities,   # ⭐ THIS LINE IS IMPORTANT
        suggestions=suggestions,
        tomorrow_tips=tomorrow_tips
    )
    return render_template("score.html", quote=quote, activities=activities, suggestions=suggestions, tomorrow_tips=tomorrow_tips)

# -------------------- Run App -------------------- #
if __name__=="__main__":
    if not os.path.exists(DB_NAME):
        os.system("python init_db.py")
    app.run(debug=True)