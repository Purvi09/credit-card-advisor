import sqlite3
import json
import os
import sys

DB_PATH = "cards.db"
JSON_PATH = "./creditCards.json"

def initialize_database():
    try:
        if not os.path.exists(JSON_PATH):
            raise FileNotFoundError(f"JSON file not found at {JSON_PATH}")

        with open(JSON_PATH, "r", encoding="utf-8") as f:
            try:
                cards = json.load(f)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON format: {e}")

        if not isinstance(cards, list):
            raise TypeError("JSON data must be a list of card objects.")

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        cur.execute("""
        CREATE TABLE IF NOT EXISTS credit_cards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            issuer TEXT,
            annual_fee INTEGER,
            reward_type TEXT,
            eligibility TEXT,
            min_income INTEGER,
            perks TEXT,
            apply_link TEXT
        )
        """)

        for card in cards:
            try:
                cur.execute("""
                    INSERT INTO credit_cards (name, issuer, annual_fee, reward_type, eligibility, min_income, perks, apply_link)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    card.get("name"),
                    card.get("issuer"),
                    card.get("annual_fee"),
                    card.get("reward_type"),
                    card.get("eligibility"),
                    card.get("min_income"),
                    ", ".join(card.get("perks", [])),
                    card.get("apply_link"),
                ))
            except Exception as e:
                print(f"Skipping card due to error: {e}")

        conn.commit()
        print("Database initialized successfully!")

    except (FileNotFoundError, ValueError, TypeError) as e:
        print(e)
        sys.exit(1)
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)
    finally:
        try:
            if conn:
                conn.close()
        except NameError:
            pass

if __name__ == "__main__":
    initialize_database()