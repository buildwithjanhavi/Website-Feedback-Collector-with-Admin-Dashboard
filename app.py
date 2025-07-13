from flask import Flask, render_template, request, redirect, session, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def get_db_connection():
    conn = sqlite3.connect('feedback.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            conn.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect('/login')
        except sqlite3.IntegrityError:
            flash('Username already exists. Please try another.', 'danger')
        finally:
            conn.close()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password)).fetchone()
        conn.close()
        if user:
            session['username'] = username
            if username.endswith('admin'):
                return redirect('/admin-dashboard')
            return redirect('/dashboard')
        else:
            flash('Invalid credentials. Please try again.', 'danger')
    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' not in session:
        return redirect('/login')
    if request.method == 'POST':
        feedback = request.form['feedback']
        rating = request.form['rating']
        category = request.form['category']
        username = session['username']
        conn = get_db_connection()
        conn.execute('INSERT INTO feedback (username, feedback, rating, category) VALUES (?, ?, ?, ?)', 
                     (username, feedback, rating, category))
        conn.commit()
        conn.close()
        flash('Thank you for submitting the feedback!', 'success')
    return render_template('user_dashboard.html', username=session['username'])

@app.route('/admin-dashboard')
def admin_dashboard():
    if 'username' not in session or not session['username'].endswith('admin'):
        return redirect('/login')
    conn = get_db_connection()
    feedbacks = conn.execute('SELECT * FROM feedback').fetchall()
    conn.close()
    total = len(feedbacks)
    avg_rating = round(sum([f['rating'] for f in feedbacks])/total, 2) if total else 0
    categories = {}
    for f in feedbacks:
        cat = f['category']
        categories[cat] = categories.get(cat, 0) + 1
    return render_template('admin_dashboard.html', feedbacks=feedbacks, total=total, avg_rating=avg_rating, categories=categories)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')
