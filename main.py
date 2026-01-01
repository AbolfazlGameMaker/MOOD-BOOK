import sys
import sqlite3
from datetime import datetime
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton,
    QLabel, QListWidget, QHBoxLayout
)
from PySide6.QtCore import Qt
from textblob import TextBlob
import matplotlib

# Fix matplotlib for Windows
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

# =========================
# Database setup
# =========================
conn = sqlite3.connect("moodbook.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT,
    emotion TEXT,
    date TEXT
)
""")
conn.commit()

# =========================
# Advanced sentiment analysis
# =========================
def analyze_emotion(text):
    text_lower = text.lower()

    # Keywords for emotions
    angry_words = ["angry", "mad", "furious", "hate", "annoyed", "pissed", "rage", "irritated"]
    sad_words = ["sad", "bad day", "depressed", "unhappy", "cry", "crying", "lonely", "miserable"]
    anxious_words = ["anxious", "stress", "stressed", "worried", "panic", "nervous", "afraid"]
    happy_words = ["happy", "great", "awesome", "good day", "love", "excited", "amazing", "fantastic"]

    # Check keywords first
    for w in angry_words:
        if w in text_lower:
            return "Angry 😡"
    for w in sad_words:
        if w in text_lower:
            return "Sad 😢"
    for w in anxious_words:
        if w in text_lower:
            return "Anxious 😟"
    for w in happy_words:
        if w in text_lower:
            return "Happy 😄"

    # Fallback to TextBlob
    polarity = TextBlob(text).sentiment.polarity
    if polarity > 0.2:
        return "Happy 🙂"
    elif polarity < -0.2:
        return "Sad 🙁"
    else:
        return "Neutral 😐"

# =========================
# Main GUI
# =========================
class MoodBook(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mood Book 🌟")
        self.setGeometry(300, 100, 650, 600)

        layout = QVBoxLayout()
        self.setLayout(layout)

        # TextEdit
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Type your note here...")
        layout.addWidget(self.text_edit)

        # Buttons
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Note")
        self.add_button.clicked.connect(self.add_note)
        button_layout.addWidget(self.add_button)

        self.plot_button = QPushButton("Show Sentiment Chart")
        self.plot_button.clicked.connect(self.plot_emotions)
        button_layout.addWidget(self.plot_button)
        layout.addLayout(button_layout)

        # Label for current sentiment
        self.emotion_label = QLabel("")
        self.emotion_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.emotion_label)

        # List of notes
        self.notes_list = QListWidget()
        layout.addWidget(self.notes_list)

        self.load_notes()

    # Add note
    def add_note(self):
        note_text = self.text_edit.toPlainText().strip()
        if not note_text:
            self.emotion_label.setText("Please enter some text!")
            return

        emotion = analyze_emotion(note_text)
        date = datetime.now().strftime("%Y-%m-%d %H:%M")
        cursor.execute(
            "INSERT INTO notes (text, emotion, date) VALUES (?, ?, ?)",
            (note_text, emotion, date)
        )
        conn.commit()

        self.notes_list.addItem(f"{date} | {note_text} -> {emotion}")
        self.emotion_label.setText(f"Sentiment: {emotion}")
        self.text_edit.clear()

    # Load notes
    def load_notes(self):
        cursor.execute("SELECT text, emotion, date FROM notes ORDER BY id")
        rows = cursor.fetchall()
        for text, emotion, date in rows:
            self.notes_list.addItem(f"{date} | {text} -> {emotion}")

    # Plot sentiment chart
    def plot_emotions(self):
        cursor.execute("SELECT emotion, date FROM notes ORDER BY id")
        rows = cursor.fetchall()
        if not rows:
            self.emotion_label.setText("No notes for chart!")
            return

        dates = []
        values = []
        for emo, date in rows:
            dates.append(date)
            if "Happy" in emo:
                values.append(1)
            elif "Sad" in emo:
                values.append(-1)
            elif "Angry" in emo:
                values.append(-2)
            elif "Anxious" in emo:
                values.append(-0.5)
            else:
                values.append(0)

        plt.figure(figsize=(9, 4))
        plt.plot(dates, values, marker="o", color="#007ACC")
        plt.xticks(rotation=45, ha="right")
        plt.yticks([-2, -1, -0.5, 0, 1], ["Angry 😡","Sad 😢","Anxious 😟","Neutral 😐","Happy 😄"])
        plt.title("Sentiment Trend Over Time")
        plt.tight_layout()
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.show()

# =========================
# Run app
# =========================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MoodBook()
    window.show()
    sys.exit(app.exec())
