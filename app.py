from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os

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
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        if user:
            flash('Username already exists')
            return redirect(url_for('register'))
        conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        conn.close()
        flash('Registered successfully. Please login.')
        return redirect(url_for('login'))
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
            if 'admin' in username.lower():
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials')
    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        username = session['username']
        feedback = request.form['feedback']
        rating = request.form['rating']
        category = request.form['category']
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO feedback (username, feedback, rating, category) VALUES (?, ?, ?, ?)',
            (username, feedback, rating, category)
        )
        conn.commit()
        conn.close()
        flash('Thank you for submitting feedback.')
        return redirect(url_for('dashboard'))
    return render_template('user_dashboard.html', username=session['username'])

@app.route('/admin-dashboard')
def admin_dashboard():
    if 'username' not in session or 'admin' not in session['username'].lower():
        return redirect(url_for('login'))
    conn = get_db_connection()
    feedbacks = conn.execute('SELECT * FROM feedback').fetchall()
    stats = conn.execute("""
        SELECT category, COUNT(*) as count
        FROM feedback
        GROUP BY category
    """).fetchall()
    conn.close()
    return render_template('admin_dashboard.html', feedbacks=feedbacks, stats=stats)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))
