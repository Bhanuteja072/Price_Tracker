import mysql.connector
from mysql.connector import Error
def connect_to_db():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='bhanu@123',
            database='newr'
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error: {e}")
        return None
