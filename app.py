from flask import Flask, render_template, redirect, url_for, session
from auth import auth_bp
from database import get_feedbacks
import os

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "secret")

app.register_blueprint(auth_bp)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    
    username = session['username']
    if username.endswith("admin"):
        feedbacks = get_feedbacks()
        return render_template('admin_dashboard.html', username=username, feedbacks=feedbacks)
    else:
        return render_template('user_dashboard.html', username=username)

if __name__ == '__main__':
    app.run(debug=True)
