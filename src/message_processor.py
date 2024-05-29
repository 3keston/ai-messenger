"""
Message processor
"""

import asyncio
import logging
from db_manager import DatabaseManager
from model_client import OllamaClient
from apple_script_messenger import AppleScriptMessenger


class MessageProcessor:
    """MessageProcessor"""

    def __init__(self, db_manager: DatabaseManager, client: OllamaClient, config):
        self._db_manager = db_manager
        self._as_utils = AppleScriptMessenger()
        self._client = client
        self._max_chat_items = config["max_chat_items"]
        self._max_interval = config["max_interval"]
        self._sleep_interval = config["sleep_interval"]
        self._mention = config["mention"]
        self._last_sent_message = None
        self._previous_sleep_interval = None

    async def run(self):
        """run"""
        while True:
            try:
                if await self._db_manager.has_db_changed():
                    await self._process_new_messages()
                    self._sleep_interval = 2
                else:
                    self._sleep_interval = min(
                        self._max_interval, self._sleep_interval + 5
                    )

                if self._sleep_interval != self._previous_sleep_interval:
                    logging.info(f"Sleeping for {self._sleep_interval} seconds...")
                    self._previous_sleep_interval = self._sleep_interval

                await asyncio.sleep(self._sleep_interval)
            except KeyboardInterrupt:
                logging.info("Program interrupted.")
                break
            except Exception as e:
                logging.error(f"An error occurred: {e}", exc_info=True)

    async def _process_new_messages(self):
        """process new messages"""
        last_k = await self._db_manager.get_messages_in_last_seconds(
            self._sleep_interval
        )
        drop_last_sent = [m for m in last_k if m["text"] != self._last_sent_message]
        if not drop_last_sent:
            return

        grouped_k = await self._group_by(drop_last_sent, "handle_id")

        for handle_id, _ in grouped_k.items():
            await self._process_messages_by_handle_id(handle_id)

    async def _process_messages_by_handle_id(self, handle_id):
        """process each "chat" determined by handle_id"""
        recent_messages = await self._db_manager.get_latest_messages_for_chat(
            self._max_chat_items, handle_id
        )
        if recent_messages and recent_messages[0]:
            await self._check_and_send_messages(handle_id, recent_messages)

    async def _check_and_send_messages(self, handle_id, recent_messages):
        """check and send messages"""
        most_recent_msg = recent_messages[0]["text"]
        agent_directed = self._is_agent_directed(most_recent_msg)

        if agent_directed:
            sent_message = await self._as_utils.send_message_via_applescript(
                handle_id, await self._client.get_msg(recent_messages)
            )
            if sent_message:
                self._last_sent_message = sent_message

    def _is_agent_directed(self, text):
        """Check if text starts with or ends with the mention"""
        return text and (text.startswith(self._mention) or text.endswith(self._mention))

    async def _group_by(self, data, key):
        """group_by"""
        grouped_data = {}
        for entry in data:
            handle_id = entry[key]
            if handle_id in grouped_data:
                grouped_data[handle_id].append(entry)
            else:
                grouped_data[handle_id] = [entry]
        return grouped_data


# Setup logging
logging.basicConfig(level=logging.INFO)
