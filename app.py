from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace with your secure key

# ---------- Sentiment Logic (Simple) ----------
def get_sentiment(text):
    text = text.lower()
    if any(word in text for word in ['good', 'great', 'awesome', 'excellent', 'love']):
        return 'Positive'
    elif any(word in text for word in ['bad', 'poor', 'worst', 'hate', 'terrible']):
        return 'Negative'
    else:
        return 'Neutral'

# ---------- DB Connection ----------
def get_db_connection():
    conn = sqlite3.connect('feedback.db')
    conn.row_factory = sqlite3.Row
    return conn

# ---------- Landing Page ----------
@app.route('/')
def index():
    return render_template('index.html')

# ---------- Registration ----------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        if cursor.fetchone():
            flash('Username already exists')
            return redirect(url_for('register'))

        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        conn.close()
        flash('Registered successfully. Please login.')
        return redirect(url_for('login'))

    return render_template('register.html')

# ---------- Login ----------
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
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))
        else:
            flash('Invalid credentials')
            return redirect(url_for('login'))

    return render_template('login.html')

# ---------- Logout ----------
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.')
    return redirect(url_for('login'))

# ---------- User Dashboard ----------
@app.route('/user')
def user_dashboard():
    if 'username' not in session or session['username'].endswith('admin'):
        return redirect(url_for('login'))
    return render_template('user_dashboard.html')

# ---------- Submit Feedback ----------
@app.route('/submit-feedback', methods=['POST'])
def submit_feedback():
    if 'username' not in session:
        return redirect(url_for('login'))

    content = request.form['content']
    rating = request.form.get('rating', 'N/A')
    sentiment = get_sentiment(content)

    conn = get_db_connection()
    conn.execute('INSERT INTO feedback (username, content, sentiment, rating) VALUES (?, ?, ?, ?)',
                 (session['username'], content, sentiment, rating))
    conn.commit()
    conn.close()

    flash("Thank you for submitting your feedback!")
    return redirect(url_for('user_dashboard'))

# ---------- Admin Dashboard ----------
@app.route('/admin')
def admin_dashboard():
    if 'username' not in session or not session['username'].endswith('admin'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM feedback')
    feedbacks = cursor.fetchall()

    cursor.execute('SELECT COUNT(*) FROM feedback')
    total_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM feedback WHERE sentiment = 'Positive'")
    positive_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM feedback WHERE sentiment = 'Neutral'")
    neutral_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM feedback WHERE sentiment = 'Negative'")
    negative_count = cursor.fetchone()[0]

    conn.close()

    return render_template('admin_dashboard.html',
                           feedbacks=feedbacks,
                           total_count=total_count,
                           positive_count=positive_count,
                           neutral_count=neutral_count,
                           negative_count=negative_count)

# ---------- Run ----------
if __name__ == '__main__':
    app.run(debug=True)
