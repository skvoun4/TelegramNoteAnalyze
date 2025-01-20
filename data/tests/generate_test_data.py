import sqlite3

def test_add_note():
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE notes (id INTEGER PRIMARY KEY, content TEXT NOT NULL)")
    cursor.execute("INSERT INTO notes (content) VALUES (?)", ("Test note",))
    cursor.execute("SELECT content FROM notes WHERE id = 1")
    assert cursor.fetchone()[0] == "Test note"
    print("Тест добавления заметки пройден!")
