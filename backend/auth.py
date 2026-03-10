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


def update_user_profile(user_id, name, email, phone=None, location=None, bio=None, role=None):
    execute_query(
        """UPDATE users SET name = %s, email = %s, phone = %s, location = %s, bio = %s, role = %s
           WHERE id = %s""",
        (name, email, phone, location, bio, role, user_id),
    )
    return get_user_by_id(user_id)


def change_user_password(user_id, old_password, new_password):
    user = fetch_one("SELECT password_hash FROM users WHERE id = %s", (user_id,))
    if not user:
        return False, "User not found."
    if not verify_password(old_password, user["password_hash"]):
        return False, "Current password is incorrect."
    new_hash = hash_password(new_password)
    execute_query("UPDATE users SET password_hash = %s WHERE id = %s", (new_hash, user_id))
    return True, "Password updated successfully."
