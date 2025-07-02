import psycopg2
from psycopg2.extras import RealDictCursor

# 数据库连接配置
DB_CONFIG = {
    'dbname': 'transport',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost',
    'port': '5432'
}

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

def execute_query(query, params=None):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute(query, params or ())
        if query.strip().upper().startswith('SELECT'):
            result = cur.fetchall()
        else:
            conn.commit()
            result = None
        return result
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close() 