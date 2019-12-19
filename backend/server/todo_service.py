# -*- coding: utf-8 -*-
"""
Created on Fri Nov  8 09:45:39 2019

@author: lvi
"""

from flask import Flask, request, jsonify #, abort, flash, url_for, redirect
import secrets
import hashlib
import hmac
import binascii
import mysql.connector
from get_docker_secret import get_docker_secret

app = Flask(__name__)



def generate_salt_csprng(n=64):
    possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
    salt = ''.join(secrets.choice(possible) for i in range(n))
    return salt

def hash_string(key):
    key = str.encode(key)
    h = hashlib.sha256()
    h.update(key)
    return h.hexdigest()
    
#    return hashlib.sha256(str.encode(key)).hexdigest()

def generate_token(nbytes=64):
    return secrets.token_hex(nbytes)

def update_login_token(user_id):
    connection = db_connect()
    if (connection is None):
        return None
    
    login_token = None
    cursor = connection.cursor(prepared=True)
    try:
        new_login_token = generate_token(nbytes=32)
        cursor.execute("UPDATE users SET login_token=(%s) WHERE id=(%s)", (new_login_token, user_id))
        connection.commit()
        
        ## setup return data 
        cursor.execute("SELECT login_token FROM users WHERE id = %s", (user_id,))
        
        token_data = cursor.fetchone()
        if (token_data):
            login_token = token_data[0]

            
    except mysql.connector.Error as error:
        print("parameterized query failed {}".format(error))
        return None
        
    finally:
        if (connection.is_connected()):
            cursor.close()
            connection.close()
    
    return login_token

def sign_sha256(key, message):
    byte_key = binascii.unhexlify(key)
    message = message.encode()
    return hmac.new(byte_key, message, hashlib.sha256).hexdigest()

def make_rememberme_cookie(user_id, login_token):
    cookie = ':'.join([str(user_id), login_token])
    mac = sign_sha256(get_docker_secret('api_secret_key'), cookie)
    cookie = ':'.join([cookie, mac])
    return cookie

def get_login_token_expiration_seconds():
    return 60*10

def set_rememberme_cookie(response, cookie):
    response.set_cookie('_rememberme', cookie, max_age=get_login_token_expiration_seconds(), httponly=True)
    return response

 
cors_white_list = ['http://localhost:3000']
@app.after_request
def after_request(response): 
    req_origin = request.environ.get("HTTP_ORIGIN", "Unknown Origin")
    if req_origin in cors_white_list:
        response.headers.add('Access-Control-Allow-Origin', req_origin)
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Credentials', 'true')        # allow transmit of cookies etc
#        response.headers.add('Access-Control-Allow-Headers', 'Cache-Control')
#        response.headers.add('Access-Control-Allow-Headers', 'X-Requested-With')
#        response.headers.add('Access-Control-Allow-Headers', 'Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, DELETE, PATCH')
    return response




@app.route("/users", methods=["GET"]) # register
def get_users():
#    if request.headers['Content-Type'] != 'application/json' or request.headers['Content-Type'] != 'application/json;charset=UTF-8':
#        return jsonify({"Error": "Unexpected Content-Type header", "statusCode": 503, "statusMsg": "Content-Type header did not match required value 'application/json', was " + request.headers['Content-Type']})

    connection = db_connect()
    if (connection is None):
        return jsonify({"errMsg": "Could not connect to database"}), 503
    
    
    # todo: verify that the user querying is admin?
    
    users = []
    cursor = connection.cursor(prepared=True)
    try: 
        cursor.execute("SELECT id, username, first_name, last_name, role_desc FROM users JOIN user_role ON users.id = user_role.user_id JOIN roles ON user_role.role_id = roles.role_id;")
        
        db_users = cursor.fetchall()
        for user in db_users:
            user_id = user[0]
            user_username = user[1]
            user_fname = user[2]
            user_lname = user[3]
            user_role_desc = user[4]
            
            user = {"id": user_id, "username": user_username, "first_name": user_fname, "last_name": user_lname, "role_desc": user_role_desc}
            users.append(user)
            
        return jsonify({"users": users, "statusMsg": "Fetched all users"}), 200
            
    except mysql.connector.Error:
        return jsonify({"errMsg": "Database error"}), 502
        
    finally:
        if (connection.is_connected()):
            cursor.close()
            connection.close()
    
    return jsonify({"errMsg": "Something went wrong - unexpected error"}), 500


