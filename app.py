from flask import Flask, request
from db_interactions import select, insert, delete, update
import bcrypt
from flask import jsonify
from flask_cors import CORS

app = Flask(__name__)

CORS(app, origins=['http://localhost:3000', 'https://shiny-malabi-e40d14.netlify.app'], supports_credentials=True, with_credentials=True)

@app.route("/", methods=['GET'])
def index():
    return 'Dino'

@app.route('/personal-leaderboard', methods=['GET'])
def get_personal_leaderboard():
    username = request.args.get('user', type=str) 
    data = select("""SELECT score, date, username FROM scores 
    JOIN users ON users.user_id = scores.user_id 
    WHERE username = %s
    ORDER BY score DESC, date;""",(username,)
    )

    formatted_data = []
    for i in range(len(data)):
        each_score = {'score': data[i][0], 'date': data[i][1] }
        formatted_data.append(each_score)
    return formatted_data, 200, {'Content-Type': 'application/json'}

@app.route('/global-leaderboard', methods=['GET'])
def get_global_leaderboard():
    data = select("""SELECT username, score, dino_id
    FROM scores JOIN users ON users.user_id = scores.user_id
    ORDER BY score DESC;""")
    formatted_data = []
    for i in range(len(data)):
        each_score = {'name': data[i][0], 'score': data[i][1], 'dinoId': data[i][2]}
        formatted_data.append(each_score)
    return formatted_data, 200, {'Content-Type': 'application/json'}

@app.route('/get-rank', methods=['GET'])
def get_rank():
    data = select("""SELECT username FROM (
        SELECT DISTINCT ON (username) *
        FROM scores JOIN users ON users.user_id = scores.user_id
        ORDER BY username, score DESC
        ) t
        ORDER BY score DESC;
        """)
    username = request.args.get('user', type=str)
    rank = [i+1 for (i, user) in enumerate(data) if user[0] == username]

    return rank, 200, {'Content-Type': 'application/json'}

@app.route('/submit-score', methods=['POST'])
def submit_score():
    data = request.json
    username = data["username"]
    score = data["score"]
    items = data["items"]
    user_id = select("SELECT user_id FROM users WHERE username = %s", (username,))
    format_user_id = user_id[0][0]
    query = insert(
        """INSERT INTO scores (user_id, score, date, items) 
        VALUES (%s, %s, current_timestamp, %s);""", 
        (format_user_id,score,items))
    return {"status": query[0], "code": query[1]}

