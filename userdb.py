import sqlite3
import psycopg2
import config



def new_connection():
    conn = psycopg2.connect("dbname={0} user={1} password={2} host={3}".format(config.mysql['db'], config.mysql['user'], config.mysql['passwd'], config.mysql['host']))
    cursor = conn.cursor()

def test_connection():
    conn = psycopg2.connect("dbname={0} user={1} password={2} host={3}".format(config.mysql['db'], config.mysql['user'], config.mysql['passwd'], config.mysql['host']))
    cursor = conn.cursor()
    cursor.execute("""select * from user_prefs""")
    data = cursor.fetchall()
    print(data)
    cursor.close()
    conn.close()

def create_table():
    try:
        conn = psycopg2.connect("dbname={0} user={1} password={2} host={3}".format(config.mysql['db'], config.mysql['user'], config.mysql['passwd'], config.mysql['host']))
        cursor = conn.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS user_prefs(discordID char(50), username char(50), item char(50))')
        cursor.close()
        conn.close()
        print("table successfully created")
    except Exception as e:
        print(e)

def user_exists(user):
    conn = psycopg2.connect("dbname={0} user={1} password={2} host={3}".format(config.mysql['db'], config.mysql['user'], config.mysql['passwd'], config.mysql['host']))
    cursor = conn.cursor()
    cursor.execute('SELECT count(discordID) from user_prefs WHERE discordID = ?', (str(user),))
    data = cursor.fetchall()
    print(data)
    cursor.close()
    conn.close()
    return True

def new_pref(userID, username, item):
    conn = psycopg2.connect("dbname={0} user={1} password={2} host={3}".format(config.mysql['db'], config.mysql['user'], config.mysql['passwd'], config.mysql['host']))
    cursor = conn.cursor()
    cursor.execute("INSERT INTO user_prefs (discordID, username, item) VALUES (%s, %s, %s)", (str(userID), str(username), str(item)))
    conn.commit()
    cursor.close()
    conn.close()

def remove_pref(userID, item):
    conn = psycopg2.connect("dbname={0} user={1} password={2} host={3}".format(config.mysql['db'], config.mysql['user'], config.mysql['passwd'], config.mysql['host']))
    cursor = conn.cursor()
    cursor.execute("DELETE FROM user_prefs WHERE item = %s AND discordID = %s", (str(item), str(userID)))
    conn.commit()
    cursor.close()
    conn.close()

def pref_exists(userID, item):
    conn = psycopg2.connect("dbname={0} user={1} password={2} host={3}".format(config.mysql['db'], config.mysql['user'], config.mysql['passwd'], config.mysql['host']))
    cursor = conn.cursor()
    cursor.execute("SELECT count(item) from user_prefs where discordID = %s and item = %s", (str(userID), str(item)))
    data = cursor.fetchall()
    print(data)
    return (data[0])[0] > 0
    cursor.close()
    conn.close()

def user_prefs(userID):
    conn = psycopg2.connect("dbname={0} user={1} password={2} host={3}".format(config.mysql['db'], config.mysql['user'], config.mysql['passwd'], config.mysql['host']))
    cursor = conn.cursor()
    cursor.execute("SELECT item FROM user_prefs WHERE discordID = %s", (str(userID),))
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

def users(item):
    conn = psycopg2.connect("dbname={0} user={1} password={2} host={3}".format(config.mysql['db'], config.mysql['user'],
                                                                               config.mysql['passwd'],
                                                                               config.mysql['host']))
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT discordID from user_prefs WHERE item = %s", (str(item),))
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

def user_server(username):
    conn = psycopg2.connect("dbname={0} user={1} password={2} host={3}".format(config.mysql['db'], config.mysql['user'],
                                                                               config.mysql['passwd'],
                                                                               config.mysql['host']))
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT server from user_prefs WHERE username = %s", (str(username),))
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    print(data[0])
    return (data[0])[0]
