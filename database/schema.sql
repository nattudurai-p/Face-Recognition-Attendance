-- Create table for user data (name and face encoding)
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    face_encoding BLOB NOT NULL
);

-- Create table for attendance (user ID, date, time)
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER NOT NULL,
    date TEXT NOT NULL,
    time TEXT NOT NULL,
    FOREIGN KEY (id) REFERENCES users(id)
);
