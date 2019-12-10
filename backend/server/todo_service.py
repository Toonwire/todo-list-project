# -*- coding: utf-8 -*-
"""
Created on Fri Nov  8 09:45:39 2019

@author: lvi
"""

from flask import Flask, request, jsonify #, abort, flash, url_for, redirect
import secrets
import hashlib

import mysql.connector

app = Flask(__name__)



def generate_salt_csprng():
    possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
    salt = ''.join(secrets.choice(possible) for i in range(64))
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
    connection = connect('db', 'todos', 'root', 'rootroot')
    if (connection is None):
        return None
    
    login_token = None
    cursor = connection.cursor(prepared=True)
    try:
        new_login_token = generate_token()
        cursor.execute("UPDATE users SET login_token=(%s) WHERE id=(%s)", (new_login_token, user_id))
        connection.commit()
        
        ## setup return data 
        cursor.execute("SELECT login_token FROM users WHERE id = %s", (user_id,))
        login_token = cursor.fetchone()[0]

            
    except mysql.connector.Error as error:
        return "parameterized query failed {}".format(error)
        
    finally:
        if (connection.is_connected()):
            cursor.close()
            connection.close()
            print("Connection closed")
    
    return login_token
    
#    
#def login_required(protected_function):
#    @wraps(protected_function)
#    def wrapper (*args, **kwargs):
#        encoded_session_id = request.cookies.get('_session_id')
#        print(request)
#        if encoded_session_id:
#            connection = connect('db', 'todos', 'root', 'rootroot')
#            if (connection is None):
#                return jsonify({"Error": "Could not connect to database", "statusCode": 503, "statusMsg": "Incorrect db credentials or schema does not exist"})
#            
#            user_id = None
#            try:
#                payload = jwt.decode(encoded_session_id, app.config['SECRET_KEY'], algorithm='HS256')          
#                
#                cursor = connection.cursor(prepared=True)
#                cursor.execute("SELECT id FROM users WHERE username=(%s)", (user_username,))
#                
#                if user_id:
#                    return protected_function(*args, **kwargs)
#                
#                else: 
#                    flash("Session exists, but no user has that session (deleted)")
#                    return redirect(url_for('login'))
#                    
#
#            except jwt.InvalidSignatureError:
#                response = jsonify({"Error": "Invalid signature", "statusCode": 401})
#                abort(401, response)
#                
#            except Exception as e:
#                return abort(402, jsonify({"Error": e, "statusCode": 401}))
#            
#            finally:
#                if (connection.is_connected()):
#                    cursor.close()
#                    connection.close()
#                    print("Connection closed")
#        else:
#            flash("No session, please log in")
#            return redirect(url_for('login'))
#    return wrapper
        
cors_white_list = ['http://localhost:3000']
@app.after_request
def after_request(response): 
    req_origin = request.environ.get("HTTP_ORIGIN", "Unknown Origin")
    if req_origin in cors_white_list:
        response.headers.add('Access-Control-Allow-Origin', req_origin)
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
#        response.headers.add('Access-Control-Allow-Credentials', 'true')
#        response.headers.add('Access-Control-Allow-Headers', 'Cache-Control')
#        response.headers.add('Access-Control-Allow-Headers', 'X-Requested-With')
#        response.headers.add('Access-Control-Allow-Headers', 'Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, DELETE, PATCH')
    return response

@app.route("/user", methods=["POST"]) # register
def create_user():
#    if request.headers['Content-Type'] != 'application/json' or request.headers['Content-Type'] != 'application/json;charset=UTF-8':
#        return jsonify({"Error": "Unexpected Content-Type header", "statusCode": 503, "statusMsg": "Content-Type header did not match required value 'application/json', was " + request.headers['Content-Type']})

    connection = connect('db', 'todos', 'root', 'rootroot')
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
        
        login_token = generate_token()
        pw_token = generate_token()
        
#        session_id = jwt.encode({'user_username': user_username}, app.config['SECRET_KEY'], algorithm='HS256')
        
        cursor.execute(query, (user_username, user_fname, user_lname, pw_hash, salt, login_token, pw_token))
        connection.commit() 
        
        
        ## setup return data 
        cursor.execute("SELECT id, username FROM users WHERE username = %s", (user_username,))
        keys = ("id", "username")
        user = dict(zip(keys, cursor.fetchone()))
        
        return jsonify({"user": user, "statusMsg": "User created successfully"}), 201
#        response.set_cookie('_session_id', session_id, httponly=True)
            
    except mysql.connector.Error:
        return jsonify({"errMsg": "Database error"}), 502
        
    finally:
        if (connection.is_connected()):
            cursor.close()
            connection.close()
            print("Connection closed")
    
    return jsonify({"errMsg": "Something went wrong - unexpected error"}), 500


