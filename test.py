from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MySQL Configuration
config = {
    'user': 'mariadb',
    'password': '1234',
    'host': 'svc.sel5.cloudtype.app',
    'port': 31200,
    'database': 'mariadb'
}

def init_db():
    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()

        # Check if 'group_code' column exists
        cursor.execute("SHOW COLUMNS FROM plans LIKE 'group_code'")
        result = cursor.fetchone()

        if not result:
            # If 'group_code' column does not exist, add it
            cursor.execute("""
                ALTER TABLE plans
                ADD COLUMN group_code CHAR(4) NOT NULL DEFAULT '0000' AFTER notes
            """)
            connection.commit()
            print("Added 'group_code' column to 'plans' table.")
        else:
            print("'group_code' column already exists in 'plans' table.")

        cursor.close()
        connection.close()

    except Error as e:
        print("Error while connecting to MySQL and adding 'group_code' column:", e)

if __name__ == '__main__':
    init_db()
