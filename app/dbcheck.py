from db import get_connection


def count_rows(table_name):
    """특정 테이블의 행(row) 개수를 반환"""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            result = cursor.fetchone()
        return result[0]
    finally:
        conn.close()


if __name__ == "__main__":
    tables = ["restaurant_name", "restaurant_reviews"]
    for table in tables:
        count = count_rows(table)
        print(f"`{table}` 테이블의 총 행 개수: {count}")
