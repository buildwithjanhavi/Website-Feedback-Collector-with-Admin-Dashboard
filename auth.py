from flask import Blueprint, render_template, request, redirect, session, flash
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

            if username.lower() == 'admin':
                return redirect('/admin')
            else:
                return redirect('/feedbacks')
        else:
            flash('❌ Invalid credentials', 'danger')

    return render_template('login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('Please fill all fields.', 'warning')
            return redirect('/register')

        hashed_pw = generate_password_hash(password)

        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_pw))
            conn.commit()
            user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
            conn.close()

            session['user_id'] = user['id']
            session['username'] = user['username']

            if username.lower() == 'admin':
                return redirect('/admin')
            else:
                return redirect('/feedbacks')

        except sqlite3.IntegrityError:
            flash('Username already exists!', 'danger')
            conn.close()

    return render_template('register.html')

@auth.route('/logout')
def logout():
    session.clear()
    flash('Logged out.', 'info')
    return redirect('/login')
