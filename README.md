# Simple Onboard Bot

![Bot Logo](https://via.placeholder.com/150)

A Telegram bot designed to streamline the onboarding process for new community members. It handles user applications, manages approvals, and facilitates communication within the community.

## Features

-   **User Onboarding:** Guides new users through an application process with a series of questions.
-   **Admin Approval System:** Allows administrators to approve or reject user applications.
-   **Additional Application Flow:** Supports a secondary application process for specific purposes.
-   **Broadcast Messaging:** Enables administrators to send messages to all approved users.
-   **Dynamic Main Menu:** Provides a customizable main menu for approved users with different options (CN, EU/NA, Telegram, Discord, Admin).
-   **Database Integration:** Uses SQLite to store user information and application statuses.
-   **Logging:** Comprehensive logging of bot activities and errors.

## Getting Started

Follow these instructions to set up and run the Simple Onboard Bot on your local machine.

### Prerequisites

-   Python 3.8+
-   pip (Python package installer)
-   A Telegram Bot Token from BotFather
-   Your Telegram User ID and a Chat ID for logging (can be obtained from a bot like `@userinfobot`)

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/simple-onboard-bot.git
    cd simple-onboard-bot
    ```

2.  **Create a virtual environment (recommended):**

    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
    ```

3.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

### Environment Variables

Create a `.env` file in the root directory of the project based on `.env.example` and fill in your details:

```
TOKEN=YOUR_TELEGRAM_BOT_TOKEN
MY_TELEGRAM_ID=YOUR_TELEGRAM_USER_ID
LOG_CHAT_ID=YOUR_LOG_CHANNEL_CHAT_ID
ADDITIONAL_APPLICATION_LOG_CHAT_ID=YOUR_ADDITIONAL_APPLICATION_LOG_CHANNEL_CHAT_ID
```

-   `TOKEN`: The API token you received from BotFather.
-   `MY_TELEGRAM_ID`: Your personal Telegram User ID. This is used for admin commands.
-   `LOG_CHAT_ID`: The chat ID of the channel or group where general bot logs and new applications will be sent.
-   `ADDITIONAL_APPLICATION_LOG_CHAT_ID`: The chat ID of the channel or group where additional application logs will be sent.

### Running the Bot

```bash
python main.py
```

The bot will start polling for updates, and you should see a "Bot is running..." message in your console.

### Running with Docker

1.  **Build the Docker image:**

    ```bash
    docker build -t simple-onboard-bot .
    ```

2.  **Run the Docker container:**

    ```bash
    docker run --env-file .env simple-onboard-bot
    ```

    Ensure your `.env` file is correctly configured as described in the "Environment Variables" section.

## Usage

-   **Start the bot:** Send `/start` to your bot on Telegram.
-   **Admin Commands:**
    -   `/broadcast <message>`: Send a message to all approved users.
    -   `/force_update`: Force an update of the main menu keyboard for all users.
-   **Application Process:** Follow the prompts from the bot to complete the application.
-   **Main Menu:** Approved users will have access to a dynamic main menu with various options.

## Project Structure

```
.dockerignore
.env.example
.gitignore
config.py: Configuration settings for the bot.
constants.py: Defines conversation states and other constants.
conversations.py: Manages conversation flows and states.
database.py: Handles SQLite database operations for user management.
Dockerfile: Dockerfile for containerizing the application.
LICENSE: Project license information (CC0 1.0 Universal).
main.py: The main entry point for the bot application.
migrate_users.py: Script for migrating user data (if needed).
README.md: This README file.
requirements.txt: Python dependencies.
utils.py: Utility functions.
handlers/: Contains modules for handling different bot functionalities.
├── additional_application.py: Handles the additional application process.
├── admin.py: Contains admin-specific commands and callbacks (approval, broadcast).
├── application.py: Manages the main user application flow and main menu interactions.
└── buttons.py: Defines keyboard layouts for the bot.
```

## Contributing

Contributions are welcome! If you have suggestions for improvements or new features, please open an issue or submit a pull request.

## License

This project is licensed under the [CC0 1.0 Universal](LICENSE) License.
