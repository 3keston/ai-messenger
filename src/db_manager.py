"""
chat.db manager
"""

import os
import logging
from datetime import datetime

import aiosqlite


class DatabaseManager:
    """DatabaseManager"""

    def __init__(self, base_path):
        self._db_path = os.path.expanduser(os.path.join(base_path, "chat.db"))
        self._wal_path = os.path.expanduser(os.path.join(base_path, "chat.db-wal"))
        self._last_mod_times = {
            "db": os.path.getmtime(self._db_path),
            "wal": os.path.getmtime(self._wal_path),
        }

    async def has_db_changed(self):
        """has changed"""
        # Check the modification times of both the main DB and the WAL file
        current_db_mod_time = os.path.getmtime(self._db_path)
        current_wal_mod_time = os.path.getmtime(self._wal_path)
        db_changed = current_db_mod_time != self._last_mod_times["db"]
        wal_changed = current_wal_mod_time != self._last_mod_times["wal"]

        if db_changed or wal_changed:
            logging.info(f"Database change detected at {datetime.now()}")
            self._last_mod_times["db"] = current_db_mod_time
            self._last_mod_times["wal"] = current_wal_mod_time
            return True
        return False

    async def _execute_query(self, query, params=None, fetchall=False):
        """execute"""
        try:
            # Using aiosqlite to handle database operations asynchronously
            async with aiosqlite.connect(self._db_path) as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(query, params if params else ())
                    result = (
                        await cursor.fetchall() if fetchall else await cursor.fetchone()
                    )
                    return result
        except Exception as e:
            logging.info(f"An error occurred: {e}")
            return None

    async def _process_messages(self, messages):
        """process"""
        results = []
        if messages:
            for message in messages:
                handle_id, text, attributed_body, timestamp, is_from_me = message
                if text is None and attributed_body:
                    from typedstream import unarchive_from_data  # type: ignore

                    unarch = unarchive_from_data(attributed_body)
                    text = unarch.contents[0].value.value
                message_dict = {
                    "handle_id": handle_id,
                    "text": text,
                    "timestamp": timestamp,
                    "is_from_me": is_from_me,
                }
                results.append(message_dict)
        return results

    async def get_latest_messages_for_chat(self, k, handle_id):
        """get latest by id"""
        query = """
        SELECT handle.id, message.text, message.attributedBody,
            datetime(message.date/1000000000 + strftime("%s", "2001-01-01"),
            "unixepoch", "localtime") as timestamp, message.is_from_me
        FROM message
        JOIN handle ON message.handle_id = handle.ROWID
        WHERE handle.id = ?
        ORDER BY message.date DESC
        LIMIT ?;
        """
        # Fetch all results using the provided handle_id and limit
        latest_messages = await self._execute_query(
            query, (handle_id, k), fetchall=True
        )
        return await self._process_messages(latest_messages)

    async def get_messages_in_last_seconds(self, seconds):
        """Get messages from the last specified number of seconds."""
        # Calculate the current time in nanoseconds and the time threshold
        nanoseconds = seconds * 1000000000

        # Updated SQL query using correct time comparison
        query = """
        SELECT handle.id, message.text, message.attributedBody,
               datetime((message.date / 1000000000) + strftime('%s', '2001-01-01'),
                        'unixepoch', 'localtime') as timestamp, message.is_from_me
        FROM message
        JOIN handle ON message.handle_id = handle.ROWID
        WHERE message.date >= ((strftime("%s", 'now') - strftime("%s", '2001-01-01')) * 1000000000 - ?)
        ORDER BY message.date DESC;
        """

        # Fetch all results since we are limiting based on time in the query itself
        messages_in_last_seconds = await self._execute_query(
            query, (nanoseconds,), fetchall=True
        )

        # Process and return the messages
        processed_messages = await self._process_messages(messages_in_last_seconds)
        return processed_messages


# Setup logging
logging.basicConfig(level=logging.INFO)
