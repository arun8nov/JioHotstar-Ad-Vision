from database import get_connection

my_db = get_connection()
cursor = my_db.cursor()
cursor.execute("DROP DATABASE IF EXISTS jiohotstar_ads")
cursor.execute("CREATE DATABASE IF NOT EXISTS jiohotstar_ads")
cursor.execute("USE jiohotstar_ads")

cursor.execute("SHOW DATABASES")
databases = cursor.fetchall()

cursor.execute("USE jiohotstar_ads")

create_table_query = """
CREATE TABLE IF NOT EXISTS matches (
    match_id INT PRIMARY KEY,
    teams VARCHAR(255),
    location VARCHAR(255),
    match_type VARCHAR(100),
    winner VARCHAR(255),
    video_path VARCHAR(255) UNIQUE,
    match_timestamp DATETIME NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""

cursor.execute(create_table_query)
my_db.commit()

print("Database and table have been reset and created successfully.")

cursor.close()
my_db.close()

