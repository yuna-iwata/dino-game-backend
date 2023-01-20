# 🦖Dino game Flask API🦖

- An api for mediating requests for the dinosaur game at https://github.com/yuna-iwata/dino-frontend-v2. 
- View the running API here: https://the-dino-game-api.herokuapp.com/

## Running the app

Preferably, first create a virtualenv and activate it, perhaps with the following command:

```
python3 -m venv venv
source ./venv/bin/activate
```

Next, run

```
pip3 install -r requirements.txt
```

Finally run the app with

```
export FLASK_APP=app.py
flask run
```
Rest Api 
-----

#### Test Api: 
to ensure the api is up and running: should display the text 'Dino' 

GET - test: (http://localhost:5000/)

#### Users Api:

POST - set_username_and_password: (http://localhost:5000/create-account) + body containing username and password

POST - check_username_and_password: (http://localhost:5000/login) + body containing username and password

POST - change_password: (http://localhost:5000/delete-account) + body containing username, oldPassword and newPassword

POST - change_username: (http://localhost:5000/change-password) + body containing oldUsername, newUsername and password

POST - change_avatar: (http://localhost:5000/change-username) + body containing username and newAvatar

DELETE - delete_account: (http://localhost:5000/change-avatar) + body containing username

#### Leaderboard Api:

GET - get_personal_leaderboard: (http://localhost:5000/personal-leaderboard)

GET - get_global_leaderboard: (http://localhost:5000/global-leaderboard)

POST - submit_score: (http://localhost:5000/submit-score) + body containing username and score