@app.route('/create-account', methods=['POST'])
def set_username_and_password():
    data = request.json
    username = data["username"]
    password = data["password"].encode('utf8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password, salt).decode('utf8')
    query = insert(
        """INSERT INTO users (username, hashed_password) 
        VALUES (%s, %s);""", 
        (username, hashed_password)
        )
    return {"status": query[0], "code": query[1]}


@app.route('/login', methods=['POST'])
def check_username_and_password():
    data = request.json
    username = data["username"]
    query = select(
        """SELECT hashed_password, dino_id FROM users
        WHERE username = %s""",
        (username,)
        )
    entered_password = data["password"].encode('utf8')
    if len(query) > 0:
        hashed_password = query[0][0].encode('utf8')
    if len(query) == 0:
        return jsonify({"status": "No matching user found", "code": 404})
    elif bcrypt.checkpw(entered_password, hashed_password):
        dino_id = query[0][1]
        return_data = {"match": True, "status": 'success', "code": 200, "dino_id": dino_id}
        return jsonify(return_data)
    else:
        return_data = {"match": False, "status": 'Unauthorised', "code": 401}
        return jsonify(return_data)

@app.route('/delete-account', methods=['DELETE'])
def delete_account():
    data = request.json
    username = data["username"]
    print(username)
    query = delete(
        """DELETE FROM scores
        WHERE user_id = (SELECT user_id FROM users WHERE username=%s);

        DELETE FROM sessions
        WHERE user_id = (SELECT user_id FROM users WHERE username=%s);

        DELETE FROM users
        WHERE username=%s;""",
        (username, username, username)
        )
    return {"status": query[0], "code": query[1]}


@app.route('/change-password', methods=['POST'])
def change_password():
    data = request.json
    username = data["username"]
    check_pw_query = select(
        """SELECT (hashed_password) FROM users
        WHERE username = %s""",
        (username,)
        )
    old_password = data["oldPassword"].encode('utf8')
    new_password = data["newPassword"].encode('utf8')
    current_hashed_password = check_pw_query[0][0].encode('utf8')
    if bcrypt.checkpw(old_password, current_hashed_password):
        salt = bcrypt.gensalt()
        new_hashed_password = bcrypt.hashpw(new_password, salt).decode('utf8')
        update(
            """UPDATE users
            SET hashed_password = %s
            WHERE username = %s;""",
            (new_hashed_password, username)
            )
        return_data = {"match": True, "status": 'success', "code": 200}
        return jsonify(return_data)
    else:
        return_data = {"match": False, "status": 'Unauthorised - incorrect password', "code": 401}
        return jsonify(return_data)

@app.route('/change-username', methods=['POST'])
def change_username():
    data = request.json
    old_username = data["oldUsername"]
    check_pw_query = select(
        """SELECT (hashed_password) FROM users
        WHERE username = %s""",
        (old_username,)
        )
    entered_password = data["password"].encode('utf8')
    new_username = data["newUsername"]
    current_hashed_password = check_pw_query[0][0].encode('utf8')
    search_new_username_query = select(
        """SELECT (username) FROM users
        WHERE username = %s""", (new_username,)
        )
    if len(search_new_username_query) == 1:
        return_data = {"match": False, "status": 'Unauthorised - username already exists', "code": 409}
        return jsonify(return_data)
    if bcrypt.checkpw(entered_password, current_hashed_password):
        update(
            """UPDATE users
            SET username = %s
            WHERE username = %s;""",
            (new_username, old_username)
            )
        return_data = {"match": True, "status": 'success', "code": 200}
        return jsonify(return_data)
    else:
        return_data = {"match": False, "status": "Unauthorised - incorrect password", "code": 401}
        return jsonify(return_data)

@app.route('/change-avatar', methods=['POST'])
def change_avatar():
    data = request.json
    username = data['username']
    avatar = data['newAvatar']

    change_avatar_query = update(
        """UPDATE users 
        SET dino_id = %s
        WHERE username = %s""",
        (avatar, username)
    )

    if change_avatar_query[1] == 200:
        return_data = {"match": True, "status": "success", "code": 200}
        return jsonify(return_data)
    else:
        return_data = {"match": False, "status": "internal server error", "code": 500}
        return jsonify(return_data)

@app.route('/check-user-exists', methods=['GET'])
def check_user_exists():
    username = request.args.get('user', type=str) 
    data = select("""SELECT username FROM users 
    WHERE username = %s""",(username,))
    return data, 200, {'Content-Type': 'application/json'}

@app.route('/user-avatar', methods=['GET'])
def get_avatar():
    username = request.args.get('user', type=str) 
    data = select("""SELECT dino_id FROM users 
    WHERE username = %s""",(username,))
    return data, 200, {'Content-Type': 'application/json'}

@app.route('/unlocked-avatars', methods=['GET'])
def get_unlocked_avatars():
    username = request.args.get('user', type=str) 
    data = select("""SELECT MAX(items) FROM scores JOIN users ON scores.user_id=users.user_id
    WHERE username = %s""",(username,))
    return data, 200, {'Content-Type': 'application/json'}

@app.route('/set-session', methods=['POST'])
def set_session_id():
    data = request.json
    username = data['username']
    session_id = data['sessionId']
    query = insert("""INSERT INTO sessions (uuid, created_at, user_id) 
        VALUES (%s, current_timestamp, (
            SELECT user_id FROM users
            WHERE username=%s));""", 
        (session_id,username))
    return {"status": query[0], "code": query[1]}

@app.route('/get-session', methods=['GET'])
def get_session_id():
    session_id = request.args.get('session', type=str) 
    user = select("""SELECT username, dino_id FROM users
    WHERE user_id = (SELECT user_id FROM sessions 
        WHERE uuid=%s);""", 
        (session_id,))
    return user, 200, {'Content-Type': 'application/json'}

@app.route('/delete-session', methods=['DELETE'])
def delete_session():
    data = request.json
    session_id = data["sessionId"]
    print(session_id)
    query = delete(
        """DELETE FROM sessions
        WHERE uuid=%s;""",
        (session_id,)
        )
    return {"status": query[0], "code": query[1]}