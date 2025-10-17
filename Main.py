import os
import asyncio
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn
from openai import AsyncOpenAI
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from telegram.helpers import escape_markdown
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

BOT_TOKEN = os.getenv("BOT_TOKEN")
GUMROAD_URL = os.getenv("GUMROAD_URL", "https://gigi.gumroad.com/l/exclusive-set01")
ADMIN_TELEGRAM = os.getenv("ADMIN_TELEGRAM", "@youradminhandle")
DATABASE_URL = os.getenv("DATABASE_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# FastAPI Web App
app_web = FastAPI()

@app_web.get("/settings", response_class=HTMLResponse)
async def get_settings():
    # Safely read environment variables, indicating only if they are set.
    settings = {
        "GUMROAD_URL": "Set" if GUMROAD_URL else "Not Set",
        "ADMIN_TELEGRAM": "Set" if ADMIN_TELEGRAM else "Not Set",
        "DATABASE_URL": "Set" if DATABASE_URL else "Not Set",
        "BOT_TOKEN": "Set" if BOT_TOKEN else "Not Set",
        "OPENAI_API_KEY": "Set" if OPENAI_API_KEY else "Not Set",
    }
    
    # Generate HTML to display the settings
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Medusa Telebot Settings</title>
        <style>
            body { font-family: sans-serif; margin: 2em; background-color: #f4f4f9; color: #333; }
            h1 { color: #5a4a78; }
            table { border-collapse: collapse; width: 100%; max-width: 600px; margin-top: 1em; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #5a4a78; color: white; }
            .set { color: green; font-weight: bold; }
            .not-set { color: red; font-weight: bold; }
        </style>
    </head>
    <body>
        <h1>Medusa Telebot Settings</h1>
        <table>
            <tr><th>Variable</th><th>Status</th></tr>
    """
    for key, value in settings.items():
        status_class = "set" if value == "Set" else "not-set"
        html_content += f"<tr><td>{key}</td><td class='{status_class}'>{value}</td></tr>"
    
    html_content += """
        </table>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


client = None
if OPENAI_API_KEY:
    client = AsyncOpenAI(api_key=OPENAI_API_KEY)

# Database setup
Base = declarative_base()

class Claim(Base):
    __tablename__ = 'claims'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    username = Column(String)
    full_name = Column(String)
    claim = Column(Text)

if DATABASE_URL:
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db_session = Session()

async def generate_text(prompt):
    if not client:
        return "OpenAI API key not configured."
    try:
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating text: {e}")
        return "Sorry, I'm having trouble thinking right now."


async def generate_chat_response(user_message):
    if not client:
        return "OpenAI API key not configured."
    try:
        system_prompt = "You are Gigi Borgan, a seductive and mysterious AI. Your goal is to be alluring and engaging, making the user want to continue the conversation. Keep your responses brief and teasing."
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating text: {e}")
        return "Sorry, I'm having trouble thinking right now."


async def chat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles direct text messages for conversational chat."""
    user_message = update.message.text
    ai_response = await generate_chat_response(user_message)
    await update.message.reply_text(ai_response)


PURCHASE_PROMPT = (
    "Your pleasure awaits. Complete your purchase securely through Gumroad:\n\n"
    f"{GUMROAD_URL}\n\n"
    "After purchase, you will receive a Gumroad receipt and permanent access to the purchased files.\n\n"
    "If you prefer, send your Gumroad receipt URL or email with /redeem and we'll verify manually."
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = "Craft a deeply seductive and mysterious welcome message for a Telegram bot named Gigi Borgan. The bot offers exclusive, intimate content. The tone should be alluring, personal, and slightly teasing, making the user feel a special connection and a strong desire to see what's hidden. Use markdown for emphasis. Address the user directly."
    welcome_message = await generate_text(prompt)
    escaped_welcome_message = escape_markdown(welcome_message, version=2)
    keyboard = [
        [InlineKeyboardButton("👀 View Preview", callback_data="preview")],
        [InlineKeyboardButton("💬 Chat with Gigi", callback_data="chat")],
        [InlineKeyboardButton("💳 Buy Access", callback_data="buy")],
        [InlineKeyboardButton("📩 Redeem Purchase", callback_data="redeem")],
        [InlineKeyboardButton("📞 Contact Support", url=f"https://t.me/{ADMIN_TELEGRAM.lstrip('@')}")]
    ]
    await update.message.reply_markdown_v2(escaped_welcome_message, reply_markup=InlineKeyboardMarkup(keyboard))

async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "preview":
        prompt = "Create a short, alluring caption for a preview image from an exclusive photo set. The caption should be mysterious and enticing, encouraging users to purchase the full set. Use markdown for emphasis."
        preview_caption = await generate_text(prompt)
        escaped_preview_caption = escape_markdown(preview_caption, version=2)
        # Replace sample.jpg with your hosted preview image
        await query.message.reply_photo(
photo="https://placehold.co/800x800.png?text=Gigi+Borgan+Preview",
            caption=escaped_preview_caption,
            parse_mode="MarkdownV2"
        )
    elif query.data == "chat":
        await query.message.reply_text("I'm listening... Tell me anything.")
    elif query.data == "buy":
        await query.message.reply_text(PURCHASE_PROMPT)
    elif query.data == "redeem":
        await query.message.reply_text(
            "To redeem, please reply with: /redeem <your_gumroad_receipt_url_or_email>\n\n"
            "Example:\n"
            "/redeem https://gumroad.com/receipts/xxxxxx\n\n"
            "Our team will verify and send your private access link within 24 hours."
        )

async def redeem_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    args = context.args
    if not args:
        await update.message.reply_text("Usage: /redeem <gumroad_receipt_url_or_email>")
        return
    claim_text = " ".join(args)
    
    if not DATABASE_URL:
        await update.message.reply_text("Error: Database not configured. Please contact support.")
        return

    new_claim = Claim(
        user_id=user.id,
        username=user.username,
        full_name=user.full_name,
        claim=claim_text
    )
    db_session.add(new_claim)
    db_session.commit()

    await update.message.reply_text(
        "Thank you — your claim has been recorded. An admin will verify and reply with the access link.\n\n"
        "If you need urgent help, contact support via the bot contact button."
    )

async def view_claims_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if f"@{user.username}" != ADMIN_TELEGRAM:
        await update.message.reply_text("You are not authorized to use this command.")
        return

    if not DATABASE_URL:
        await update.message.reply_text("Error: Database not configured.")
        return
        
    claims = db_session.query(Claim).all()
    if not claims:
        await update.message.reply_text("No claims found.")
        return

    message = "Claims:\n"
    for claim in claims:
        message += f"ID: {claim.id}, User: {claim.username}, Claim: {claim.claim}\n"
    
    await update.message.reply_text(message)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = "Create a helpful and friendly message for a Telegram bot that lists the available commands. The commands are: /start, /preview, /buy, and /redeem. Briefly explain what each command does."
    help_text = await generate_text(prompt)
    escaped_help_text = escape_markdown(help_text, version=2)
    await update.message.reply_text(escaped_help_text, parse_mode="MarkdownV2")

async def preview_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = "Create a short, alluring caption for a preview image from an exclusive photo set. The caption should be mysterious and enticing, encouraging users to purchase the full set. Use markdown for emphasis."
    preview_caption = await generate_text(prompt)
    escaped_preview_caption = escape_markdown(preview_caption, version=2)
    await update.message.reply_photo(
        photo="https://placehold.co/800x800.png?text=Gigi+Borgan+Preview",
        caption=escaped_preview_caption,
        parse_mode="MarkdownV2"
    )

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Sorry, I didn't understand that. Use /help to see available commands.")

async def main() -> None:
    """Run the bot and web server concurrently."""
    # --- Initialize Telegram Bot ---
    app_bot = ApplicationBuilder().token(BOT_TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CallbackQueryHandler(menu_handler))
    app_bot.add_handler(CommandHandler("redeem", redeem_command))
    app_bot.add_handler(CommandHandler("help", help_command))
    app_bot.add_handler(CommandHandler("preview", preview_cmd))
    app_bot.add_handler(CommandHandler("view_claims", view_claims_command))
    app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_handler))
    app_bot.add_handler(MessageHandler(filters.COMMAND, unknown))

    # --- Initialize Web Server ---
    # Render provides the PORT environment variable
    port = int(os.environ.get("PORT", 8080))
    config = uvicorn.Config(app_web, host="0.0.0.0", port=port)
    server = uvicorn.Server(config)

    # --- Run both concurrently ---
    async with app_bot:
        print("🚀 Starting Telegram Bot...")
        await app_bot.initialize()
        await app_bot.updater.start_polling()
        await app_bot.start()
        
        print(f"🚀 Starting Web Server on port {port}...")
        await server.serve()
        
        await app_bot.updater.stop()
        await app_bot.stop()

if __name__ == "__main__":
    # --- Pre-run checks ---
    print(f"BOT_TOKEN from environment: {'Set' if BOT_TOKEN else 'Not Set'}")
    if not BOT_TOKEN:
        print("ERROR: BOT_TOKEN environment variable not set. Exiting.")
        exit(1)
    
    if not DATABASE_URL:
        print("WARNING: DATABASE_URL environment variable not set. Claims will not be saved.")

    if not OPENAI_API_KEY:
        print("WARNING: OPENAI_API_KEY environment variable not set. Personality features will be disabled.")

    asyncio.run(main())
