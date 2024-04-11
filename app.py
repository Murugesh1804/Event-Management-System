from flask import Flask, render_template, request, redirect, url_for,g,flash, get_flashed_messages
from flask_login import LoginManager, UserMixin, login_user
from flask_login import login_required, current_user
import sqlite3

app = Flask(__name__,static_folder="")
app.secret_key = 'secret'

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

DATABASE = 'sign.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def connect_db():
    return sqlite3.connect(DATABASE)

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/signup', methods=['POST','GET'])
def signup():
    if request.method == 'POST':
        username = request.form['uname']
        password = request.form['pwd']
        email = request.form['mail']
        phno = request.form['phno']

        db = get_db()
        cursor = db.cursor()

        cursor.execute('INSERT INTO users (username, password, email, phno) VALUES (?, ?, ?, ?)', (username, password, email, phno))
        db.commit()

        if cursor.rowcount > 0:
            msg = 'User added Successfully !!!'
            return render_template('index.html', msg=msg)
        else:
            msg = 'Failed to add user'
            return render_template('signup.html', msg=msg)

    return render_template('signup.html')

# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

@login_manager.user_loader
def load_user(user_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user_data = cursor.fetchone()
    db.close()
    if user_data:
        return User(user_data[0])  

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['uname']
        password = request.form['pwd']

        db = get_db()
        cursor = db.cursor()

        cursor.execute('SELECT id FROM users WHERE username = ? AND password = ?', (username, password))
        user_id = cursor.fetchone()

        db.close()

        if user_id:
            user = User(user_id[0])
            login_user(user)  # Log in the user
            msg = 'Logged in !!!'
            flash(msg)
            return redirect(url_for('index'))  # Redirect to the index page after successful login
        else:
            msg = 'User Not found !! SignUp first...'
            flash(msg)
            return redirect(url_for('signup')) 
        
    return render_template('login.html')
    
@app.route('/organize', methods=['POST','GET'])
def organize():
    if request.method == 'POST':
        event_name = request.form['event_name']
        date = request.form['event_date']
        time = request.form['event_time']
        location = request.form['event_location']
        organizer_name = request.form['organizer_name']
        phone_number = request.form['organizer_phone']
        email = request.form['organizer_email']

        db = get_db()
        cursor = db.cursor()


        cursor.execute('INSERT INTO events (eventName, eventDate, eventTime, eventLocation, organizerName, phoneNumber, mailId) VALUES (?, ?, ?, ?, ?, ?, ?)',
                       (event_name, date, time, location, organizer_name, phone_number, email))
        db.commit()

        if cursor.rowcount > 0:
            msg = 'Event added Successfully !!!'
            return render_template('index.html', msg=msg)
        else:
            msg = 'Failed to add Event'
            return render_template('signup.html', msg=msg)

    return render_template('organize.html')

@app.route('/book', methods=['POST','GET'])
def book():
    conn = sqlite3.connect('sign.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM events WHERE eventName IS NOT NULL')
    events = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    conn.close()
    return render_template('book-now.html', events=events)


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

# Load user callback for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT username FROM users WHERE id = ?', (user_id,))
    user_data = cursor.fetchone()
    cursor.close()
    if user_data:
        return User(user_data[0])

def get_db2():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('booking.db')
    return db

@app.route('/verify', methods=['POST'])
def verify():
    try:
        event_name = request.form['eventName']
        event_date = request.form['eventDate']
        event_time = request.form['eventTime']
        event_loc = request.form['eventLocation']
        user_id = current_user.id

        db = get_db2()
        cursor = db.cursor()

        cursor.execute('''
            INSERT INTO eventBooked (event_name, event_date, event_time, event_location, user_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (event_name, event_date, event_time, event_loc, user_id))

        db.commit()

        msg = 'Event Booking successful'
    except Exception as e:
        msg = 'Error: ' + str(e)
        # Rollback transaction if error occurs
        db.rollback()
    finally:
        # Close cursor
        cursor.close()

    return render_template('index.html',msg=msg)

@app.route('/booking', methods=['POST'])
@login_required
def booking():
        event_name = request.form['eventName']
        event_date = request.form['eventDate']
        event_time = request.form['eventTime']
        event_loc = request.form['eventLocation']
        user_id = current_user.id
        
        return render_template('verify.html',event_name=event_name, event_date=event_date, event_time=event_time, event_loc=event_loc, user_id=user_id)


    # except Exception as e:
    #     msg = 'Error: ' + str(e)
    #     # Rollback transaction if error occurs
    #     db.rollback()
    # finally:
    #     # Close cursor
    #     cursor.close()

    # return render_template('index.html',msg=msg)



if __name__ == '__main__':
     app.run(debug=True)
