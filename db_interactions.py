import psycopg2
import psycopg2.extras as pse  # We'll need this to convert SQL responses into dictionaries

def get_db_connection():
  try:
    conn = psycopg2.connect("dbname=dzmxageo user=dzmxageo password=aXwhLXYi3XWyQiLf3cEid5qHuj4oU6eL host=rogue.db.elephantsql.com port=5432")
    return conn
  except:
    print("Error connecting to database")

def insert(query, params=()):
  try:
    conn = get_db_connection()
    with conn.cursor() as cur:
      cur.execute(query, params)
      conn.commit()
    return "Insert completed.", 200
  except:
    return "Error inserting data", 500

def select(query, params=()):
  # try:
    conn = get_db_connection()
    with conn.cursor() as cur:
      cur.execute(query, params)
      data = cur.fetchall()
      return data
  # except:
  #   return "Error selecting data", 500

def delete(query, params=()):
  try:
    conn = get_db_connection()
    with conn.cursor() as cur:
      cur.execute(query, params)
      conn.commit()
    return "Deletion completed.", 200
  except:
    return "Error deleting data", 500

def update(query, params=()):
  try:
    conn = get_db_connection()
    with conn.cursor() as cur:
      cur.execute(query, params)
      conn.commit()
    return "Update completed.", 200
  except:
    return "Error updating data", 500
