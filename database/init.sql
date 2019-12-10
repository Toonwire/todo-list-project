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


CREATE TABLE todo_list (
	id INT PRIMARY KEY AUTO_INCREMENT, 
	title VARCHAR(255) NOT NULL
);

INSERT INTO todo_list
	(title)
VALUES
	('My Todos'),
	('My Work Todos');
	

CREATE TABLE todo_item (
	id INT PRIMARY KEY AUTO_INCREMENT, 
	label VARCHAR(255) NOT NULL,
	completed BOOLEAN,
	due_date DATETIME,
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

DELIMITER // ;
CREATE PROCEDURE delete_completed(IN list_id INT)
BEGIN
	DELETE FROM todo_item
	WHERE todolist_id=list_id AND completed=true;
END //
DELIMITER ; //