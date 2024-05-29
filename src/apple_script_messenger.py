"""
AppleScriptMessenger
"""

import logging
import subprocess


class AppleScriptMessenger:
    """AppleScriptMessenger"""

    def __init__(self) -> None:
        pass

    @staticmethod
    def _get_template():
        """Script template"""
        script = """
        on run {mymessage, myid}
            tell application "Messages"
                set targetService to 1st service whose service type is iMessage
                set targetBuddy to buddy myid of targetService
                send mymessage to targetBuddy
            end tell
        end run
        """
        return script

    async def send_message_via_applescript(self, recipient, message):
        """Send"""

        def strip_leading_dashes(s):
            """osascript can't have messages starting with -"""
            if s.startswith("-"):
                return strip_leading_dashes(s[1:])
            return s

        escaped_recipient = recipient.strip('"').strip()
        escaped_message = strip_leading_dashes(message.strip('"').strip())

        script = self._get_template()

        try:
            result = subprocess.run(
                ["osascript", "-e", script, escaped_message, escaped_recipient],
                check=True,
                text=True,
                capture_output=True,
            )
            logging.info(result.stdout)
        except subprocess.CalledProcessError as e:
            logging.info(f"An error occurred: {e.stderr}")

        return escaped_message


# Setup logging
logging.basicConfig(level=logging.INFO)
