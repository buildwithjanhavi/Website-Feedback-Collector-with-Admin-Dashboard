from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

DATABASE = 'feedback.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', 
                            (username, password)).fetchone()
        conn.close()
        if user:
            session['username'] = username
            if username.endswith('admin'):
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))
        else:
            flash('Invalid credentials')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        existing = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        if existing:
            flash('Username already exists')
            return redirect(url_for('register'))
        conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        conn.close()
        flash('Registered successfully! Please login.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/user_dashboard', methods=['GET', 'POST'])
def user_dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        feedback = request.form['feedback']
        rating = request.form.get('rating')
        category = request.form.get('category')
        conn = get_db_connection()
        conn.execute('INSERT INTO feedback (username, feedback, rating, category) VALUES (?, ?, ?, ?)', 
                     (session['username'], feedback, rating, category))
        conn.commit()
        conn.close()
        flash('Thank you for submitting the feedback!')
    return render_template('user_dashboard.html', username=session['username'])

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'username' not in session or not session['username'].endswith('admin'):
        return redirect(url_for('login'))
    conn = get_db_connection()
    feedbacks = conn.execute('SELECT * FROM feedback').fetchall()
    conn.close()
    return render_template('admin_dashboard.html', feedbacks=feedbacks)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
