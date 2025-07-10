from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

auth = Blueprint('auth', __name__)

def get_db_connection():
    conn = sqlite3.connect('feedback.db')
    conn.row_factory = sqlite3.Row
    return conn

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash('Login successful!', 'success')

            # Redirect to proper dashboard
            if username.lower() == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('feedback_dashboard'))
        else:
            flash('Invalid credentials', 'danger')
    return render_template('login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])

        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            conn.commit()

            # Auto-login after register
            user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
            conn.close()

            session['user_id'] = user['id']
            session['username'] = user['username']

            # Redirect to dashboard
            if username.lower() == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('feedback_dashboard'))

        except sqlite3.IntegrityError:
            flash('Username already exists!', 'danger')
            conn.close()

    return render_template('register.html')

@auth.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('auth.login'))
