import mysql.connector
from config import DB_CONFIG


def get_connection():
    """MySQL 데이터베이스 연결 반환 함수"""
    return mysql.connector.connect(**DB_CONFIG)


def fetch_all_data(query):
    """SQL 쿼리를 실행하고 결과를 반환하는 함수"""
    conn = get_connection()
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(query)
            return cursor.fetchall()
    finally:
        conn.close()
