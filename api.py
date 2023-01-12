from flask import Flask, request
from db_interactions import select, insert
import bcrypt
from flask import jsonify
from flask_cors import CORS

app = Flask(__name__)

CORS(app, origins=['http://localhost:3000', 'https://shiny-malabi-e40d14.netlify.app'], supports_credentials=True, with_credentials=True)

@app.route('/create-account', methods=['POST'])
def set_username_and_password():
    data = request.json
    username = data["username"]
    password = data["password"].encode('utf8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password, salt).decode('utf8')
    try:
        query = insert(
            """INSERT INTO users (username, hashed_password) 
            VALUES (%s, %s);""", 
            (username, hashed_password)
            )
        print(query)
        return {"status": query[0], "code": query[1]}
    except:
        return {"status": "Internal server error", "code": 500}


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
        return_data = {"match": False, "status": 'Unauthorised', "code": 400}
        return jsonify(return_data)