import os
import psycopg2
import psycopg2.extras


def get_connection():
    return psycopg2.connect(os.environ["DATABASE_URL"])


def execute_query(query, params=None):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(query, params)
        conn.commit()
        return cur
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def execute_returning(query, params=None):
    conn = get_connection()
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(query, params)
        result = cur.fetchone()
        conn.commit()
        return result
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def fetch_one(query, params=None):
    conn = get_connection()
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(query, params)
        return cur.fetchone()
    finally:
        conn.close()


def fetch_all(query, params=None):
    conn = get_connection()
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(query, params)
        return cur.fetchall()
    finally:
        conn.close()
