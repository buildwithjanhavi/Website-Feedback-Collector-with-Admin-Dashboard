from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# Home route – Feedback form
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form['name']
        comment = request.form['comment']
        sentiment = request.form['sentiment']

        conn = sqlite3.connect('feedback.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO feedback (name, comment, sentiment) VALUES (?, ?, ?)",
                       (name, comment, sentiment))
        conn.commit()
        conn.close()

        return redirect('/thankyou')

    return render_template('index.html')

# Thank You page
@app.route('/thankyou')
def thankyou():
    return "<h2>Thank you for your feedback!</h2><a href='/'>Back</a>"

# Admin route – Dashboard
@app.route('/admin')
def admin():
    conn = sqlite3.connect('feedback.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM feedback")
    feedbacks = cursor.fetchall()
    conn.close()
    return render_template('admin.html', feedbacks=feedbacks)

if __name__ == '__main__':
    app.run(debug=True)
