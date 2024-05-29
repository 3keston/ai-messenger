"""
Messages Agent
"""

import asyncio

from model_client import OllamaClient
from db_manager import DatabaseManager
from message_processor import MessageProcessor
from config import config


async def main():
    """main"""
    client = OllamaClient(config)
    db_manager = DatabaseManager(base_path=config["db_path"])
    processor = MessageProcessor(db_manager, client, config)
    await processor.run()


if __name__ == "__main__":
    asyncio.run(main())
