import sqlite3

db = sqlite3.connect("database.db")

cursor = db.cursor()

cursor.execute('PRAGMA table_info("order")')
columns = [row[1] for row in cursor.fetchall()]

print("Existing columns:")
print(columns)

if "completed_date" not in columns:
    cursor.execute(
        'ALTER TABLE "order" ADD COLUMN completed_date DATE'
    )
    db.commit()
    print("completed_date added successfully")
else:
    print("completed_date already exists")

db.close()
print("DONE")