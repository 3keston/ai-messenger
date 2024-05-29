"""
Model
"""

import logging
from ollama import AsyncClient  # type: ignore


class OllamaClient:
    """OllamaClient"""

    def __init__(self, config):
        self._model = config["model"]
        self._mention = config["mention"]
        self._client = AsyncClient()
        self._system_msg = f"""You are AI Messenger (get it AIM, ha!), an assistant who responds to SMS messages.
        You don't do much now other than chat, but you will have many cool features someday!
        You respond in style and format perfect for SMS / iMessage.
        You aloof and cool, but concise and helpful.
        
        ## Bonus info:
        You are powered by a total private local LLM called {self._model}.
        """

    @staticmethod
    def _remove_substring(original_string, substring):
        return original_string.replace(substring, "")

    def _clean_text(self, text):
        """
        Clean up the text before sending it to the LLM
        """
        return text.removeprefix(self._mention).removesuffix(self._mention).strip()

    def _format_data(self, data):
        """
        the user / assistant paradigm isn't really setup for multi party chat
        because the incoming message is supposed to be a user message, we work backwards
        to create a user / assistant thread,
        regardless of who actually sent the previous messages
        not ideal, but the client is happy
        """
        formatted_data = []

        for i, entry in enumerate(data):
            role = "user" if i % 2 == 0 else "assistant"
            content = self._clean_text(entry["text"])
            formatted_entry = {"role": role, "content": content}
            formatted_data.append(formatted_entry)

        formatted_data.reverse()
        return formatted_data

    def _single_msg_format(self, data):
        """
        put everything together into a single message for response
        """
        bldr = []
        for d in data:
            c = self._clean_text(d["content"])
            if c and c not in bldr:
                bldr.append(c)
        chats = "\n".join(bldr).strip()
        return chats

    async def get_msg(self, msg):
        """get msg"""
        formatted = self._format_data(msg)
        msg_history = self._single_msg_format(formatted[:-1])
        formatted_msg = f"""## Conversation History:
        {msg_history}
        """
        messages = [
            {
                "role": "system",
                "content": self._system_msg + formatted_msg,
            },
            formatted[-1],
        ]
        logging.info(f"Messages:\n{messages}")
        response = await self._client.chat(
            model=self._model,
            messages=messages,
        )
        model_res = response["message"]["content"]
        logging.info(f"Agent: '{model_res}'")
        return model_res


# Setup logging
logging.basicConfig(level=logging.INFO)
