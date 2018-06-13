import psycopg2
import config

# test function called at the start f the program to see if the DB connection is successful
def create_table():
    try:
        conn = psycopg2.connect("dbname={0} user={1} password={2} host={3}".format(config.mysql['db'], config.mysql['user'], config.mysql['passwd'], config.mysql['host']))
        cursor = conn.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS user_prefs(discordID char(50), username char(50), item char(50))')
        cursor.close()
        conn.close()
        print("DB connection successful")
    except Exception as e:
        print(e)

def new_pref(userID, username, item, server):
    conn = psycopg2.connect("dbname={0} user={1} password={2} host={3}".format(config.mysql['db'], config.mysql['user'], config.mysql['passwd'], config.mysql['host']))
    cursor = conn.cursor()
    cursor.execute("INSERT INTO user_prefs (discordID, username, item, server) VALUES (%s, %s, %s, %s)", (str(userID), str(username), str(item), str(server)))
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

# returns if an item is in a user's notify list
def pref_exists(userID, item):
    conn = psycopg2.connect("dbname={0} user={1} password={2} host={3}".format(config.mysql['db'], config.mysql['user'], config.mysql['passwd'], config.mysql['host']))
    cursor = conn.cursor()
    cursor.execute("SELECT count(item) from user_prefs where discordID = %s and item = %s", (str(userID), str(item)))
    data = cursor.fetchall()
    print(data)
    cursor.close()
    conn.close()
    return (data[0])[0] > 0


# returns the list of preferences for a user
def user_prefs(userID):
    conn = psycopg2.connect("dbname={0} user={1} password={2} host={3}".format(config.mysql['db'], config.mysql['user'], config.mysql['passwd'], config.mysql['host']))
    cursor = conn.cursor()
    cursor.execute("SELECT item FROM user_prefs WHERE discordID = %s", (str(userID),))
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

# returns the list of users for an item
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

# gets the server that a user is in
def user_server(discordID):
    conn = psycopg2.connect("dbname={0} user={1} password={2} host={3}".format(config.mysql['db'], config.mysql['user'],
                                                                               config.mysql['passwd'],
                                                                               config.mysql['host']))
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT server from user_prefs WHERE discordID = %s", (str(discordID),))
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    print(data[0])
    return (data[0])[0].strip()

def user_exists(discordID):
    conn = psycopg2.connect("dbname={0} user={1} password={2} host={3}".format(config.mysql['db'], config.mysql['user'],
                                                                               config.mysql['passwd'],
                                                                               config.mysql['host']))
    cursor = conn.cursor()
    cursor.execute("SELECT count(discordID) from user_prefs WHERE discordID = %s", (str(discordID),))
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return (data[0])[0] > 0

# gets the id for the AH discord role for an item
def ah_roles(items):
    conn = psycopg2.connect("dbname={0} user={1} password={2} host={3}".format(config.mysql['db'], config.mysql['user'],
                                                                               config.mysql['passwd'],
                                                                               config.mysql['host']))
    cursor = conn.cursor()
    cursor.execute("SELECT role from ah_roles where (item = %s or item = %s or item = %s)", (str(items[1]).lower(), str(items[2]).lower(), str(items[3]).lower()))
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

def authorize_user(server, user):
    conn = psycopg2.connect("dbname={0} user={1} password={2} host={3}".format(config.mysql['db'], config.mysql['user'],
                                                                               config.mysql['passwd'],
                                                                               config.mysql['host']))
    cursor = conn.cursor()
    cursor.execute("INSERT INTO authorized_users (sever, username) values (%s, %s)", (str(server), str(user)))
    cursor.close()
    conn.close()
