import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    try:
        database_url = os.getenv("DATABASE_URL")

        if not database_url:
            print("DATABASE_URL is missing")
            return None

        connection = psycopg2.connect(database_url)

        print("PostgreSQL Connected Successfully!")
        return connection

    except Exception as e:
        print("PostgreSQL Connection Error:", e)
        return None