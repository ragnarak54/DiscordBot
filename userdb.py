import sqlite3
import psycopg2



def new_connection():
    conn = psycopg2.connect("dbname=userdb user=postgres")
    cursor = conn.cursor()

def test_connection():
    conn = psycopg2.connect("dbname=userdb user=postgres")
    cursor = conn.cursor()
    cursor.execute('select * from user_prefs')
    data = cursor.fetchall()
    print(data)
    cursor.close()
    conn.close()

def create_table():
    conn = psycopg2.connect("dbname=userdb user=postgres")
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS user_prefs(discordID TEXT, item TEXT)')
    cursor.close()
    conn.close()

def user_exists(user):
    conn = psycopg2.connect("dbname=userdb user=postgres")
    cursor = conn.cursor()
    cursor.execute('SELECT count(discordID) from user_prefs WHERE discordID = ?', (str(user),))
    data = cursor.fetchall()
    print(data)
    cursor.close()
    conn.close()
    return True

def new_user(userID):
    conn = psycopg2.connect("dbname=userdb user=postgres")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO user_prefs (discordID) VALUES (?)", (str(userID)))
    conn.commit()
    cursor.close()
    conn.close()

def new_pref(userID, item):
    conn = psycopg2.connect("dbname=userdb user=postgres")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO user_prefs (discordID, item) VALUES (?, ?)", (str(userID), str(item)))
    conn.commit()
    cursor.close()
    conn.close()

def remove_pref(userID, item):
    conn = psycopg2.connect("dbname=userdb user=postgres")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM user_prefs WHERE item = ?", (str(item),))
    conn.commit()
    cursor.close()
    conn.close()

def pref_exists(userID, item):
    conn = psycopg2.connect("dbname=userdb user=postgres")
    cursor = conn.cursor()
    cursor.execute("SELECT count(item) from user_prefs where discordID = ? and item = ?", (str(userID), str(item)))
    data = cursor.fetchall()
    print(data)
    return (data[0])[0] > 0
    cursor.close()
    conn.close()

def user_prefs(userID):
    conn = psycopg2.connect("dbname=userdb user=postgres")
    cursor = conn.cursor()
    cursor.execute("SELECT item FROM user_prefs WHERE discordID = ?", (str(userID),))
    return cursor.fetchall()
    cursor.close()
    conn.close()
