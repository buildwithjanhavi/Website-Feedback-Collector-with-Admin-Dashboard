from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# DB connection
def get_db_connection():
    conn = sqlite3.connect('feedback.db')
    conn.row_factory = sqlite3.Row
    return conn

# Home
@app.route('/')
def index():
    return render_template('index.html')

# Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()

        if not username or not password:
            flash('Please fill out all fields.')
            return redirect(url_for('register'))

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        if cursor.fetchone():
            flash('Username already exists.')
            conn.close()
            return redirect(url_for('register'))

        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        conn.close()
        flash('Registered successfully. Please log in.')
        return redirect(url_for('login'))

    return render_template('register.html')

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password)).fetchone()
        conn.close()

        if user:
            session['username'] = username
            if username.endswith('admin'):
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials.')
            return redirect(url_for('login'))

    return render_template('login.html')

# User Dashboard
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        username = session['username']
        feedback = request.form['feedback'].strip()
        rating = request.form['rating']
        category = request.form['category']

        if not feedback or not rating or not category:
            flash('All fields are required.')
            return redirect(url_for('dashboard'))

        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO feedback (username, feedback, rating, category) VALUES (?, ?, ?, ?)',
                         (username, feedback, rating, category))
            conn.commit()
            flash('Thank you for submitting the feedback!')
        except Exception as e:
            flash('An error occurred while submitting your feedback.')
        finally:
            conn.close()
        return redirect(url_for('dashboard'))

    return render_template('user_dashboard.html')

# Admin Dashboard
@app.route('/admin-dashboard')
def admin_dashboard():
    if 'username' not in session or not session['username'].endswith('admin'):
        flash('Unauthorized access')
        return redirect(url_for('login'))

    conn = get_db_connection()
    feedback = conn.execute('SELECT * FROM feedback').fetchall()
    conn.close()
    return render_template('admin_dashboard.html', feedback=feedback)

# Logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Logged out successfully.')
    return redirect(url_for('login'))

# Run
if __name__ == '__main__':
    app.run(debug=True)
