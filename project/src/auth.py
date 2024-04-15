import mysql.connector
from passlib.hash import pbkdf2_sha256

def validate_credentials(username, password):
    # Connect to MySQL database
    db = mysql.connector.connect(
        host="localhost",
        user="username",
        password="password",
        database="your_database"
    )
    cursor = db.cursor()

    # Retrieve hashed password for the given username
    cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
    result = cursor.fetchone()

    if result:
        hashed_password = result[0]
        # Verify password
        if pbkdf2_sha256.verify(password, hashed_password):
            return True
    return False
