import sqlite3

Users = []  # Global liste for å holde på brukerne


def get_all_users(db_path, session):
    global Users
    if not Users:  # Hvis listen er tom, hent fra databasen
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT username FROM users")
            Users = cursor.fetchall()
            conn.close()
        except Exception as e:
            print("Error retrieving users:", e)
    return Users
