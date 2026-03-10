import bcrypt
from backend.db import execute_query, fetch_one


def hash_password(password):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def create_user(name, email, password, role="farmer"):
    password_hash = hash_password(password)
    execute_query(
        "INSERT INTO users (name, email, password_hash, role) VALUES (%s, %s, %s, %s)",
        (name, email, password_hash, role),
    )


def authenticate_user(email, password):
    user = fetch_one("SELECT * FROM users WHERE email = %s", (email,))
    if user and verify_password(password, user["password_hash"]):
        return dict(user)
    return None


def get_user_by_id(user_id):
    user = fetch_one("SELECT * FROM users WHERE id = %s", (user_id,))
    if user:
        return dict(user)
    return None
