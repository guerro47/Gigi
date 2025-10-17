# Medusa Telebot

Medusa Telebot is a sophisticated, AI-powered Telegram bot designed for content creators. It provides an interactive and sensual chat experience, automates the sales and redemption process for exclusive content via Gumroad, and includes a simple web interface to monitor its configuration.

## Features

- **AI-Powered Chat:** Engages users with a seductive and mysterious AI personality.
- **Gumroad Integration:** Seamlessly guides users to a Gumroad purchase link.
- **Content Redemption:** Allows users to redeem their purchases by providing a receipt.
- **Admin Dashboard:** A protected command for administrators to view purchase claims.
- **Web Settings View:** A simple, secure web page to check the status of the bot's configuration.
- **Asynchronous:** Built with `asyncio` to run the Telegram bot and the web server concurrently.

## Technology Stack

- **Language:** Python 3.11+
- **Bot Framework:** `python-telegram-bot`
- **Web Framework:** `FastAPI` & `Uvicorn`
- **Database:** `SQLAlchemy` with a PostgreSQL backend.
- **AI:** `OpenAI` API for text generation.

## Setup and Configuration

Follow these steps to get your own instance of Medusa Telebot running.

### 1. Clone the Repository

```bash
git clone https://github.com/guerro47/Gigi.git medusa_telebot
cd medusa_telebot
```

### 2. Install Dependencies

Install the required Python libraries:

```bash
pip install -r requirements.txt
```

### 3. Set Environment Variables

This project uses environment variables for configuration. Create a `.env` file for local development or set these in your hosting provider's dashboard (e.g., Replit Secrets).

| Variable         | Description                                                                 |
| ---------------- | --------------------------------------------------------------------------- |
| `BOT_TOKEN`      | **Required.** Your Telegram Bot Token from BotFather.                         |
| `OPENAI_API_KEY` | **Required.** Your API key from OpenAI to enable the chat functionality.      |
| `GUMROAD_URL`    | The full URL to your Gumroad product page.                                  |
| `ADMIN_TELEGRAM` | Your Telegram username (e.g., `@yourname`) for accessing admin commands.      |
| `DATABASE_URL`   | The connection URL for your PostgreSQL database (e.g., `postgresql://...`). |

## Running the Project

### Locally

After setting your environment variables, you can run the bot directly:

```bash
python Main.py
```

The web view for settings will be available at `http://127.0.0.1:8080/settings`.

### On Replit

1.  **Import** the project from GitHub.
2.  Add all the required environment variables in the **Secrets** tab.
3.  Click the **Run** button. The web view will automatically appear in a new pane.

## Usage

### User Commands

- `/start`: Initializes the bot and shows the main menu.
- `/help`: Displays a help message.
- `/preview`: Shows a preview of the content.
- `/buy`: Provides the link to purchase the content.
- `/redeem <receipt>`: Allows a user to redeem their purchase.
- **Direct Chat:** Simply send any text message to start a conversation with the bot.

### Admin Commands

- `/view_claims`: View all the purchase claims submitted by users. You must be the configured admin to use this.
