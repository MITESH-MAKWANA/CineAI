import sqlite3

conn = sqlite3.connect('cineai.db')
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Tables found:", tables)

cursor.execute("SELECT id, username, email, age, gender, favorite_genres FROM users")
users = cursor.fetchall()
print(f"\nTotal users: {len(users)}")
for u in users:
    print(f"  ID={u[0]}, username={u[1]}, email={u[2]}, age={u[3]}, gender={u[4]}, genres={u[5]}")

cursor.execute("SELECT COUNT(*) FROM watchlist")
print(f"\nWatchlist rows: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM favorites")
print(f"Favorites rows: {cursor.fetchone()[0]}")

conn.close()
print("\nDone.")
