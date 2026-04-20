import mysql.connector

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "mundial2026"
}

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)
