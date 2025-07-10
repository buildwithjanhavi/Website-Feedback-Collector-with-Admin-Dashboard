from flask import Flask, render_template, request, redirect, session, flash
from auth import auth
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace this securely in production
app.register_blueprint(auth)

def get_db_connection():
    conn = sqlite3.connect('feedback.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    if 'user_id' not in session:
        return redirect('/login')

    name = session['username']
    feedback = request.form['feedback']
    sentiment = request.form['sentiment']

    conn = get_db_connection()
    conn.execute(
        'INSERT INTO feedback (name, feedback, sentiment) VALUES (?, ?, ?)',
        (name, feedback, sentiment)
    )
    conn.commit()
    conn.close()

    flash('✅ Feedback submitted successfully!', 'success')
    return redirect('/')

@app.route('/feedbacks')
def feedback_dashboard():
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_db_connection()
    feedbacks = conn.execute(
        'SELECT * FROM feedback WHERE name = ? ORDER BY id DESC',
        (session['username'],)
    ).fetchall()
    conn.close()

    return render_template('feedback_dashboard.html', feedbacks=feedbacks)

@app.route('/admin')
def admin_dashboard():
    if 'user_id' not in session or session.get('username', '').lower() != 'admin':
        flash("Access denied.", "danger")
        return redirect('/')

    search = request.args.get('search')
    conn = get_db_connection()
    if search:
        feedbacks = conn.execute(
            'SELECT * FROM feedback WHERE feedback LIKE ?',
            ('%' + search + '%',)
        ).fetchall()
    else:
        feedbacks = conn.execute(
            'SELECT * FROM feedback ORDER BY id DESC'
        ).fetchall()
    conn.close()
    return render_template('admin_dashboard.html', feedbacks=feedbacks, search=search)

@app.route('/test-session')
def test_session():
    return f"Session debug → username: {session.get('username')}, user_id: {session.get('user_id')}"

if __name__ == '__main__':
    app.run(debug=True)
