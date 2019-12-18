CREATE DATABASE todos;
use todos;

CREATE TABLE users (
	id INT PRIMARY KEY AUTO_INCREMENT,
	username VARCHAR(255) NOT NULL,
	first_name VARCHAR(255),
	last_name VARCHAR(255),
	pw_hash VARCHAR(255),
	salt VARCHAR(255),
	login_token VARCHAR(255),
	pw_token VARCHAR(255)
);

INSERT INTO users
	(username, first_name, last_name, pw_hash, salt, login_token, pw_token)
VALUES
	('admin', 'ad', 'min', '1232bfc5986e8c63a3e150ab4744bdda6bd45c1fe42afdfff2d885a5e0ccdea4', 'LQlsQuGmV426uiO4SAwO5P0jQpMIxuu-tTakqhiBVumATlRWIlev8i-JmWFwt6xK', NULL, '05808b62f0c7c89f284b6ccc75c7519f2bc5a421a6013f8773b6827b7e82cf7ef8d7f592947b0225ec35bf91174128201c34d9895853eea442eef6186bbf561b');



CREATE TABLE roles (
	role_id INT PRIMARY KEY AUTO_INCREMENT,
	role_desc varchar(25) NOT NULL
);

INSERT INTO roles
	(role_desc)
VALUES
	('Admin'),
	('User');



CREATE TABLE user_role (
	user_id INT NOT NULL,
	role_id INT DEFAULT 2,
	FOREIGN KEY (user_id)
		REFERENCES users(id)
		ON DELETE CASCADE,
	FOREIGN KEY (role_id)
		REFERENCES roles(role_id)
		ON DELETE CASCADE
);

INSERT INTO user_role VALUES (1, 1);



CREATE TABLE todo_list (
	id INT PRIMARY KEY AUTO_INCREMENT, 
	title VARCHAR(255) NOT NULL,
	user_id INT NOT NULL,
	FOREIGN KEY (user_id)
		REFERENCES users(id)
		ON DELETE CASCADE
);

INSERT INTO todo_list
	(title, user_id)
VALUES
	('My Todos', 1),
	('My Work Todos', 1);



CREATE TABLE todo_item (
	id INT PRIMARY KEY AUTO_INCREMENT, 
	label VARCHAR(255) NOT NULL,
	completed BOOLEAN,
	due_date DATETIME,
	priority INT,
	todolist_id INT,
	FOREIGN KEY (todolist_id)
		REFERENCES todo_list(id)
		ON DELETE CASCADE
);

INSERT INTO todo_item
	(label, completed, todolist_id)
VALUES
	('note1', true, 1),
	('note2', true, 1),
	('note3', false, 1),
	('note4', false, 2),
	('note5', true, 2);

UPDATE todo_item SET priority = id WHERE priority is NULL;

DELIMITER // ;
CREATE PROCEDURE delete_completed(IN list_id INT)
BEGIN
	DELETE FROM todo_item
	WHERE todolist_id=list_id AND completed=true;
END //
DELIMITER ; //


CREATE TRIGGER  after_user_insert
	AFTER INSERT ON users FOR EACH ROW 
		INSERT INTO user_role (user_id , role_id) VALUES (NEW.id , 2);