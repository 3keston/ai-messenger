import os
import sys
import time
import sqlite3
import unittest
import tempfile
from pathlib import Path

# Add the src directory to the sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from db_manager import DatabaseManager  # type: ignore


class TestDatabaseManager(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory
        self.test_dir = tempfile.TemporaryDirectory()

        # Paths for the database and wal files
        self.db_path = os.path.join(self.test_dir.name, "chat.db")
        self.wal_path = os.path.join(self.test_dir.name, "chat.db-wal")

        # Create the database file
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.close()

        # Create the wal file by writing to the database
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("CREATE TABLE handle (id INTEGER PRIMARY KEY, name TEXT);")
            conn.execute(
                "CREATE TABLE message (id INTEGER PRIMARY KEY, handle_id INTEGER, text TEXT, attributedBody BLOB, date INTEGER, is_from_me INTEGER, FOREIGN KEY(handle_id) REFERENCES handle(id));"
            )
            conn.commit()

        # Ensure the wal file exists
        assert os.path.exists(self.wal_path)

    def tearDown(self):
        # Cleanup the temporary directory
        self.test_dir.cleanup()

    def test_database_manager_initialization(self):
        # Test the initialization of DatabaseManager
        db_manager = DatabaseManager(self.test_dir.name)
        self.assertEqual(db_manager._db_path, self.db_path)
        self.assertEqual(db_manager._wal_path, self.wal_path)
        self.assertGreater(db_manager._last_mod_times["db"], 0)
        self.assertGreater(db_manager._last_mod_times["wal"], 0)

    def test_insert_and_retrieve_data(self):
        # Insert data into the database
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("INSERT INTO handle (name) VALUES (?);", ("test_handle",))
            handle_id = conn.execute(
                "SELECT id FROM handle WHERE name = ?;", ("test_handle",)
            ).fetchone()[0]
            conn.execute(
                "INSERT INTO message (handle_id, text, attributedBody, date, is_from_me) VALUES (?, ?, ?, ?, ?);",
                (
                    handle_id,
                    "test_message",
                    b"\x04\x0bstreamtyped\x81\xe8\x03\x84\x01@\x84\x84\x84\x08NSString\x01\x84\x84\x08NSObject\x00\x85\x84\x01+\x0cstring value\x86",
                    int(time.time() * 1000000000),
                    1,
                ),
            )
            conn.commit()

        # Verify the data was inserted correctly
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT handle.name, message.text, message.attributedBody, message.date, message.is_from_me FROM message JOIN handle ON message.handle_id = handle.id;"
            )
            row = cursor.fetchone()
            self.assertIsNotNone(row)
            self.assertEqual(row[0], "test_handle")
            self.assertEqual(row[1], "test_message")
            self.assertEqual(
                row[2],
                b"\x04\x0bstreamtyped\x81\xe8\x03\x84\x01@\x84\x84\x84\x08NSString\x01\x84\x84\x08NSObject\x00\x85\x84\x01+\x0cstring value\x86",
            )
            self.assertGreater(row[3], 0)
            self.assertEqual(row[4], 1)


class TestDatabaseManagerAsync(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.test_dir.name, "chat.db")
        self.wal_path = os.path.join(self.test_dir.name, "chat.db-wal")

        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.close()

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("CREATE TABLE handle (id INTEGER PRIMARY KEY, name TEXT);")
            conn.execute(
                "CREATE TABLE message (id INTEGER PRIMARY KEY, handle_id INTEGER, text TEXT, attributedBody BLOB, date INTEGER, is_from_me INTEGER, FOREIGN KEY(handle_id) REFERENCES handle(id));"
            )
            conn.commit()

        assert os.path.exists(self.wal_path)

    async def asyncTearDown(self):
        self.test_dir.cleanup()

    async def test_get_messages_in_last_seconds(self):
        def time_ns_since_2001():
            epoch_2001 = 978307200  # Seconds between 1970-01-01 and 2001-01-01
            current_time_ns = int(time.time() * 1000000000)
            time_since_2001_ns = current_time_ns - (epoch_2001 * 1000000000)
            return time_since_2001_ns

        db_manager = DatabaseManager(self.test_dir.name)

        current_time_ns = time_ns_since_2001()
        past_time_ns = current_time_ns - (10 * 1000000000)
        outside_time_ns = current_time_ns - (100 * 1000000000)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("INSERT INTO handle (name) VALUES (?);", ("test_handle",))
            handle_id = conn.execute(
                "SELECT id FROM handle WHERE name = ?;", ("test_handle",)
            ).fetchone()[0]
            conn.execute(
                "INSERT INTO message (handle_id, text, attributedBody, date, is_from_me) VALUES (?, ?, ?, ?, ?);",
                (
                    handle_id,
                    "recent_message",
                    b"\x04\x0bstreamtyped\x81\xe8\x03\x84\x01@\x84\x84\x84\x08NSString\x01\x84\x84\x08NSObject\x00\x85\x84\x01+\x0cstring value\x86",
                    current_time_ns,
                    1,
                ),
            )
            conn.execute(
                "INSERT INTO message (handle_id, text, attributedBody, date, is_from_me) VALUES (?, ?, ?, ?, ?);",
                (
                    handle_id,
                    "past_message",
                    b"\x04\x0bstreamtyped\x81\xe8\x03\x84\x01@\x84\x84\x84\x08NSString\x01\x84\x84\x08NSObject\x00\x85\x84\x01+\x0cstring value\x86",
                    past_time_ns,
                    1,
                ),
            )
            conn.execute(
                "INSERT INTO message (handle_id, text, attributedBody, date, is_from_me) VALUES (?, ?, ?, ?, ?);",
                (
                    handle_id,
                    "outside_message",
                    b"\x04\x0bstreamtyped\x81\xe8\x03\x84\x01@\x84\x84\x84\x08NSString\x01\x84\x84\x08NSObject\x00\x85\x84\x01+\x0cstring value\x86",
                    outside_time_ns,
                    1,
                ),
            )
            conn.commit()

        messages = await db_manager.get_messages_in_last_seconds(20)

        # Print the messages for debugging
        print(f"Retrieved messages: {messages}")

        self.assertEqual(len(messages), 2)
        self.assertTrue(any(msg["text"] == "recent_message" for msg in messages))
        self.assertTrue(any(msg["text"] == "past_message" for msg in messages))
        self.assertFalse(any(msg["text"] == "outside_message" for msg in messages))


if __name__ == "__main__":
    unittest.main()