@app.route("/login", methods=["POST"])
def login_user():
    if request.headers['Content-Type'] != 'application/json':
        return jsonify({"errMsg": "Content-Type header did not match required value 'application/json', was " + request.headers['Content-Type']}), 406
    
    connection = connect('db', 'todos', 'root', 'rootroot')
    if (connection is None):
        return jsonify({"errMsg": "Could not connect to database"}), 503
    
    user = None
    cursor = connection.cursor(prepared=True)
    try:
        req_data = request.get_json()
        username = req_data['username']       
        password = req_data['password']
        
        cursor.execute("SELECT id, salt, pw_hash FROM users WHERE username=(%s)", (username,))
        user_credentials = cursor.fetchone()
        if user_credentials is None:
            return jsonify({"errMsg": "User not found"}), 404
        
        user_id = user_credentials[0]
        user_salt = user_credentials[1]
        user_pw_hash = user_credentials[2]

        salted_password = password + user_salt
        pw_hash = hash_string(salted_password)
        
        if (pw_hash == user_pw_hash):
            ## login success
            ## setup return data 
            keys = ("id", "username")
            values = (user_id, username)
            user = dict(zip(keys, values))
            return jsonify({"user": user, "statusMsg": "User logged in"}), 200
            
    except mysql.connector.Error:
        return jsonify({"errMsg": "Database error"}), 502
        
    finally:
        if (connection.is_connected()):
            cursor.close()
            connection.close()
            print("Connection closed")
    
    return jsonify({"errMsg": "Something went wrong - unexpected error"}), 500
#    print(request.cookies.get('_session_id'))
#    if not request.cookies.get('_session_id'):
#        response.set_cookie('_session_id', jwt.encode({'user_username': user_username}, app.config['SECRET_KEY'], algorithm='HS256'))
    



#@app.route("/login/token", methods=["POST"])
#def login_user_with_token():
#    if request.headers['Content-Type'] != 'application/json':
#        return jsonify({"Error": "Unexpected Content-Type header", "statusCode": 503, "statusMsg": "Content-Type header did not match required value 'application/json', was " + request.headers['Content-Type']})
#    
#    connection = connect('db', 'todos', 'root', 'rootroot')
#    if (connection is None):
#        return jsonify({"Error": "Could not connect to database", "statusCode": 503, "statusMsg": "Incorrect credentials or schema does not exist"})
#    
#    user = None
#    cursor = connection.cursor(prepared=True)
#    try:
#        req_data = request.get_json()
#        token = req_data['login_token']  
#        
#        cursor.execute("SELECT id, username FROM users WHERE login_token=(%s)", (token,))
#        user_credentials = cursor.fetchone()
#        user_id = user_credentials[0]
#        user_username = user_credentials[1]
#        if not user_id: 
#            response = jsonify({"Error": "Invalid token", "statusCode": 401, "statusMsg": "User is not registered"})
#            abort(401, response)
#
#     
#        ## setup return data 
#        keys = ("id", "username", "login_token")
#        values = (user_id, user_username, token)
#        user = dict(zip(keys, values))
#
#            
#    except mysql.connector.Error:
#        return jsonify({"Error": "SQL failed", "statusCode": 503, "statusMsg": "Something went wrong trying to call database"})
#        
#    finally:
#        if (connection.is_connected()):
#            cursor.close()
#            connection.close()
#            print("Connection closed")
#    
#    response = jsonify({"user": user, "statusCode": 200, "statusMsg": "User logged in"})
#    return response

    
@app.route("/todolists", methods=["POST"])
def insert_todolists():
    if request.headers['Content-Type'] != 'application/json':
        return jsonify({"errMsg": "Content-Type header did not match required value 'application/json', was " + request.headers['Content-Type']}), 406
    
    req_data = request.get_json()
   
    todos = [todo for todo in req_data['todo_lists']]
    
    connection = connect('db', 'todos', 'root', 'rootroot')
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
    connection = connect('db', 'todos', 'root', 'rootroot')
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
            todo_items = [{"id": item_id, "label": label, "completed": completed, "due_date": due_date} for (item_id, label, completed, due_date, todolist_id) in cursor]
            todo_lists.append({"id": list_id, "title": list_title, "todo_items": todo_items})
        
        return jsonify({"todo_lists": todo_lists, "statusMsg": "Successfully fetched todo lists belonging to user"}), 200
             
    except mysql.connector.Error:
        return jsonify({"errMsg": "Database error"}), 502
        
    finally:
        if (connection.is_connected()):
            cursor.close()
            connection.close()
            print("Connection closed")
        
    return jsonify({"errMsg": "Something went wrong - unexpected error"}), 500
        
