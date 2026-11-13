
import mysql.connector
from dotenv import load_dotenv
import os

# Load database credentials
load_dotenv()

# Connect to MySQL database
def get_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            port=int(os.getenv("DB_PORT", 3306))
        )

        return connection

    except mysql.connector.Error as error:
        print("Database connection error:", error)
        return None


# Test database connection
if __name__ == "__main__":
    connection = get_connection()

    if connection:
        print("MySQL Database Connected Successfully!")
        connection.close()
    else:
        print("Database Connection Failed!")
