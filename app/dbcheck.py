import mysql.connector

def get_connection():
    """Adminer와 연결된 MySQL 데이터베이스 연결 함수"""
    return mysql.connector.connect(
        host="127.0.0.1",  # Adminer와 동일한 MySQL 호스트 (예: Docker 컨테이너 IP)
        port=3306,         # MySQL 포트 (기본값: 3306)
        user="root",       # Adminer에서 사용하는 사용자 이름
        password="1234",   # Adminer에서 사용하는 비밀번호
        database="crawling_db"  # Adminer에서 사용하는 데이터베이스 이름
    )

def count_rows(table_name):
    """특정 테이블의 행(row) 개수를 반환"""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            query = f"SELECT COUNT(*) FROM {table_name};"  # 행 개수 조회 쿼리
            cursor.execute(query)
            result = cursor.fetchone()
        return result[0]  # 행 개수 반환
    finally:
        conn.close()

if __name__ == "__main__":
    # 테이블 이름 지정
    tables = ["restaurant_name", "restaurant_reviews"]
    
    # 각 테이블의 row 개수 출력
    for table in tables:
        count = count_rows(table)
        print(f"`{table}` 테이블의 총 행 개수: {count}")