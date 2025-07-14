from flask import Flask, render_template, request, redirect, session, flash
import sqlite3
from textblob import TextBlob

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Connect to database
def get_db_connection():
    conn = sqlite3.connect('feedback.db')
    conn.row_factory = sqlite3.Row
    return conn

# Home page
@app.route('/')
def index():
    return render_template('index.html')

# Register
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
            flash('Username already exists. Try another.', 'error')
        finally:
            conn.close()
    return render_template('register.html')

# Login
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
            else:
                return redirect('/dashboard')
        else:
            flash('Invalid credentials. Try again.', 'error')
    return render_template('login.html')

# User Dashboard
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' not in session or session['username'].endswith('admin'):
        return redirect('/login')
    
    username = session['username']
    
    if request.method == 'POST':
        feedback = request.form['feedback']
        rating = request.form.get('rating')
        category = request.form.get('category')

        # Sentiment Analysis
        sentiment = TextBlob(feedback).sentiment.polarity
        if sentiment > 0:
            sentiment_label = 'Positive'
        elif sentiment < 0:
            sentiment_label = 'Negative'
        else:
            sentiment_label = 'Neutral'

        conn = get_db_connection()
        conn.execute(
            'INSERT INTO feedback (username, feedback, rating, category, sentiment) VALUES (?, ?, ?, ?, ?)',
            (username, feedback, rating, category, sentiment_label)
        )
        conn.commit()
        conn.close()
        flash('Thank you for submitting your feedback!', 'success')
        return redirect('/dashboard')

    return render_template('user_dashboard.html', username=username)

# Admin Dashboard
@app.route('/admin-dashboard')
def admin_dashboard():
    if 'username' not in session or not session['username'].endswith('admin'):
        return redirect('/login')
    
    conn = get_db_connection()
    feedback = conn.execute('SELECT * FROM feedback').fetchall()
    stats = conn.execute('''
        SELECT category, COUNT(*) as count
        FROM feedback
        GROUP BY category
    ''').fetchall()
    conn.close()
    
    return render_template('admin_dashboard.html', feedback=feedback, stats=stats)

# Logout
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
