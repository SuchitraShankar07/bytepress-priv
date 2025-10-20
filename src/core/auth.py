from src.utils.security import hash_password, verify_password
from src.core.database import add_user, get_user

def register_user(email: str, password: str, name: str = None) -> dict:
    """Register a new user with email, password, and optional name
    Returns: {"success": bool, "error": str, "error_type": str}
    """
    hashed = hash_password(password)
    return add_user(email, hashed, name)

def authenticate_user(email: str, password: str) -> dict:
    """Authenticate user and return user data if successful"""
    user = get_user(email)
    if user and verify_password(password, user["password"]):
        # Return user data without password
        user_data = user.copy()
        del user_data["password"]
        return user_data
    return None

def user_exists(email: str) -> bool:
    """Check if user exists"""
    return get_user(email) is not None
