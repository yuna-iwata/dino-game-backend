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
        """SELECT (hashed_password) FROM users
        WHERE username = %s""",
        (username,)
        )
    entered_password = data["password"].encode('utf8')
    if len(query) > 0:
        hashed_password = query[0][0].encode('utf8')
    if len(query) == 0:
        return jsonify({"status": "No matching user found", "code": 404})
    elif bcrypt.checkpw(entered_password, hashed_password):
        return_data = {"match": True, "status": 'success', "code": 200}
        return jsonify(return_data)
    else:
        return_data = {"match": False, "status": 'Unauthorised', "code": 401}
        return jsonify(return_data)

@app.route('/delete-account', methods=['DELETE'])
def deleteAccount():
    data = request.json
    username = data["username"]
    query = delete(
        """DELETE FROM users
        WHERE username=%s""",
        (username,)
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
        return_data = {"match": False, "status": 'Unauthorised - incorrect password', "code": 401}
        return jsonify(return_data)