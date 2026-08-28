import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    try:
        connection = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT", "5432")),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )

        print("PostgreSQL Connected Successfully!")
        return connection

    except Exception as e:
        print("PostgreSQL Connection Error:", e)
        return None