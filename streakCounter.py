from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import date, timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///streak.db'
db = SQLAlchemy(app)
app.secret_key = "hello"
app.permanent_session_lifetime = timedelta(minutes=60)

class Streak(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    last_check_in = db.Column(db.Date, nullable=False, default=date.today() - timedelta(days=1))
    streak_count = db.Column(db.Integer, nullable=False, default=0)
    

def get_streak():
    streak = Streak.query.first()
    if not streak:
        streak = Streak(streak_count=0)
        db.session.add(streak)
        db.session.commit()
    return streak

@app.route('/')
def index():
    if "user" in session:  
        user = session["user"]
        streak = get_streak()
        return render_template('index.html', user = user, streak=streak.streak_count, current_date = date.today(), last_date_checked_in=streak.last_check_in)
    else:
        return redirect(url_for('login'))

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        session.permanent = True
        name = request.form["fname"]
        session["user"] = name
        return redirect(url_for('index'))
    if request.method == "GET":
        return render_template('login.html')

@app.route("/logout")
def logout():
    if "user" in session:
        user = session["user"]
        flash("Logged out successfully", "info")
    session.pop("user", None)
    return redirect(url_for("login"))


@app.route('/check-in')
def check_in():
    streak = get_streak()
    today = date.today()
    if streak.last_check_in == today:
        pass  # Already checked in today
    elif streak.last_check_in == today - timedelta(days=1):
        streak.streak_count += 1  # Continue streak
    else:
        streak.streak_count = 0  # Reset streak
    
    streak.last_check_in = today
    ###streak.streak_count += 1
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)