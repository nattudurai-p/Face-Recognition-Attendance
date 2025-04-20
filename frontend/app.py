from flask import Flask, request, jsonify
import face_recognition
import cv2
import numpy as np
import sqlite3
from datetime import datetime

app = Flask(__name__)

# SQLite Database Setup
conn = sqlite3.connect('../database/attendance.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY, name TEXT, face_encoding BLOB)""")
cursor.execute("""CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER, date TEXT, time TEXT)""")

@app.route('/register', methods=['POST'])
def register():
    name = request.form['name']
    image = request.files['image'].read()
    nparr = np.frombuffer(image, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    encodings = face_recognition.face_encodings(rgb_img)

    if not encodings:
        return jsonify({"error": "No face detected"}), 400

    encoding = encodings[0]
    cursor.execute("INSERT INTO users (name, face_encoding) VALUES (?, ?)", (name, encoding.tobytes()))
    conn.commit()
    return jsonify({"success": True, "name": name})

@app.route('/recognize', methods=['POST'])
def recognize():
    image = request.files['image'].read()
    nparr = np.frombuffer(image, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    encodings = face_recognition.face_encodings(rgb_img)

    if not encodings:
        return jsonify({"error": "No face detected"}), 400

    unknown_encoding = encodings[0]
    cursor.execute("SELECT id, name, face_encoding FROM users")
    users = cursor.fetchall()

    for user in users:
        stored_encoding = np.frombuffer(user[2], dtype=np.float64)
        match = face_recognition.compare_faces([stored_encoding], unknown_encoding)[0]
        if match:
            now = datetime.now()
            cursor.execute("INSERT INTO attendance (id, date, time) VALUES (?, ?, ?)",
                           (user[0], now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S")))
            conn.commit()
            return jsonify({"success": True, "name": user[1]})

    return jsonify({"error": "Unknown face"}), 404

if __name__ == '__main__':
    app.run(debug=True)
