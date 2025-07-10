from flask import Flask, render_template, request, redirect, session, flash
from auth import auth
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace this with a strong key in production

# Register auth blueprint
app.register_blueprint(auth)

# Database connection function
def get_db_connection():
    conn = sqlite3.connect('feedback.db')
    conn.row_factory = sqlite3.Row
    return conn

# Home page - feedback submission form
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('index.html')

# Submit feedback
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

# User's feedback dashboard
@app.route('/feedbacks')
def feedback_dashboard():
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_db_connection()
    username = session['username']
    feedbacks = conn.execute(
        'SELECT * FROM feedback WHERE name = ? ORDER BY id DESC', (username,)
    ).fetchall()
    conn.close()

    return render_template('feedback_dashboard.html', feedbacks=feedbacks)

# Admin dashboard (for user "admin" only)
@app.route('/admin')
def admin_dashboard():
    if 'user_id' not in session:
        return redirect('/login')

    if session['username'].lower() != 'admin':
        flash("❌ Access denied. Admins only.", "danger")
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

# 🔍 Debug route to check session (for development only)
@app.route('/test-session')
def test_session():
    return f"🧠 Session debug → username: {session.get('username')}, user_id: {session.get('user_id')}"

# Run the app locally
if __name__ == '__main__':
    app.run(debug=True)
