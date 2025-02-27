from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import date, timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///streak.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = "hello"
app.permanent_session_lifetime = timedelta(minutes=60)

##add an actual password hashing system and login manager, so people can't just
##access the check-in page since when they go directly into that page
##it breaks the site since it would return a NoneType as per line 34

db = SQLAlchemy(app)


class Streak(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    last_check_in = db.Column(db.Date, nullable=False, default=date.today() - timedelta(days=1))
    streak_count = db.Column(db.Integer, nullable=False, default=0)
    email = db.Column(db.String(100))

    def __init__(self, name, last_check_in, streak_count, email):
        self.name = name
        self.last_check_in = last_check_in
        self.streak_count = streak_count
        self.email = email

'''class Milestone(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(100))
    threshold = db.Column(db.Integer, nullable=False)

def calculate_progress(streak_count):
    # Get all milestone thresholds sorted in ascending order
    milestones = [m.threshold for m in Milestone.query.order_by(Milestone.threshold).all()]
    
    # Determine the next milestone
    for milestone in milestones:
        if streak_count < milestone:
            return {
                "current": streak_count,
                "next": milestone,
                "progress_percent": int((streak_count / milestone) * 100)
            }
    
    # If all milestones are passed
    return {
        "current": streak_count,
        "next": None,
        "progress_percent": 100
    }
'''

def get_streak():
    if "user" not in session:
        return None
    return Streak.query.filter_by(name=session["user"]).first()

    '''streak = Streak.query.first()
    if not streak:
        streak = Streak(streak_count=0)
        db.session.add(streak)
        db.session.commit()
    return streak'''

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
        user = request.form["fname"]
        session["user"] = user
        
        found_user = Streak.query.filter_by(name = user).first()
        ##if found_user:
            ##session["email"] = found_user.email
        if not found_user:
            usr = Streak(name=user, last_check_in=date.today()-timedelta(days=1), streak_count=0, email=request.form["email"])
            db.session.add(usr)
            db.session.commit()


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
        ##flash message here to tell the user that they 
        ##missed the last login, needs further testing, make sure that it doesn't
        ##pop up messages from the login screen "Logged out successfully" or make sure 
        ##it doesn't always just flash the message everytime. 
        ###flash("Logged out successfully")
        streak.streak_count = 1  # Reset streak
    
    streak.last_check_in = today
    ###streak.streak_count += 1
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)