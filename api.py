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
    WHERE username = %s""",(username,))
    formatted_data = []
    for i in range(len(data)):
        each_score = {'score': data[i][0], 'date': data[i][1] }
        formatted_data.append(each_score)
    return formatted_data, 200, {'Content-Type': 'application/json'}

@app.route('/global-leaderboard', methods=['GET'])
def get_global_leaderboard():
    data = select("""SELECT users.user_id, username,score, date, users.dino_id
    FROM scores JOIN users ON users.user_id = scores.user_id
    ORDER BY user_id, score DESC, date;""")
    formatted_data = []
    for i in range(len(data)):
        each_score = {'name': data[i][1], 'score': data[i][2], 'date': data[i][3], 'dino_id': data[i][4]}
        formatted_data.append(each_score)
    return formatted_data, 200, {'Content-Type': 'application/json'}

@app.route('/submit-score', methods=['POST'])
def submit_score():
    data = request.json
    username = data["username"]
    score = data["score"]
    user_id = select("SELECT user_id FROM users WHERE username = %s", (username,))
    format_user_id = user_id[0][0]
    query = insert(
        """INSERT INTO scores (user_id, score, date) 
        VALUES (%s, %s, current_timestamp);""", 
        (format_user_id,score))
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
def deleteAccount():
    data = request.json
    username = data["username"]
    query = delete(
        """DELETE FROM scores
        WHERE user_id = (SELECT user_id FROM users WHERE username=%s);

        DELETE FROM users
        WHERE username=%s""",
        (username, username)
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