@app.route("/todolist", methods=["POST"])
def insert_todolist():
    connection = connect('db', 'todos', 'root', 'rootroot')
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
            print("Connection closed")
            
    return jsonify({"errMsg": "Something went wrong - unexpected error"}), 500


@app.route("/todo", methods=["PATCH"])
def update_todo(): # change completed
    connection = connect('db', 'todos', 'root', 'rootroot')
    if (connection is None):
        return jsonify({"errMsg": "Could not connect to database"}), 503
    
    todo = None
    cursor = connection.cursor(prepared=True)
    try:
        query = """ UPDATE todo_item SET completed=(%s), due_date=(%s) WHERE id=(%s) """
        
        req_data = request.get_json()
        todo_completed = req_data['completed']
        todo_duedate = req_data['due_date']
        todo_id = req_data['id']
        
        cursor.execute(query, (todo_completed, todo_duedate, todo_id))
        connection.commit()
        
        ## setup return data 
        cursor.execute("SELECT id, label, completed, due_date, todolist_id FROM todo_item WHERE id = %s", (todo_id,))
        keys = ("id", "label", "completed", "due_date", "todolist_id")
        todo = dict(zip(keys, cursor.fetchone()))
        return jsonify({"todo": todo, "statusMsg": "Updated todo item"}), 200

            
    except mysql.connector.Error:
        return jsonify({"errMsg": "Database error"}), 502
        
    finally:
        if (connection.is_connected()):
            cursor.close()
            connection.close()
            print("Connection closed")
            
    return jsonify({"errMsg": "Something went wrong - unexpected error"}), 500


@app.route("/todos/completed", methods=["PATCH"])
def clear_completed_todos(): 
    connection = connect('db', 'todos', 'root', 'rootroot')
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
            print("Connection closed")
    
    return jsonify({"errMsg": "Something went wrong - unexpected error"}), 500
    
    
@app.route("/todo", methods=["DELETE"])
def delete_todo(): 
    connection = connect('db', 'todos', 'root', 'rootroot')
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
            print("Connection closed")
    
    return jsonify({"errMsg": "Something went wrong - unexpected error"}), 500

@app.route("/todo", methods=["POST"])
def insert_todo(): 
    connection = connect('db', 'todos', 'root', 'rootroot')
    if (connection is None):
        return jsonify({"errMsg": "Could not connect to database"}), 503
    
    cursor = connection.cursor(prepared=True)
    
    todo = None
    try:
        query = """ INSERT INTO todo_item (label, completed, due_date, todolist_id) VALUES (%s, %s, %s, %s) """
        
        req_data = request.get_json()
        todo_label = req_data['label']
        todo_completed = req_data['completed']
        todo_duedate = req_data['due_date']
        todo_list_id = req_data['todolist_id']
        
        cursor.execute(query, (todo_label, todo_completed, todo_duedate, todo_list_id))
        connection.commit()
        
        ## setup return data 
        cursor.execute("SELECT * FROM todo_item WHERE id = LAST_INSERT_ID()")
        keys = ("id", "label", "completed", "due_date", "todolist_id")
        todo = dict(zip(keys, cursor.fetchone()))
        return jsonify({"todo": todo, "statusMsg": "Todo inserted successfully"}), 201

            
    except mysql.connector.Error:
        return jsonify({"errMsg": "Database error"}), 502
        
    finally:
        if (connection.is_connected()):
            cursor.close()
            connection.close()
            print("Connection closed")
            
    return jsonify({"errMsg": "Something went wrong - unexpected error"}), 500
        

@app.route("/todos", methods=["GET"])
def get_todos(): 
    connection = connect('db', 'todos', 'root', 'rootroot')
    todo_items = []
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM todo_item")
        todo_items = [{"id": item_id, "label": label, "completed": completed, "due_date": due_date, "todolist_id": todolist_id} for (item_id, label, completed, due_date, todolist_id) in cursor]
        return jsonify({'todo_items': todo_items, "statusMsg": "Successfully fetched todo items"}), 200
    
    except mysql.connector.Error:
        return jsonify({"errMsg": "Database error"}), 502
        
    finally:
        if (connection.is_connected()):
            cursor.close()
            connection.close()
            print("Connection closed")
        
    return jsonify({"errMsg": "Something went wrong - unexpected error"}), 500

    
def connect(host='db', db='todos', user='root', password='rootroot'):
    connection = None
    try:
        connection = mysql.connector.connect(host=host,
                                             database=db,
                                             user=user,
                                             password=password)
        print("Connection succeeded")
    except:
        print("Could not connection to specified host with the given information")
        
    finally:
        return connection
    
if __name__ == '__main__':
#      app.config['SECRET_KEY'] = "NS8V26K7aRTP5wDXwVxkR4iBy1oEiNud"
      app.run(host="0.0.0.0", port=int("5000"))
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      