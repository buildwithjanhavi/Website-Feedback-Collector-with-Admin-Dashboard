from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from database import init_db, get_db_connection

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Initialize the database
init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()

        if not username or not password:
            flash('Please fill in all fields.')
            return redirect(url_for('register'))

        conn = get_db_connection()
        existing_user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()

        if existing_user:
            conn.close()
            flash('Username already exists.')
            return redirect(url_for('register'))

        conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        conn.close()
        flash('Registration successful. Please log in.')
        return redirect(url_for('login'))

    return render_template('register.html')

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
            if 'admin' in username.lower():
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']

    if request.method == 'POST':
        feedback = request.form['feedback'].strip()
        rating = request.form['rating']
        category = request.form['category']

        if not feedback or not rating or not category:
            flash("All fields are required.")
            return redirect(url_for('dashboard'))

        conn = get_db_connection()
        conn.execute(
            'INSERT INTO feedback (username, feedback, rating, category) VALUES (?, ?, ?, ?)',
            (username, feedback, rating, category)
        )
        conn.commit()
        conn.close()

        flash("Thank you for submitting your feedback!")
        return redirect(url_for('dashboard'))

    return render_template('user_dashboard.html', username=username)

@app.route('/admin-dashboard')
def admin_dashboard():
    if 'username' not in session or 'admin' not in session['username'].lower():
        flash("Unauthorized access.")
        return redirect(url_for('login'))

    conn = get_db_connection()
    feedbacks = conn.execute('SELECT * FROM feedback ORDER BY id DESC').fetchall()
    stats = conn.execute('SELECT category, COUNT(*) as count FROM feedback GROUP BY category').fetchall()
    conn.close()

    return render_template('admin_dashboard.html', feedbacks=feedbacks, stats=stats)

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("Logged out successfully.")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
