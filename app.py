from flask import Flask, render_template, request, redirect, url_for, session, flash
from auth import auth
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # change this in production!

app.register_blueprint(auth)

def get_db_connection():
    conn = sqlite3.connect('feedback.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    conn = get_db_connection()
    feedbacks = conn.execute('SELECT * FROM feedback ORDER BY id DESC').fetchall()
    conn.close()
    return render_template('index.html', feedbacks=feedbacks)

@app.route('/submit', methods=['POST'])
def submit():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    name = request.form['name']
    feedback = request.form['feedback']
    sentiment = request.form['sentiment']
    conn = get_db_connection()
    conn.execute('INSERT INTO feedback (name, feedback, sentiment) VALUES (?, ?, ?)',
                 (name, feedback, sentiment))
    conn.commit()
    conn.close()
    flash('Feedback submitted!', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
