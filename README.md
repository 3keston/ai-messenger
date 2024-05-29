
# AI Messenger for macOS

AI Messenger is a macOS application designed to read your `chat.db` table and send messages to the chat when prompted. It also supports sending messages to self-chats (chats with yourself). 

## Features
- Reads and interacts with your `chat.db` table.
- Sends messages to chats when called with `@a` (or any mention you configure).
- Configurable with user-specific details.

## Requirements
- macOS
- Full Disk Access enabled in Privacy & Security settings.
- [Ollama](https://ollama.com/) installed for model support.
- Python 3.12 (see requirements.txt)

## Installation and Setup

### Step 1: Clone the Repository
First, clone the repository to your local machine:
```bash
git clone https://github.com/yourusername/ai-messenger.git
cd ai-messenger
```

### Step 2: Set Up the Virtual Environment
Create a virtual environment and install the required packages:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 3: Configure the Application
Navigate to the `src/config` directory and open the configuration file. Set the model running on Ollama.
```json
{
  "model": "ollama_model_name"
}
```

### Step 4: Build the Application
Use the `pyinstaller` builder to create the `.app` file:
```bash
python build_app.py
```

### Step 5: Move the Application to the Applications Folder
Once you have the `.app` file, copy it to your Applications folder:
```bash
cp dist/AI_Messenger.app /Applications/
```

### Step 6: Enable Full Disk Access
Go to `System Preferences` > `Privacy & Security` > `Full Disk Access` and enable Full Disk Access for AI Messenger.

### Step 7: Install and Setup Ollama
1. Download and install Ollama from [here](https://ollama.com/).
2. Open a terminal and run the following command to pull the latest model:
```bash
git pull llama3
```

## Usage

### Running the Application
You can now run AI Messenger from your Applications folder. 

### Sending Messages
To send a message to a chat:
- Mention `@a` at the beginning or end of the chat for AIM to jump in.

## Troubleshooting
- Ensure Full Disk Access is enabled.
- Verify the configuration file has the correct details.
- Make sure Ollama is correctly installed and the latest model is pulled.

I've had an issue where the FDA flicks off even after flicking it on, so double check.

## Contributing
Feel free to fork the repository and submit pull requests. For major changes, please open an issue first to discuss what you would like to change.

## License
This project is licensed under the GNU General Public License (GPL). See the `LICENSE` file for details.

By following these steps, you should be able to successfully install and use AI Messenger on your macOS device. If you encounter any issues, refer to the troubleshooting section or open an issue in the repository.
