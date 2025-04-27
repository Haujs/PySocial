from flask import Flask, request, render_template, redirect, session, url_for
import os, json, uuid, base64

app = Flask(__name__)
app.secret_key = 'supersecretkey'
DATA_FILE = 'data.json'

# Загрузка базы данных
def load_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w') as f:
            json.dump({"users": {}, "messages": []}, f)
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

# Сохранение базы данных
def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

@app.route('/')
def index():
    if 'username' in session:
        data = load_data()
        user = data['users'][session['username']]
        return render_template('app.html', action='profile', session=session, user=user, messages=[], results=None)
    return render_template('app.html', action='login')

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    data = load_data()
    if username in data['users']:
        return "Username already taken"
    user_id = str(uuid.uuid4())
    data['users'][username] = {
        "id": user_id,
        "password": password,
        "bio": "",
        "avatar": "",
        "admin": False
    }
    save_data(data)
    session['username'] = username
    return redirect('/')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    data = load_data()
    if username in data['users'] and data['users'][username]['password'] == password:
        session['username'] = username
        return redirect('/')
    return "Invalid credentials"

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/profile', methods=['POST'])
def profile():
    data = load_data()
    username = session['username']
    user = data['users'][username]
    user['bio'] = request.form['bio']
    if 'avatar' in request.files:
        avatar_file = request.files['avatar']
        if avatar_file and avatar_file.filename:
            avatar_data = base64.b64encode(avatar_file.read()).decode('utf-8')
            user['avatar'] = 'data:image/png;base64,' + avatar_data
    save_data(data)
    return redirect('/')

@app.route('/send_message', methods=['POST'])
def send_message():
    data = load_data()
    from_user = session['username']
    to_user = request.form['recipient']
    message = request.form['message']
    if to_user in data['users']:
        data['messages'].append({
            "from": from_user,
            "to": to_user,
            "message": message
        })
        save_data(data)
    return redirect('/')

@app.route('/chat/<username>')
def chat(username):
    data = load_data()
    messages = [
        msg for msg in data['messages']
        if (msg['from'] == session['username'] and msg['to'] == username) or
           (msg['from'] == username and msg['to'] == session['username'])
    ]
    user = data['users'][session['username']]
    return render_template('app.html', action='profile', session=session, user=user, messages=messages, results=None)

@app.route('/search')
def search():
    query = request.args.get('q', '').lower()
    data = load_data()
    results = [username for username in data['users'] if query in username.lower() and username != session['username']]
    user = data['users'][session['username']]
    return render_template('app.html', action='profile', session=session, user=user, results=results, messages=None)

if __name__ == '__main__':
    app.run(debug=True)
