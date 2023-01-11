import psycopg2
import psycopg2.extras as pse  # We'll need this to convert SQL responses into dictionaries
from flask import Flask, current_app, request, jsonify
from flask_cors import CORS

app=Flask(__name__)
CORS(app)

def get_db_connection():
    try:
        conn = psycopg2.connect("dbname=czreijar user=czreijar password=TJ2StTuQIl2CoRoinQTwPxk8pBGfdf6t host=kandula.db.elephantsql.com port=5432")
        return conn
    except:
        print('Error Connecting to Database')

conn = get_db_connection()

def db_select(query, parameters=()):
    if conn != None:
        with conn.cursor(cursor_factory=pse.RealDictCursor) as cur:
            try:
                print(parameters)
                cur.execute(query, parameters)
                data = cur.fetchall()
                return data       
            except:
               return "Error executing query.", 404
    else:
        return "No connection"

@app.route("/", methods=['GET'])
def index():
    return 'Countries Application'

@app.route("/countries/<string:name>", methods=['GET'])
def get_countries(name):
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=pse.RealDictCursor)

        cur.execute("SELECT * from countries WHERE shortname= %s", [name])

        countries_data = cur.fetchall()
        cur.close()

        if (len(countries_data)<1):
            return 'No Country Found with such name', 404
        else:
            return countries_data, 200, {'Content-Type': 'application/json'}

    except:
        return 'Failed to fetch Data', 404

@app.route("/countries/<string:name>/<string:indicator>/<int:year>", methods=['GET'])
def get_indicator_for_year(name, indicator, year):
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=pse.RealDictCursor)

        cur.execute("SELECT * from indicators WHERE countryname= %s AND LOWER(indicatorname)=LOWER(%s) AND year=%s", [name,indicator, year])

        indicator_data = cur.fetchall()
        cur.close()

        if (len(indicator_data)<1):
            return 'No Country Found with such name', 404
        else:
            return indicator_data, 200, {'Content-Type': 'application/json'}

    except:
        return 'Failed to fetch Data', 404


@app.route("/countries", methods=["GET"])
def search_countries():
    result_name = request.args.get('name', type=str) 
    result_indicator = request.args.get('indicator', type=str) 
    result_year = request.args.get('year', type=str) 
    name_params = result_name.split(',')
    countries_of_name = []
    for item in name_params:
        param = [item,result_indicator,result_year]
        query = "SELECT * from indicators WHERE LOWER(countryname)= %s AND LOWER(indicatorname)=LOWER(%s) AND year=%s"
        data = db_select(query,(param))
        countries_of_name.append(data)
    if len(countries_of_name[0])>0:
        return countries_of_name
    else: 
        return 'No Country Found with such name', 404
        





@app.route("/countries", methods=["GET"])
def search_country():
    result = request.args.get('name', type=str) 
    params = result.split(',')
    countries_of_name = []
    print(params)
    for item in params:
        param = item
        query = "SELECT * from countries WHERE LOWER(shortname)= %s"
        data = db_select(query,(param,))
        countries_of_name.append(data)
    if len(countries_of_name[0])>0:
        return countries_of_name
    else: 
        return 'No Country Found with such name', 404




@app.route("/countries/indicators", methods=['GET'])
def get_list_of_indicators():

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT DISTINCT indicatorname from indicators")
        indicators = cur.fetchall()
        cur.close()

        return indicators, 200
    except:
        return 'Failed to fetch Data', 404


@app.route("/countries/allnames", methods=['GET'])
def get_list_of_country_shortnames():

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT shortname from countries")
        countries = cur.fetchall()
        cur.close()

        return countries, 200

    except:
        return 'Failed to fetch Data', 404



    