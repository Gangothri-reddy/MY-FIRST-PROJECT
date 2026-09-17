from database import get_connection

conn = get_connection()
cursor = conn.cursor()

cursor.execute(
    "INSERT INTO users (username, password) VALUES (?, ?)",
    ("admin", "admin123")
)

conn.commit()
conn.close()

print("Admin user created successfully!")