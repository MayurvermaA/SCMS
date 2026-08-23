import mysql.connector
from mysql.connector import Error


def get_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Mayur@28",
            database="scms_db",
            port=3306
        )

        if connection.is_connected():
            print("MySQL Connected Successfully!")
            return connection

    except Error as e:
        print("MySQL Connection Error:", e)

    return None