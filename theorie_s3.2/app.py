from flask import Flask, request, session, render_template
import os

app = Flask(__name__, template_folder='templates')
app.secret_key = 'demo_secret_key'  # Nécessaire pour session
app.config['APP_NAME'] = 'Mon Super Site'
app.config['MAIL_ADMIN'] = 'admin@example.com'


@app.route('/')
def home():
    # Exemple : mettre un user en session
    session['username'] = 'Kusay'
    session['user_id'] = 123
    return render_template('home.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/profil')
def profil():
    return render_template('profil.html')
 

if __name__ == "__main__":
    app.run(debug=True)