@app.route("/user", methods=["POST"]) # register
def create_user():
#    if request.headers['Content-Type'] != 'application/json' or request.headers['Content-Type'] != 'application/json;charset=UTF-8':
#        return jsonify({"Error": "Unexpected Content-Type header", "statusCode": 503, "statusMsg": "Content-Type header did not match required value 'application/json', was " + request.headers['Content-Type']})

    connection = db_connect()
    if (connection is None):
        return jsonify({"errMsg": "Could not connect to database"}), 503
    
    cursor = connection.cursor(prepared=True)
    try:
        query = """ INSERT INTO users (username, first_name, last_name, pw_hash, salt, login_token, pw_token) VALUES (%s, %s, %s, %s, %s, %s, %s) """
        req_data = request.get_json()
        user_username = req_data['username']
        user_fname = req_data['first_name']
        user_lname = req_data['last_name']
        user_pw = req_data['password']
        user_cpw = req_data['confirmPassword']
        
        cursor.execute("SELECT 1 FROM users WHERE username=(%s)", (user_username,))
        cursor.fetchall()
        
    
        if (cursor.rowcount > 0): return jsonify({"errMsg": "Username already in use"}), 409
        if user_pw != user_cpw: return jsonify({"errMsg": "Passwords did not match"}), 400
        
        salt = generate_salt_csprng()
        salted_password = user_pw + salt
        pw_hash = hash_string(salted_password)
        
        login_token = generate_token(32)
        pw_token = generate_token()
        
        cursor.execute(query, (user_username, user_fname, user_lname, pw_hash, salt, login_token, pw_token))
        connection.commit() 
        
        
        ## setup return data 
        cursor.execute("SELECT id, username, role_desc FROM users JOIN user_role ON users.id = user_role.user_id JOIN roles ON user_role.role_id = roles.role_id WHERE username = %s", (user_username,))
        keys = ("id", "username", "role_desc")
        user = dict(zip(keys, cursor.fetchone()))

        cookie = make_rememberme_cookie(user.get('id'), login_token)
        response = jsonify({"user": user, "statusMsg": "User created successfully"})
        response = set_rememberme_cookie(response, cookie)
        return response, 201
            
    except mysql.connector.Error:
        return jsonify({"errMsg": "Database error"}), 502
        
    finally:
        if (connection.is_connected()):
            cursor.close()
            connection.close()
    
    return jsonify({"errMsg": "Something went wrong - unexpected error"}), 500


@app.route("/user", methods=["DELETE"])
def delete_user():
    
    connection = db_connect()
    if (connection is None):
        return jsonify({"errMsg": "Could not connect to database"}), 503
    
    cursor = connection.cursor(prepared=True)
    try:
        req_data = request.get_json()
        if (req_data is None):
             return jsonify({"errMsg": "Invalid request"}), 401
         
        user_id = req_data['user_id']
        if (user_id is None):
            return jsonify({"errMsg": "Invalid request parameters"}), 401
        
        cursor.execute("DELETE FROM users WHERE id=%s", (user_id,))
        connection.commit() 
        
        return jsonify({"errMsg": "User successfully deleted"}), 200
            
    except mysql.connector.Error:
        return jsonify({"errMsg": "Database error"}), 502
        
    finally:
        if (connection.is_connected()):
            cursor.close()
            connection.close()
    
    return jsonify({"errMsg": "Something went wrong - unexpected error"}), 500


def validate_rememberme_cookie(cookie):
    try:
        user_id, login_token, mac = cookie.split(':')
    except: # token must have been tampered with
        return False
    
    if (sign_sha256(get_docker_secret('api_secret_key'), ':'.join([user_id, login_token])) != mac):
        return False
    
    connection = db_connect()
    if (connection is None):
        return False
    cursor = connection.cursor(prepared=True)
    
    try:
        cursor.execute("SELECT login_token FROM users WHERE id=(%s)", (user_id,))
        
        user_token = cursor.fetchone()
        if user_token is None:
            return False
        
        user_login_token = user_token[0]
        return user_login_token == login_token
        
        
    except mysql.connector.Error:
        return False
        
    finally:
        if (connection.is_connected()):
            cursor.close()
            connection.close()
    
def get_user_role(user_id):
    connection = db_connect()
    if (connection is None):
        return jsonify({"errMsg": "Could not connect to database"}), 503
    
    user_role = None
    cursor = connection.cursor(prepared=True)
    try: 
        cursor.execute("SELECT role_desc FROM users JOIN user_role ON users.id = user_role.user_id JOIN roles ON user_role.role_id = roles.role_id WHERE users.id=(%s)", (user_id,))
        user_role = cursor.fetchone()
        if (user_role): 
            user_role = user_role[0]
            
    except mysql.connector.Error:
        return jsonify({"errMsg": "Database error"}), 502
        
    finally:
        if (connection.is_connected()):
            cursor.close()
            connection.close()
    return user_role

