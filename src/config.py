""" Config """

config = {
    "model": "llama3",  # Ollama model choice, e.g. ollama pull $MODEL
    "db_path": "~/Library/Messages",  # location of your Messages chat.db
    "mention": "@a",  # how you want to call out to the agent
    "max_chat_items": 10,  # how many items to load into the context window
    "max_interval": 30,  # max polling interval - will affect how snappy agent feels
    "sleep_interval": 2,  # the smaller sleep interval - will affect how snappy agent feels
}
