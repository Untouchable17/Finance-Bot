from database.db_connect import get_connection
from datetime import datetime, timedelta


def get_categories_from_db():
	
	connect = get_connection()
	
	with connect.cursor() as cursor:
		result = cursor.execute("SELECT * FROM `category`")
		row = cursor.fetchall()
		return row


def get_category_id(category_name):
	
	connection = get_connection()
	try:
		with connection.cursor() as cursor:
			sql = "SELECT `id` FROM `category` WHERE `name`=%s"
			cursor.execute(sql, (category_name,))
			result = cursor.fetchone()
			if result:
				return result[0]
			else:
				return None
	finally:
		connection.close()


def save_finance_record(price, comment, category_name):
	
	category_id = get_category_id(category_name)

	if not category_id:
		return f"Категория {category_name} не найдена в базе данных."
	
	connection = get_connection()
	try:
		with connection.cursor() as cursor:
			sql = "INSERT INTO `finance` (`amount`, `comment`, `category_id`) VALUES (%s, %s, %s)"
			cursor.execute(sql, (price, comment, category_id))
			connection.commit()
	finally:
		connection.close()


def get_last_record_from_db():
	
	connection = get_connection()
	try:
		with connection.cursor() as cursor:
			sql = "SELECT * FROM `finance` ORDER BY `id` DESC LIMIT 1"
			cursor.execute(sql)
			last_record = cursor.fetchone()

			return last_record

	except Exception as ex:
		return(f"Record not found: {ex}")

	finally:
		connection.close()
    

def delete_last_record_from_db():

	connection = get_connection()
	try:
		with connection.cursor() as cursor:
			select_sql = "SELECT `id` FROM `finance` ORDER BY `id` DESC LIMIT 1"
			cursor.execute(select_sql)
			result = cursor.fetchone()

			if not result:
				return False

			record_id = result[0]

			delete_sql = "DELETE FROM `finance` WHERE `id`=%s"
			cursor.execute(delete_sql, (record_id,))
			connection.commit()

			return True

	except Exception as ex:
		return(f"Error deleting record: {ex}")

	finally:
		connection.close()


def delete_records_for_category(category_name):

	connection = get_connection()

	try:
		cursor = connection.cursor()
		query = """
			DELETE f FROM finance f
			JOIN category c ON f.category_id = c.id
			WHERE c.name = %s
		"""
		cursor.execute(query, (category_name,))
		if cursor.rowcount == 0:
			return "Категория уже пустая или не создана"
		connection.commit()

	finally:
		connection.close()



def get_statistics_from_db():

	connection = get_connection()
	try:
		with connection.cursor() as cursor:
			query = """
				SELECT c.name, COUNT(f.amount), SUM(f.amount) 
				FROM finance f
				INNER JOIN category c ON f.category_id = c.id
				GROUP BY c.name
			"""
			cursor.execute(query)
			results = cursor.fetchall()

			print(f"DB_EXECUTOR:\n {results}")
			return results

	finally:
		connection.close()


def get_records_by_category_from_db(category_name):

	connection = get_connection()
	try:
		with connection.cursor() as cursor:
			query = """
				SELECT 
					`finance`.`id`, 
					`finance`.`amount`, 
					`finance`.`comment`, 
					`finance`.`date_created` 
				FROM `finance` 
				INNER JOIN `category` 
				ON `finance`.`category_id` = `category`.`id` 
				WHERE `category`.`name` = %s
			"""
			cursor.execute(query, (category_name,))
			records = cursor.fetchall()
			return records
	finally:
		connection.close()


def get_records_from_database(category_name: str, limit: int, offset: int):
	
	connection = get_connection()

	try:
		with connection.cursor() as cursor:
			query = f"""
				SELECT * FROM `finance` 
        		INNER JOIN `category` 
        			ON `finance`.`category_id` = `category`.`id` 
    			WHERE `category`.`name` = %s LIMIT {limit} OFFSET {offset}
			"""
			cursor.execute(query, (category_name,))
			records = cursor.fetchall()
			return records
	finally:
		connection.close()



def get_export_db_data():
	
	connection = get_connection()
	try:
		with connection.cursor() as cursor:
			query = """
			    SELECT 
			    	finance.id, 
			    	finance.amount, 
			    	category.name, 
			    	finance.comment, 
			    	finance.date_created
			    FROM finance
			    JOIN category ON finance.category_id = category.id
			"""
			cursor.execute(query)
			records = cursor.fetchall()
			return records
	finally:
		connection.close()