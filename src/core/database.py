# import json, os
# from src.utils.config import DB_FILE

# def _load():
#     if not os.path.exists(DB_FILE):
#         return {}
#     with open(DB_FILE, "r") as f:
#         return json.load(f)

# def _save(data):
#     with open(DB_FILE, "w") as f:
#         json.dump(data, f, indent=2)

# def add_user(email, password_hash):
#     db = _load()
#     if email in db:
#         return False
#     db[email] = {"password": password_hash}
#     _save(db)
#     return True

# def get_user(email):
#     db = _load()
#     return db.get(email)
# placeholder for database operations