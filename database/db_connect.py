import pymysql.cursors
import os


def get_connection():
	
	connection = pymysql.connect(
		host=os.environ.get("HOST"),
		user=os.environ.get("USER"),
		password=os.environ.get("PASSWORD"),
		db=os.environ.get("DATABASE")
	)

	return connection


def execute_database_relations():

    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS finance (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            price DECIMAL(10, 2) NOT NULL,
            comment VARCHAR(255) NOT NULL,
            category_id INT NOT NULL,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );'''
    )

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS category (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL
        );'''
    )

    conn.commit()
    cursor.close()


def create_db():

	conn = get_connection()
	execute_database_relations(conn)
	conn.close()