@app.route("/login", methods=["POST"])
def login_user():
    if request.headers['Content-Type'] != 'application/json':
        return jsonify({"errMsg": "Content-Type header did not match required value 'application/json', was " + request.headers['Content-Type']}), 406
    
    connection = db_connect()
    if (connection is None):
        return jsonify({"errMsg": "Could not connect to database"}), 503
    
    auth_by_cookie = False
    if (request.cookies.get('_rememberme')):
        auth_by_cookie = validate_rememberme_cookie(request.cookies.get('_rememberme'))
        
        
    user = None
    cursor = connection.cursor(prepared=True)
    try:
        
        if (auth_by_cookie):
            user_id = request.cookies.get('_rememberme').split(':')[0]
            cursor.execute("SELECT username, role_desc FROM users JOIN user_role ON users.id = user_role.user_id JOIN roles ON user_role.role_id = roles.role_id WHERE users.id=(%s)", (user_id,))
            
            (username, role_desc) = cursor.fetchone()
            if (username):
                
                 ## store new login token with user 
                new_login_token = update_login_token(user_id)
                cookie = make_rememberme_cookie(user_id, new_login_token) if new_login_token else ''
                
                ## setup return data 
                keys = ("id", "username", "role_desc")
                values = (user_id, username, role_desc)
                user = dict(zip(keys, values))
            
                response = jsonify({"user": user, "statusMsg": "User logged in by cookie"})
                response = set_rememberme_cookie(response, cookie)
                return response, 200
            
            return jsonify({"errMsg": "User must have been deleted"}), 401
        
        else:
            req_data = request.get_json()
            username = req_data['username']       
            password = req_data['password']
            
            cursor.execute("SELECT id, salt, pw_hash FROM users WHERE username=(%s)", (username,))
            user_credentials = cursor.fetchone()
            if user_credentials is None:
                return jsonify({"errMsg": "User does not exist"}), 401
            
            user_id = user_credentials[0]
            user_salt = user_credentials[1]
            user_pw_hash = user_credentials[2]
    
            salted_password = password + user_salt
            pw_hash = hash_string(salted_password)
            
            if (pw_hash == user_pw_hash):
                ## login success
                
                ## store new login token with user 
                new_login_token = update_login_token(user_id)
                cookie = make_rememberme_cookie(user_id, new_login_token) if new_login_token else ''
                
                ## setup return data 
                keys = ("id", "username", "role_desc")
                values = (user_id, username, get_user_role(user_id))
                user = dict(zip(keys, values))
                
                response = jsonify({"user": user, "statusMsg": "User logged in"})
                response = set_rememberme_cookie(response, cookie)
                return response, 200
            
            else:
                return jsonify({"errMsg": "Invalid credentials"}), 401
        
    except mysql.connector.Error:
        return jsonify({"errMsg": "Database error"}), 502
        
    finally:
        if (connection.is_connected()):
            cursor.close()
            connection.close()
    
    return jsonify({"errMsg": "Something went wrong - unexpected error"}), 500



@app.route("/logout", methods=["POST"])
def logout_user():
    req_data = request.get_json()
    user_id = req_data['user_id']

    if (user_id is None): 
        return jsonify({"errMsg": "Cannot logout user"}), 401
    
    update_login_token(user_id) # change login token to make sure duplicates cant be used 
    response = jsonify({"statusMsg": "User logged out"})
    response.set_cookie('_rememberme', '')  # overwrite cookie to clear it
    return response, 200
    
