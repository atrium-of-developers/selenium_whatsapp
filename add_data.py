import sqlite3

def create_tables():
    """
    Creates the database schema with topics, subtopics, and content tables.
    """
    conn = sqlite3.connect("study_bot.db")
    cursor = conn.cursor()

    # Create tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subtopics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            FOREIGN KEY (topic_id) REFERENCES topics (id) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS content (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subtopic_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            FOREIGN KEY (subtopic_id) REFERENCES subtopics (id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()

def add_data(data):
    """
    Populates the database with topics, subtopics, and their content.
    Expects data in the format:
    {
        "Topic1": {
            "Subtopic1": ["Content1", "Content2"],
            "Subtopic2": ["ContentA", "ContentB"]
        },
        "Topic2": {
            "Subtopic3": ["ContentX", "ContentY"]
        }
    }
    """
    conn = sqlite3.connect("study_bot.db")
    cursor = conn.cursor()

    for topic, subtopics in data.items():
        # Insert topic
        cursor.execute("INSERT OR IGNORE INTO topics (name) VALUES (?)", (topic,))
        cursor.execute("SELECT id FROM topics WHERE name = ?", (topic,))
        topic_id = cursor.fetchone()[0]

        for subtopic, contents in subtopics.items():
            # Insert subtopic
            cursor.execute(
                "INSERT INTO subtopics (topic_id, name) VALUES (?, ?)",
                (topic_id, subtopic)
            )
            subtopic_id = cursor.lastrowid

            # Insert content
            for content in contents:
                cursor.execute(
                    "INSERT INTO content (subtopic_id, content) VALUES (?, ?)",
                    (subtopic_id, content)
                )

    conn.commit()
    conn.close()

if __name__ == "__main__":
    # Example data: replace this with your actual data source
    example_data = {
        "Python Basics": {
            "Variables": ["What is a variable?", "How to declare a variable"],
            "Control Flow": ["What are if-else statements?", "Loops in Python"]
        },
        "Web Development": {
            "HTML": ["What is HTML?", "Basic structure of HTML"],
            "CSS": ["What is CSS?", "Selectors and properties"]
        }
    }

    # Create tables
    create_tables()

  
    print("Data populated successfully!")