@app.route("/todolists", methods=["POST"])
def insert_todolists():
    if request.headers['Content-Type'] != 'application/json':
        return jsonify({"errMsg": "Content-Type header did not match required value 'application/json', was " + request.headers['Content-Type']}), 406
    
    req_data = request.get_json()
   
    todos = [todo for todo in req_data['todo_lists']]
    
    connection = db_connect()
    if (connection is None):
        return jsonify({"errMsg": "Could not connect to database"}), 503
    
    cursor = connection.cursor(prepared=True)
    
    try:
        query = """ INSERT INTO todo_list (title, user_id) VALUES (%s, %s) """
        
        for todo in todos:
            cursor.execute(query, (todo['title'], todo['user_id']))
            connection.commit()
        
        ## Now insert all todo items under the new todo list (reference the todo list id of the newly created todo list)
        for todo in todos:
            cursor.execute(""" SELECT id FROM todo_list WHERE title=(%s) ORDER BY id DESC LIMIT 1 """, (todo['title'],))
            todolist_id = cursor.fetchall()[0][0]   # fetchall()[0] returns the row as a tuple '(id,)'
            ## insert todo items referencing this todo list
            for item in todo['todo_items']:
                cursor.execute(""" INSERT INTO todo_item (label, completed, due_date, todolist_id) VALUES (%s,%s,%s) """, (item['label'], item['completed'], item['due_date'], todolist_id))
            
        connection.commit()
        return jsonify({"statusMsg": "Inserts were successful"}), 201
         
    except mysql.connector.Error:
        return jsonify({"errMsg": "Database error"}), 502
        
    finally:
        if (connection.is_connected()):
            cursor.close()
            connection.close()
            
    return jsonify({"errMsg": "Something went wrong - unexpected error"}), 500
    


@app.route("/todolists", methods=["GET"])
#@login_required
def get_todolists():
    connection = db_connect()
    todo_lists = []
    try:
        user_id = request.args.get('user_id')
        
        cursor = connection.cursor()
        cursor.execute("SELECT id, title, user_id FROM todo_list WHERE user_id = %s", (user_id,))
        todolists = cursor.fetchall()
        for todolist in todolists:
            list_id = todolist[0]
            list_title = todolist[1]
            
            cursor.execute(""" SELECT * FROM todo_item WHERE todolist_id=(%s) """, (list_id,))
            todo_items = [{"id": item_id, "label": label, "completed": completed, "due_date": due_date, "priority": priority} for (item_id, label, completed, due_date, priority, todolist_id) in cursor]
            todo_lists.append({"id": list_id, "title": list_title, "todo_items": todo_items})
        
        return jsonify({"todo_lists": todo_lists, "statusMsg": "Successfully fetched todo lists belonging to user"}), 200
             
    except mysql.connector.Error:
        return jsonify({"errMsg": "Database error"}), 502
        
    finally:
        if (connection.is_connected()):
            cursor.close()
            connection.close()
        
    return jsonify({"errMsg": "Something went wrong - unexpected error"}), 500
        
@app.route("/todolist", methods=["POST"])
def insert_todolist():
    connection = db_connect()
    if (connection is None):
        return jsonify({"errMsg": "Could not connect to database"}), 503
    
    todo_list = None
    cursor = connection.cursor(prepared=True)
    try:
        query = """ INSERT INTO todo_list (title, user_id) VALUES (%s, %s) """
    
        req_data = request.get_json()
        todolist_title = req_data['title']
        todolist_user_id = req_data['user_id']
        
        cursor.execute(query, (todolist_title, todolist_user_id))
        connection.commit()
        
        ## setup return data 
        cursor.execute("SELECT id, title, user_id FROM todo_list WHERE id = LAST_INSERT_ID()")
        keys = ("id", "title", "user_id")
        todo_list = dict(zip(keys, cursor.fetchone()))
        return jsonify({"todo_list": todo_list, "statusMsg": "New todolist inserted"}), 201

    except mysql.connector.Error:
        return jsonify({"errMsg": "Database error"}), 502
        
    finally:
        if (connection.is_connected()):
            cursor.close()
            connection.close()
            
    return jsonify({"errMsg": "Something went wrong - unexpected error"}), 500


@app.route("/todo", methods=["PATCH"])
def update_todo(): # change completed
    connection = db_connect()
    if (connection is None):
        return jsonify({"errMsg": "Could not connect to database"}), 503
    
    todo = None
    cursor = connection.cursor(prepared=True)
    try:
        query = """ UPDATE todo_item SET completed=(%s), due_date=(%s), priority=(%s) WHERE id=(%s) """
        
        req_data = request.get_json()
        todo_completed = req_data['completed']
        todo_duedate = req_data['due_date']
        todo_id = req_data['id']
        todo_priority = req_data['priority']
        
        cursor.execute(query, (todo_completed, todo_duedate, todo_priority, todo_id))
        connection.commit()
        
        ## setup return data 
        cursor.execute("SELECT id, label, completed, due_date, priority, todolist_id FROM todo_item WHERE id = %s", (todo_id,))
        keys = ("id", "label", "completed", "due_date", "priority", "todolist_id")
        todo = dict(zip(keys, cursor.fetchone()))
        return jsonify({"todo": todo, "statusMsg": "Updated todo item"}), 200
    
    except mysql.connector.Error:
        return jsonify({"errMsg": "Database error"}), 502
        
    finally:
        if (connection.is_connected()):
            cursor.close()
            connection.close()
            
    return jsonify({"errMsg": "Something went wrong - unexpected error"}), 500


@app.route("/todos/completed", methods=["PATCH"])
def clear_completed_todos(): 
    connection = db_connect()
    if (connection is None):
        return jsonify({"errMsg": "Could not connect to database"}), 503
    
    
    cursor = connection.cursor()
    try:
        req_data = request.get_json()
        todolist_id = req_data['todolist_id']
        
        cursor.callproc('delete_completed', [todolist_id])
        connection.commit()
            
        return jsonify({"statusMsg": "Cleared all completed todos from todolist with id: " + str(todolist_id)}), 200

    except mysql.connector.Error:
        return jsonify({"errMsg": "Database error"}), 502
        
    finally:
        if (connection.is_connected()):
            cursor.close()
            connection.close()
    
    return jsonify({"errMsg": "Something went wrong - unexpected error"}), 500
    
    
@app.route("/todo", methods=["DELETE"])
def delete_todo(): 
    connection = db_connect()
    if (connection is None):
        return jsonify({"errMsg": "Could not connect to database"}), 503
    
    cursor = connection.cursor(prepared=True)
    try:
        query = """ DELETE FROM todo_item WHERE id=(%s) """        
        
        req_data = request.get_json()
        todo_id = req_data['id']
        
        cursor.execute(query, (todo_id,))
        connection.commit()
        
        return jsonify({"statusMsg": "Todo deleted successfully"}), 200

    except mysql.connector.Error:
        return jsonify({"errMsg": "Database error"}), 502
        
    finally:
        if (connection.is_connected()):
            cursor.close()
            connection.close()
    
    return jsonify({"errMsg": "Something went wrong - unexpected error"}), 500

@app.route("/todo", methods=["POST"])
def insert_todo(): 
    connection = db_connect()
    if (connection is None):
        return jsonify({"errMsg": "Could not connect to database"}), 503
    
    cursor = connection.cursor(prepared=True)
    
    todo = None
    try:
        query = """ INSERT INTO todo_item (label, completed, due_date, priority, todolist_id) VALUES (%s, %s, %s, %s, %s) """
        
        req_data = request.get_json()
        todo_label = req_data['label']
        todo_completed = req_data['completed']
        todo_duedate = req_data['due_date']
        todo_priority = req_data['priority']
        todo_list_id = req_data['todolist_id']
        
        cursor.execute(query, (todo_label, todo_completed, todo_duedate, todo_priority, todo_list_id))
        connection.commit()
        
        ## setup return data 
        cursor.execute("SELECT * FROM todo_item WHERE id = LAST_INSERT_ID()")
        keys = ("id", "label", "completed", "due_date", "priority", "todolist_id")
        todo = dict(zip(keys, cursor.fetchone()))
        return jsonify({"todo": todo, "statusMsg": "Todo inserted successfully"}), 201

            
    except mysql.connector.Error:
        return jsonify({"errMsg": "Database error"}), 502
        
    finally:
        if (connection.is_connected()):
            cursor.close()
            connection.close()
            
    return jsonify({"errMsg": "Something went wrong - unexpected error"}), 500
        

@app.route("/todos", methods=["GET"])
def get_todos(): 
    connection = db_connect()
    todo_items = []
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM todo_item")
        todo_items = [{"id": item_id, "label": label, "completed": completed, "due_date": due_date, "priority": priority, "todolist_id": todolist_id} for (item_id, label, completed, due_date, priority, todolist_id) in cursor]
        return jsonify({'todo_items': todo_items, "statusMsg": "Successfully fetched todo items"}), 200
    
    except mysql.connector.Error:
        return jsonify({"errMsg": "Database error"}), 502
        
    finally:
        if (connection.is_connected()):
            cursor.close()
            connection.close()
        
    return jsonify({"errMsg": "Something went wrong - unexpected error"}), 500


def db_connect(host='db', db='todos', user='root', password=get_docker_secret('db_root_password')):
    connection = None
    try:
        connection = mysql.connector.connect(host=host,
                                             database=db,
                                             user=user,
                                             password=password)
    except:
        print("Could not connect to specified host with the given information")
        
    finally:
        return connection
    
if __name__ == '__main__':
#      app.config['SECRET_KEY'] = "NS8V26K7aRTP5wDXwVxkR4iBy1oEiNud"
      app.run(host="0.0.0.0", port=int("5000"))
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      